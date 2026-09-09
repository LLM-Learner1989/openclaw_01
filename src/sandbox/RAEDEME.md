### OpenSandbox

1. 网上下载几个 skill 跑跑

2. skill 在沙箱中运行

直接在 LangSmith studio 问，

- 帮我找找，关于 skills 的微信公众号的内容
- 你把 AGENTS.md 安装到哪里去呢？
- 你的沙箱中有 python 执行环境吗？

跑下面两个命令：（前提是要先启动 opensandbox-server）

```
pip install -e .

langgraph dev
```

### 踩过的坑

根因：Docker runtime 下 Server 只能用 ingress.mode="direct"，没法做 proxy。所以 Mac 永远访问不到容器的 172.17.0.2。

解决办法：

把 docker.network_mode 改成 "host"，就可以访问到了。

改成 host 网络模式后，docker.port_range_min/max 就没用了（host 模式下容器直接用宿主机端口，不需要 -p 映射）
