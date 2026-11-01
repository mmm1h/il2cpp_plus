# Unity 7 运行时补丁

目标是 Unity `7000.0.0a12`，修订 `8751f7c83ed7`。仓库原有 `libil2cpp` 保持官方 Unity 6.3 基线。Unity 7 原始源码从开发者本机安装读取，本目录仅分发差异补丁与版本清单。

`prepare_probe.py` 校验完整原版源码树的文件数量和 SHA-256，拒绝不同版本、被修改的输入或已有输出。在独立目录复制 Unity 7 源码，按顺序应用全部补丁，再加入配套解释器。`--with-toolchain` 同时复制同版本 IL2CPP 工具，供独立运行时验证使用。

补丁保留 Unity 7 的序列化格式，在解码结果中补充解释器需要的类型、签名和 token。它们接入泛型与接口分发、反射、动态 GC 根、程序集注册、现代加载上下文和运行时清理。解释器特性构造器保留原有索引表示，AOT 特性继续使用 Unity 7 的编码索引。

Win64 独立 IL2CPP 程序已成功加载并执行两版外部热更 DLL。对象编译覆盖解释器和受影响的现代运行时源码；旧 Mono BCL 的反射源码在清单中明确排除。完整验证入口和范围见 [解释器说明](https://github.com/mmm1h/hybridclr/blob/codex/unity7-support/UNITY7.md)。

工具保留 `INCOMPLETE_PORT.json` 标记与默认编译防护，不安装或注册运行库。Unity Editor 安装及 Player 集成仍在适配，Android 和 iOS 未经构建及设备执行验证。
