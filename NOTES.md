### Deep Agents 牛的四个地方：

1. 规划能力 （拆解任务）
2. 文件系统 （虚拟文件系统的底层实现）

>默认是 StateBackend，存放临时文件
> FilesystemBackend
> LocalShellBackend
>CompositeBackend （路由混合）
混合策略： StateBackend + StoreBackend (长期记忆)
> 自定义 backend

3. 需要子 Agent

4. 需要子 skills

绝大多数时候用官方现成的 MemoryBackend / LocalFileBackend 就够了。只有当你需要接入特殊存储、加权限/加密/日志等横切关注点时，才需要自定义 Backend——本质上就是给 DeepAgents 的文件操作套一层你自己的逻辑。