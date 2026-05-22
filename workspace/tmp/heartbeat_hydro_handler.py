#!/usr/bin/env python3
"""Handle heartbeat events for hydro monitoring."""

import json
import subprocess
import sys
from datetime import datetime

def process_heartbeat():
    """Process heartbeat event for hydration monitoring."""
    try:
        # Check if we're in active hours (09:00-23:00)
        now = datetime.now()
        hour = now.hour
        
        if hour < 9 or hour >= 23:
            print(f"Outside active hours ({hour:02d}:00), skipping hydro check")
            return
            
        # Check hydro-heartbeat status
        result = subprocess.run([
            'python3', 'skills/hydro-heartbeat/scripts/manage.py', 'check', '--context', 'standalone'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Hydro check failed: {result.stderr}")
            return
            
        status = json.loads(result.stdout)
        
        if status.get('should_prompt', False):
            prompt_text = status.get('suggested_prompt', '该喝水了！')
            total_ml = status.get('today_total_ml', 0)
            goal_ml = status.get('goal_ml', 1500)
            remaining_ml = status.get('remaining_ml', 1500)
            
            message = f"💧 {prompt_text}\n\n今日已饮水: {total_ml}ml / {goal_ml}ml\n还需饮水: {remaining_ml}ml"
            
            # Send message via OpenClaw message tool
            try:
                send_result = subprocess.run([
                    'openclaw', 'message', 'send', 
                    '--target', 'o9cq80y6elATkZb3OAurZezVak0Q@im.wechat'
                ], input=message, text=True, capture_output=True, timeout=30)
                
                if send_result.returncode == 0:
                    print(f"Hydro reminder sent via heartbeat at {now}")
                    
                    # Mark as prompted
                    subprocess.run([
                        'python3', 'skills/hydro-heartbeat/scripts/manage.py', 'mark-prompt', '--kind', 'standalone'
                    ], capture_output=True)
                else:
                    print(f"Failed to send hydro reminder: {send_result.stderr}")
                    
            except Exception as e:
                print(f"Error sending hydro reminder: {e}")
        else:
            print(f"Heartbeat hydro check: no prompt needed at {now}")
            
    except Exception as e:
        print(f"Error in heartbeat hydro handler: {e}")

if __name__ == '__main__':
    # This script is called by heartbeat
    process_heartbeat()