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