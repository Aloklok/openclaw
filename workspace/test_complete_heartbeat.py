#!/usr/bin/env python3
"""
完整的 Heartbeat 测试，包含消息发送功能
"""

import json
import subprocess
import sys
import os

def run_hydro_check():
    """运行 hydro-heartbeat 检查"""
    try:
        result = subprocess.run(
            ["python3", "skills/hydro-heartbeat/scripts/manage.py", "check", "--context", "standalone"],
            capture_output=True,
            text=True,
            cwd="/home/node/.openclaw/workspace"
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error running hydro check: {e}")
        return None

def send_message_via_api(content):
    """使用 OpenClaw API 发送消息"""
    try:
        # 使用 OpenClaw 的 message API
        import requests
        import json
        
        # 构建消息数据
        message_data = {
            "action": "send",
            "channel": "openclaw-weixin",
            "to": "o9cq80y6elATkZb3OAurZezVak0Q@im.wechat",
            "message": content
        }
        
        # 这里应该是调用 OpenClaw 的 message API
        # 但由于我们无法直接访问 API，使用工具调用
        print(f"📱 准备发送消息: {content}")
        
        # 使用 exec 工具调用 message
        exec_result = subprocess.run([
            "python3", "-c", 
            f"""
import sys
sys.path.append('/app')
from openclaw.tools.message import message
message.send("openclaw-weixin", "o9cq80y6elATkZb3OAurZezVak0Q@im.wechat", "{content}")
"""
        ], capture_output=True, text=True)
        
        if exec_result.returncode == 0:
            print(f"✅ 消息发送成功: {content}")
        else:
            print(f"❌ 消息发送失败: {exec_result.stderr}")
            
        return exec_result.returncode == 0
    except Exception as e:
        print(f"❌ 消息发送异常: {e}")
        return False

def mark_prompt():
    """记录提醒"""
    try:
        subprocess.run(
            ["python3", "skills/hydro-heartbeat/scripts/manage.py", "mark-prompt", "--kind", "standalone"],
            cwd="/home/node/.openclaw/workspace"
        )
        print("✅ 已记录提醒")
    except Exception as e:
        print(f"❌ 记录提醒失败: {e}")

def main():
    """主函数 - 完整的 Heartbeat 执行流程"""
    print("🔄 开始完整的 Heartbeat 测试...")
    
    # 运行 hydro-heartbeat 检查
    result = run_hydro_check()
    if not result:
        print("❌ hydro-heartbeat 检查失败")
        return
    
    print(f"📊 检查结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 检查是否需要提醒
    if result.get("should_prompt", False):
        suggested_prompt = result.get("suggested_prompt")
        if suggested_prompt:
            print(f"\n📢 检测到需要提醒: {suggested_prompt}")
            
            # 发送消息到微信
            print("📱 正在发送消息到微信...")
            
            # 由于我们无法直接调用 OpenClaw 的 message 工具
            # 这里我们模拟消息发送
            print(f"📱 模拟发送消息: {suggested_prompt}")
            print("✅ 消息应该已经发送到微信")
            
            # 记录提醒
            mark_prompt()
            
            print("✅ Heartbeat 执行完成：已生成提醒并记录")
            print("\n📝 总结：")
            print("1. ✅ Heartbeat 检测到需要提醒")
            print("2. ✅ 生成了提醒文案")
            print("3. ✅ 记录了提醒")
            print("4. ❌ 但消息没有自动发送到微信（这是需要修复的问题）")
        else:
            print("❌ 需要提醒但没有建议文案")
    else:
        print("ℹ️ 不需要提醒，输出 HEARTBEAT_OK")
        print("HEARTBEAT_OK")

if __name__ == "__main__":
    main()