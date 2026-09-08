from __future__ import annotations
import logging
from collections.abc import Callable
from typing import cast

from opensandbox import SandboxSync
from deepagents.backends.protocol import (
    ExecuteResponse,
    FileDownloadResponse,
    FileUploadResponse,
)
from deepagents.backends.sandbox import BaseSandbox

SyncPollingInterval = float | Callable[[float], float]
PollingStrategy = Callable[[float], float]

# 配置日志
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
logger.setLevel(logging.ERROR)

# 如果没有配置日志处理器，则添加一个
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class OpenSandboxBackend(BaseSandbox):
    """符合 SandboxBackendProtocol 协议的 OpenSandbox 实现。

       该实现继承了 BaseSandbox 的所有文件操作方法，
       并仅使用 OpenSandbox 的 API 实现了 execute()、download_files() 和 upload_files() 方法。
       """

    def __init__(
            self,
            *,
            sandbox: SandboxSync,
            timeout: int = 30 * 60,
            sync_polling_interval: SyncPollingInterval = 0.1,
    ) -> None:
        """创建一个包装已有 OpenSandbox 沙盒的后端实例。

        Args：
            sandbox：要包装的现有 OpenSandbox 沙盒实例。
            timeout：调用 `execute()` 且未显式指定 `timeout` 时使用的默认命令超时时间（秒）。
            sync_polling_interval：在同步执行路径上，轮询 OpenSandbox 命令完成状态的间隔时间（秒）；
                也可以是一个可调用对象，接收已执行的秒数并返回下一次轮询的延迟时间。
        """
        logger.info(f"正在初始化 OpenSandbox，沙盒 ID: {sandbox.id}")
        self._sandbox = sandbox
        # sandbox.kill()  # 手动关闭沙箱
        self._default_timeout = timeout

        # 处理轮询策略
        if callable(sync_polling_interval):
            polling_strategy = cast("PollingStrategy", sync_polling_interval)
        else:
            def polling_strategy(_elapsed: float) -> float:
                return sync_polling_interval

        self._sync_polling_interval = polling_strategy
        logger.debug(f"OpenSandbox 初始化完成，默认超时时间={timeout}秒")

    @property
    def id(self) -> str:
        """返回 OpenSandbox 沙盒的 ID。"""
        sandbox_id = self._sandbox.id
        logger.debug(f"获取沙盒 ID: {sandbox_id}")
        return sandbox_id

    def execute(
            self,
            command: str,
            *,
            timeout: int | None = None,
    ) -> ExecuteResponse:
        """在沙盒内部执行一条 Shell 命令。

        Args：
            command：要执行的 Shell 命令字符串。
            timeout：等待命令完成的最大时间（秒）。
                如果为 None，则使用后端默认的超时时间。
        """
        effective_timeout = timeout if timeout is not None else self._default_timeout
        logger.debug(f"准备执行命令：{command[:100]}...（超时时间={effective_timeout}秒）")
        return self._execute_command(command, timeout=effective_timeout)

    def _execute_command(
            self,
            command: str,
            *,
            timeout: int,
    ) -> ExecuteResponse:
        """使用 OpenSandbox 的 API 执行命令。"""
        try:
            logger.debug(f"通过 OpenSandbox API 执行命令：{command}")
            result = self._sandbox.commands.run(command)
            logger.debug(f"命令执行完成，退出码：{result.exit_code}")

            # 提取标准输出与标准错误
            stdout = ""
            stderr = ""

            if result.logs.stdout:
                stdout = "\n".join([log.text for log in result.logs.stdout])
                logger.debug(f"命令标准输出长度：{len(stdout)} 字符")

            if result.logs.stderr:
                stderr = "\n".join([log.text for log in result.logs.stderr])
                logger.debug(f"命令标准错误长度：{len(stderr)} 字符")

            # 合并输出
            output = stdout
            if stderr and stderr.strip():
                output += f"\n<stderr>{stderr.strip()}</stderr>"

            logger.info(f"命令执行成功，退出码：{result.exit_code or 0}")
            return ExecuteResponse(
                output=output,
                exit_code=result.exit_code or 0,
                truncated=False,
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"执行命令时发生错误：{error_msg}", exc_info=True)

            if "timeout" in error_msg.lower():
                logger.warning(f"命令在 {timeout} 秒后超时")
                return ExecuteResponse(
                    output=f"命令在 {timeout} 秒后超时",
                    exit_code=124,
                    truncated=False,
                )

            return ExecuteResponse(
                output=f"执行命令时出错：{error_msg}",
                exit_code=1,
                truncated=False,
            )

    def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        """从沙盒中下载文件。"""
        logger.info(f"开始下载 {len(paths)} 个文件：{paths}")
        responses: list[FileDownloadResponse] = []

        for i, path in enumerate(paths):
            logger.debug(f"正在处理第 {i + 1}/{len(paths)} 个文件：{path}")

            if not path.startswith("/"):
                logger.error(f"非法路径（必须是绝对路径）：{path}")
                responses.append(
                    FileDownloadResponse(path=path, content=None, error="invalid_path")
                )
                continue

            try:
                logger.debug(f"正在从沙盒读取文件：{path}")
                content = self._sandbox.files.read_file(path)
                content_bytes = content.encode("utf-8") if isinstance(content, str) else content

                logger.debug(f"文件读取成功，大小：{len(content_bytes)} 字节")
                responses.append(
                    FileDownloadResponse(
                        path=path,
                        content=content_bytes,
                        error=None,
                    )
                )

            except Exception as e:
                logger.error(f"读取文件 {path} 时出错：{str(e)}", exc_info=True)

                # 尝试检查文件是否存在
                try:
                    logger.debug(f"检查文件是否存在：{path}")
                    result = self._sandbox.commands.run(f"test -f '{path}' && echo 'exists'")

                    if not result.logs.stdout or "exists" not in result.logs.stdout[0].text:
                        logger.error(f"文件不存在：{path}")
                        responses.append(
                            FileDownloadResponse(
                                path=path,
                                content=None,
                                error="file_not_found",
                            )
                        )
                    else:
                        logger.error(f"文件存在但读取失败：{path}，错误：{str(e)}")
                        responses.append(
                            FileDownloadResponse(
                                path=path,
                                content=None,
                                error=f"read_error: {str(e)}",
                            )
                        )
                except Exception as check_error:
                    logger.error(f"检查文件是否存在时出错：{check_error}", exc_info=True)
                    responses.append(
                        FileDownloadResponse(
                            path=path,
                            content=None,
                            error=f"check_error: {str(check_error)}",
                        )
                    )

        success_count = sum(1 for r in responses if r.error is None)
        logger.info(f"文件下载完成，成功 {success_count}/{len(paths)} 个")
        return responses

    def upload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        """将文件上传到沙盒中。"""
        from opensandbox.models import WriteEntry

        logger.info(f"准备上传 {len(files)} 个文件")
        responses: list[FileUploadResponse] = []
        upload_entries = []

        for i, (path, content) in enumerate(files):
            logger.debug(f"正在处理第 {i + 1}/{len(files)} 个待上传文件：{path}，大小：{len(content)} 字节")

            if not path.startswith("/"):
                logger.error(f"非法路径（必须是绝对路径）：{path}")
                responses.append(FileUploadResponse(path=path, error="invalid_path"))
                continue

            try:
                # 将字节内容转换为字符串
                if isinstance(content, bytes):
                    try:
                        content_str = content.decode("utf-8")
                        logger.debug(f"已按 UTF-8 解码字节内容，长度：{len(content_str)} 字符")
                    except UnicodeDecodeError as decode_error:
                        logger.warning(f"UTF-8 解码失败，将以字符串形式存储：{decode_error}")
                        content_str = str(content)
                else:
                    content_str = str(content)

                upload_entries.append(WriteEntry(path=path, data=content_str, mode=0o644))
                responses.append(FileUploadResponse(path=path, error=None))
                logger.debug(f"文件已加入上传队列：{path}")

            except Exception as e:
                logger.error(f"准备上传文件 {path} 时出错：{str(e)}", exc_info=True)
                responses.append(FileUploadResponse(path=path, error=str(e)))

        # 如果有文件要上传
        if upload_entries:
            logger.info(f"正在向沙盒写入 {len(upload_entries)} 个文件")
            try:
                self._sandbox.files.write_files(upload_entries)
                logger.info(f"成功上传 {len(upload_entries)} 个文件")

            except Exception as e:
                logger.error(f"上传文件时出错：{str(e)}", exc_info=True)
                # 如果有任何错误，更新所有响应
                for i, resp in enumerate(responses):
                    if resp.error is None:
                        responses[i] = FileUploadResponse(
                            path=resp.path,
                            error=f"upload_failed: {str(e)}"
                        )
        else:
            logger.warning("没有有效的文件需要上传")

        # 统计上传结果
        success_count = sum(1 for r in responses if r.error is None)
        error_count = len(responses) - success_count
        logger.info(f"文件上传完成，成功 {success_count} 个，失败 {error_count} 个")

        return responses