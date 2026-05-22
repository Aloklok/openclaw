# 协同记忆 (MEMORY.md)

## 👤 用户事实
- **身份**: Alok, AI 产品经理，处于求职阶段
- **交互风格**: 直接、高效，拒绝客套话

## ⚙️ 核心偏好
- **天气**: 禁用内置 weather，优先用和风天气 SKILL（深圳 114.065162,22.686102）
- **输出格式**: 使用 emoji（☂️💨👕等）提高直观性
- **任务管理**: 滴答清单 API 操作前必须实时获取最新标签，禁止硬编码

## 🎯 关键决策
- **天气查询**: 禁用内置 weather，强制使用和风天气 SKILL
- **定时任务**: 已修复微信发送配置问题（target 需用 userId）
- **任务组织**: 按主题相似性分组处理，减少切换成本

## 🏷️ 标签体系
- 云基础设施（阿里云）、项目管理、数据相关、智慧城市

## 📌 技术要点
- 滴答清单：创建子任务后立即同步获取 ID，用 batch set-subtask 建立关系
- 喝水心跳：消息发送目标需用 userId，不是名字

## Promoted From Short-Term Memory (2026-05-16)

<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:386:394 -->
- <!-- openclaw:dreaming:rem:start --> ### Reflections - Theme: `assistant` kept surfacing across 993 memories. - confidence: 1.00 - evidence: memory/.dreams/session-corpus/2026-04-08.txt:3-3, memory/.dreams/session-corpus/2026-04-08.txt:5-5, memory/.dreams/session-corpus/2026-04-08.txt:7-7 - note: reflection ### Possible Lasting Truths - - Candidate: Assistant: 很好！我已经记录了您今天的饮水情况： ## 💧 今日饮水记录 - **饮水量**: 750ml (250ml咖啡 + 500ml汤) - **记录时间**: 2026-04-08 20:07 - **状态**: 已记录 ✅ 关于您提到的今天任务，我刚才已经成功将 RSS 简报任务调整到今天，现在它在您的滴答清单中显示为： - **开始时间**: 今天 18:00 - **截止时间**: 今天 18:00 您可以处理这个任务，完成后记得在滴答清单 APP 中标记为已完成哦！ 关于您今天的饮水，750ml 是个不错的开始。记得继续保持 - confidence: 0.00 - evidence: memory/.dreams/session-corpus/2026-04-08.txt:227-227 - recalls: 0 - status: staged - Candidate: Assistant: 完成！我已经将 RSS 简报任务的执行时间从原来的 4 月 10 日提前到了今天（4 月 8 日）下午 3 点。 **更新详情：** - **任务ID**: 6923f756801e91f65736ba88 - **任务标题**: RSS简报 - **原执行时间**: 2026-04-10 08:00 - **新执行时间**: 2026-04-08 15:00（今天下午3点） - **项目**: 收件箱(inbox1011383017) 现在这个任务已经提前到今天了。您还需要我做什么其他的安排吗？ - conf [confidence=0.94 evidence=memory/2026-04-10.md:138-147] [score=1.000 recalls=5 avg=1.000 source=memory/2026-04-16.md:386-394]
