#!/usr/bin/env python3
"""
修复的 Heartbeat 实现，包含消息发送功能
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

def send_message(content):
    """发送消息到微信"""
    try:
        # 使用 OpenClaw 的 message 工具
        # 由于我们无法直接调用 message 工具，这里使用模拟
        print(f"📱 发送消息到微信: {content}")
        
        # 在实际环境中，这里应该调用 message 工具
        # message.send("openclaw-weixin", "o9cq80y6elATkZb3OAurZezVak0Q@im.wechat", content)
        
        # 为了测试，我们使用 exec 工具
        exec_cmd = f"""
import sys
sys.path.append('/app')
from openclaw.tools.message import message
message.send("openclaw-weixin", "o9cq80y6elATkZb3OAurZezVak0Q@im.wechat", "{content}")
"""
        
        exec_result = subprocess.run([
            "python3", "-c", exec_cmd
        ], capture_output=True, text=True)
        
        if exec_result.returncode == 0:
            print(f"✅ 消息发送成功")
            return True
        else:
            print(f"❌ 消息发送失败: {exec_result.stderr}")
            return False
            
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
    """主函数 - 修复的 Heartbeat 执行流程"""
    print("🔧 启动修复的 Heartbeat...")
    
    # 运行 hydro-heartbeat 检查
    result = run_hydro_check()
    if not result:
        print("❌ hydro-heartbeat 检查失败")
        return
    
    print(f"📊 检查结果: should_prompt={result.get('should_prompt', False)}")
    
    # 检查是否需要提醒
    if result.get("should_prompt", False):
        suggested_prompt = result.get("suggested_prompt")
        if suggested_prompt:
            print(f"📢 检测到需要提醒: {suggested_prompt}")
            
            # 发送消息到微信
            if send_message(suggested_prompt):
                print("✅ 消息发送成功")
            else:
                print("❌ 消息发送失败")
            
            # 记录提醒
            mark_prompt()
            
            print("✅ Heartbeat 执行完成")
        else:
            print("❌ 需要提醒但没有建议文案")
    else:
        print("ℹ️ 不需要提醒")
        print("HEARTBEAT_OK")

if __name__ == "__main__":
    main()