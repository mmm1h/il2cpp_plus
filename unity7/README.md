# Unity 7 基础补丁

状态：原生适配未完成，不能作为 HybridCLR Installer 的输入。

目标为 Unity `7000.0.0a12`，修订 `8751f7c83ed7`。仓库原有 `libil2cpp` 仍是官方 `v6000.3.x-9.0.1` 基线，不能覆盖 Unity 7 的运行时。Unity 7 的原始源码从开发者本机安装读取，本目录只保存基础差异补丁和必要工具。

`prepare_probe.py` 校验受影响源文件和完整源码树的 SHA-256，拒绝不同版本或被修改的输入，将 Unity 7 源码复制到新目录后应用补丁。补丁接入版本定义，追加解释器需要的 `MethodInfo` 状态，提供自定义属性范围别名和异常工厂。泛型上下文转换等配套变更位于 [hybridclr 维护分支](https://github.com/mmm1h/hybridclr/tree/codex/unity7-support)。

公共接口与运行时异常源码已通过对象编译，泛型上下文通过可执行测试。完整原生源码诊断仍失败。尚未移植的部分包括 `GlobalMetadata` 分发、压缩方法签名与 token 重建、解释器私有元数据、接口分发、动态 GC 根和程序集加载。这些补丁没有链接成可运行的 HybridCLR，不提供移动端兼容结论。

运行方式见 [解释器验证说明](https://github.com/mmm1h/hybridclr/blob/codex/unity7-support/UNITY7.md)。工具只生成源码探测树，保留 `INCOMPLETE_PORT.json` 标记，拒绝覆盖已有输出，不改 Unity 安装目录，也不注册本地运行时。
