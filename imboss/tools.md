# MC 工具套件

四个 Python 工具，用于持续推进 plans。位于 `tools/` 下，免安装，直接跑。

## mc-core.py

Mission Control 核心进程。持续启动 Agent CLI，每轮执行一个任务，写运行记录，根据指令暂停/继续/停止。

```
python tools/mc-core.py \
  --provider claude \
  --skill imboss \
  --prompt "读取 .boss/plans/INDEX.md，定位唯一 active plan，完成当前阶段下一个未完成任务" \
  --interval 5
```

| 参数 | 说明 |
|------|------|
| `--root` | 任务目录，默认 `.boss/` |
| `--provider` | Agent CLI：codex / claude / opencode / gemini |
| `--prompt "..."` | Agent CLI 的工作指令；必须显式提供，MC Core 没有默认提示词 |
| `--prompt-file p.md` | 从文件读取 Agent CLI 的工作指令 |
| `--skill NAME` | 每个回合启动前加载指定 skill（如 imboss） |
| `--command ...` | 完全自定义启动命令，`{prompt}` 会被替换 |
| `--interval N` | 每轮间隔秒数，默认 5 |
| `--max-rounds N` | 最多跑 N 轮后自动停 |
| `--cwd DIR` | Agent CLI 的工作目录 |
| `--dry-run` | 打印拼接好的命令，不实际启动 |
| `--start-paused` | 启动后暂停，等 `resume` 命令 |

MC Core 不承担默认提示词、计划解析或项目上下文拼装职责。它只负责进程生命周期；工作指令必须在启动时通过 `--prompt` 或 `--prompt-file` 显式提供。需要读取 plans、requirements、architecture、tasks 的规则，由启动 prompt 或被加载的 skill 自己规定。

## mc-cli.py

MC Core 的 CLI 控制器。对运行中的 core 发指令，或启动新 core。

```bash
# 启动 MC Core（后台常驻，每轮自动启动 Agent CLI 推进 plan）
python tools/mc-cli.py start --provider claude --skill imboss --prompt "读取 .boss/plans/INDEX.md，定位唯一 active plan，完成当前阶段下一个未完成任务"

# 自定义推进提示词
python tools/mc-cli.py start --provider claude --skill imboss --prompt "读取 .boss/plans/INDEX.md，定位唯一 active plan，完成当前阶段下一个未完成任务"

# 干跑看拼接结果
python tools/mc-cli.py start --provider claude --skill imboss --prompt "读取 .boss/plans/INDEX.md，定位唯一 active plan，完成当前阶段下一个未完成任务" --dry-run

# 查看状态
python tools/mc-cli.py status
python tools/mc-cli.py status --json

# 查看日志
python tools/mc-cli.py logs --lines 50
python tools/mc-cli.py logs --follow

# 发送控制指令
python tools/mc-cli.py pause     # 暂停
python tools/mc-cli.py resume    # 继续
python tools/mc-cli.py wake      # 立刻唤醒跑一轮
python tools/mc-cli.py stop      # 停止

# 打开浮动状态窗
python tools/mc-cli.py window
python tools/mc-cli.py window --all   # 显示所有注册的 .boss root
```

### 启动时提供工作指令

`--prompt` 或 `--prompt-file` 是必需的。MC Core 没有默认提示词，启动者必须自行规定 Agent 每轮收到的工作指令：

常驻执行的 prompt 必须和当前进度解耦。它应该描述“每轮如何重新读取状态、选择下一个动作、更新文档和验证”，而不是写死某个阶段、某个 task 编号或某个临时结论。MC Core 会复用同一 prompt；如果 prompt 里包含进度快照，阶段推进后会反复把 Agent 拉回旧状态。

```bash
# 示例 1：只做 code review
python tools/mc-cli.py start \
  --provider claude \
  --prompt "读取 .boss/plans/INDEX.md 和唯一 active plan，对当前未 review 的改动逐文件 review；active plan 超过 200 行则先压缩"

# 示例 2：按 plan 逐个消灭任务
python tools/mc-cli.py start \
  --provider claude \
  --skill imboss \
  --prompt "按 imboss 路径 E 执行：每轮重新读取 .boss/CONVENTIONS.md、.boss/PROFILE.md、.boss/plans/INDEX.md、唯一 active plan、相关 requirements、architecture 和 tasks；确认 active plan 不超过 200 行；基于当前文档状态选择下一个最小可验证动作，执行、验证并更新 active plan/tasks/交付物。不要依赖启动时的旧进度快照。"

# 示例 3：只生成文档
python tools/mc-cli.py start \
  --provider claude \
  --prompt "读取 src/ 下所有文件，生成架构文档写入 .boss/architecture/OVERVIEW.md"
```

## mc-status-window.py

浮动 Tkinter 状态窗口，只读观察所有 MC Core 实例。

```
python tools/mc-status-window.py --root .boss
python tools/mc-status-window.py --root .boss --all --refresh 3
```

## scan-agent-clis.py

扫描本地可用的 Agent CLI，输出可用列表。

```
python tools/scan-agent-clis.py
python tools/scan-agent-clis.py --json
```

## 与 imboss 的协作

MC Core 跑起来后，每轮：
1. 启动 Agent CLI（claude / codex / opencode / gemini）
2. Agent CLI 收到启动时显式提供的 prompt；如果传了 `--skill`，Core 只加一段加载 skill 的前置语
3. Agent 按 prompt 和 skill 规则读取 `.boss/plans/INDEX.md`、requirements、architecture、tasks 等上下文
4. Agent 执行、验证并更新相应文档；需要长执行记录时写入 `.boss/tasks/`
5. Agent 退出，Core 等待 interval 秒后启动下一轮

`.boss/` 是 imboss 的工作目录，`.boss/plans/INDEX.md` 是计划入口，唯一 active 大 plan 是计划中枢。这些都是 Agent/skill 的工作纪律，不是 MC Core 的内置逻辑。MC Core 不管理任务，只管理进程生命周期。
