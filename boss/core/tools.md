# 工具

`tools/` 只保留当前技能需要的确定性辅助工具。详细背景放在对应 reference，入口文档只保留怎么用。

## install-ff-stop-hooks.mjs

把 `.ai/ff.yaml` 牛马模式安装到 Codex、Claude Code、OpenCode。安装细节见 [`../references/stop-hooks-installation.md`](../references/stop-hooks-installation.md)；执行规程见 [`../guides/ff-execution.md`](../guides/ff-execution.md)，实际 prompt 写法见 [`../references/stop-hooks.md`](../references/stop-hooks.md)。

```bash
node tools/install-ff-stop-hooks.mjs
```

安装器会保守合并现有配置，不会清空已有 hooks。项目级开关模板见 [`../assets/stop-hooks/ff.yaml`](../assets/stop-hooks/ff.yaml)。
