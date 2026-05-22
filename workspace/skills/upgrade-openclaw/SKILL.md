# Skill: OpenClaw Upgrade Management

## 🎯 目标
确保 OpenClaw 系统能够安全、连续地升级，同时用户对跨版本的重大变更保持知情。

## 🛠 升级核心逻辑 (Refined Protocol)

### 1. 版本跨度审计 (Version Gap Audit)
*   **动作**：在开始升级前，必须先读取 `version.txt` 获取当前版本。
*   **对比**：运行 `ops\fetch_openclaw_release.ps1` 获取最新版本后，对比两者。
*   **补全**：若存在跨版本更新，必须抓取中间版本说明并进行集成式摘要。
*   **脚本增强 (v2026.4.26 修改)**：现有的 `4-手动升级原生OpenClaw.bat` 已更新为通过 `docker inspect` 精准获取容器版本，取代了脆弱的日志抓取逻辑。

### 2. 累积变更总结 (Cumulative Summary)
*   **原则**：严禁只总结最新一个版本。
*   **要求**：必须阅读从“当前版本+1”到“最新版本”的所有 `.upstream.md` 文件。
*   **输出**：向用户提供一个集成式的更新摘要，标注出：
    *   **新增功能**（按模块分类）
    *   **关键修复**（特别是安全相关）
    *   **破坏性变更/配置刷新**（如 Cron 迁移、安全策略收紧等）

### 3. 环境预检与加速
*   确保 `ops\sync_templates.ps1` 正常运行以同步最新的配置指南。
*   利用国内镜像加速（Cloudflare Worker 代理）来绕过网络限制。

### 4. 升级后验证
*   检查 `version.txt` 是否已更新。
*   使用 `docker logs openclaw-gateway` 确认 `[gateway] ready` 信号。
*   运行 `openclaw doctor --fix` 处理新版本带来的架构迁移（如 Cron 状态迁移）。

## ⚠️ 常见陷阱
*   **遗漏中间版本**：忽略中间版本可能导致错失关键的安全修复说明或配置变更操作。
*   **Cron 状态迁移**：v2026.4.20+ 之后 Cron 逻辑有重大变化，必须提醒用户执行迁移。
*   **镜像拉取失败**：若镜像无法拉取，需检查 Docker 守护进程的加速器配置或手动使用代理拉取并重命名为 `openclaw-local:latest`。
