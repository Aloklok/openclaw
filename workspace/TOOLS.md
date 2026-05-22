# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- 你（用户）当前所在物理位置: **广东省深圳市**
- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

### 天气默认位置
- 默认坐标: 114.065162,22.686102 (深圳)
- 使用方式: 询问天气时自动使用此坐标

### ⏰ 官方内置定时任务 (Cron Jobs)
OpenClaw 拥有原生的内部 Cron 引擎，不要自己写外挂 JS/Python 定时脚本！
- 配置文件: `/home/node/.openclaw/cron/jobs.json`
- 运行记录: `/home/node/.openclaw/cron/runs/`
- 任务格式: JSON 格式，支持 cron 表达式
- 当前任务: 早间提醒 (08:00)、次日天气提醒 (21:30)。此配置完全正常，无需干预。



### 播客转录

- API 地址: http://host.docker.internal:7861
- 技能文件: skills/podcast-helper/SKILL.md
- 使用场景: 用户发来小宇宙链接时自动触发
- 输出目录: podcast_outputs/ (挂载自宿主机 E:\iCloudDrive\outputs)
- API 开机自启: 已配置 Windows Startup 快捷方式

### 🛑 严重警告：文件系统操作防幻觉规约 (CRITICAL)

针对较小模型（如 Qwen3-8B 等）容易在调用底层工具时发生「路径幻觉」，**所有 Agent 必须严格遵守以下文件操作铁律**：

1. **分清文件和目录**：`read` 工具**只能**用来读取文本文件的内容。如果用户要求你“查看文件夹列表”、“看看目录下有什么”，你必须使用专用的目录查看工具（如 `run_command` 执行 `ls -la` 或是平台提供的目录专属工具），**严禁用 `read` 工具去读取一个目录**（否则会报 `EISDIR` 错误）。
2. **⚠️ 脚本落点铁律**：除了必须存在的官方配置（如 `*.md` 说明书、JSON 配置文件、`package.json`），**绝对禁止在 workspace 根目录堆砌任何独立的 `.py`、`.js` 脚本文件！**
   - 现存技能（Skill）关联的代码，必须原样存放于各自对应的独立文件夹如 `skills/[技能目录]/scripts/` 内。
   - 所有调试用的临时打草稿脚本，必须创建在 `./tmp/` 目录下（相对于工作区根目录），且验证完成后立即自行清理，严禁成为垃圾驻留在根目录！

### 🔥 最新可用技能清单 (v2026.5.18+)

将新版本的利器记录在案，防止系统在复杂任务中“忘记”调用：
1. **Python 调试器 (`python-debugger`)**：
   - 场景：处理沙盒中复杂的 Python 脚本报错。
   - 能力：支持 `pdb`、代码内 `breakpoint()`、事后剖析（post-mortem）以及 `debugpy` 远程附加 (remote attach)。
2. **Node 节点检查器 (`node-inspector`)**：
   - 场景：用于深度排查 Node.js 运行时的问题。
3. **融合图表生成与梗图**：
   - 包含复杂系统架构的图表生成，以及基于 Imgflip 的 meme 生成（可用于日常交互解压）。
