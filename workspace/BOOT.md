# BOOT.md

OpenClaw 启动时的自动化指令（由系统在每次 Boot 时自动执行）。执行完毕后请务必回复 `NO_REPLY` 以保持静默。

## 1. 核心状态检查 (Pre-flight Checks)
- **滴答清单同步**：运行一次同步指令，确保任务列表是最新的。
  - `npx -y dida365-ai-tools sync all`
- **Skill 依赖预检**：检查关键 Skill（如 dida365-cli, hydro-heartbeat）是否可正常运行。

## 2. 内存热启动 (Memory Warmup)
- 快速浏览 `MEMORY.md` 和昨天的 `memory/YYYY-MM-DD.md`，确立当日工作的连续性。

## 3. 上线通知 (Optional)
- 如果发现关键系统异常（如认证失效），使用 `message` 工具发送静默提醒。
- 如果一切正常，无需吵醒人类。

---

**结束指令**：
所有启动项完成后，必须直接且仅输出：
`NO_REPLY`
