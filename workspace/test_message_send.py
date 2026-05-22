#!/usr/bin/env python3
"""
测试消息发送功能
"""

import json
import subprocess

def send_message_via_tool(content):
    """使用 OpenClaw 的 message 工具发送消息"""
    try:
        # 使用 OpenClaw 的 message 工具
        cmd = [
            "python3", "-c", 
            """
import sys
import os
sys.path.insert(0, '/app')
from openclaw.tools.message import message
result = message.send("openclaw-weixin", "o9cq80y6elATkZb3OAurZezVak0Q@im.wechat", """ + repr(content) + """)
print(f"Message sent: {result}")
"""
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/home/node/.openclaw/workspace"
        )
        
        if result.returncode == 0:
            print(f"✅ 消息发送成功: {content}")
            print(f"输出: {result.stdout}")
        else:
            print(f"❌ 消息发送失败: {result.stderr}")
            
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 消息发送异常: {e}")
        return False

def main():
    """测试消息发送"""
    test_message = "测试消息：Heartbeat 修复测试"
    print(f"📱 发送测试消息: {test_message}")
    send_message_via_tool(test_message)

if __name__ == "__main__":
    main()