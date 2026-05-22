#!/usr/bin/env python3
"""Persistent hydro heartbeat monitor."""

import subprocess
import time
import json
from datetime import datetime

def check_and_send_hydration():
    """Check hydration and send reminder if needed."""
    try:
        # Check hydro-heartbeat status
        result = subprocess.run([
            'python3', 'skills/hydro-heartbeat/scripts/manage.py', 'check', '--context', 'standalone'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Hydro check failed: {result.stderr}")
            return False
            
        status = json.loads(result.stdout)
        
        if status.get('should_prompt', False):
            prompt_text = status.get('suggested_prompt', '该喝水了！')
            total_ml = status.get('today_total_ml', 0)
            goal_ml = status.get('goal_ml', 1500)
            remaining_ml = status.get('remaining_ml', 1500)
            
            message = f"💧 {prompt_text}\n\n今日已饮水: {total_ml}ml / {goal_ml}ml\n还需饮水: {remaining_ml}ml"
            
            # Send message
            try:
                send_result = subprocess.run([
                    'openclaw', 'message', 'send', 
                    '--target', 'o9cq80y6elATkZb3OAurZezVak0Q@im.wechat'
                ], input=message, text=True, capture_output=True, timeout=30)
                
                if send_result.returncode == 0:
                    print(f"Hydration reminder sent at {datetime.now()}")
                    
                    # Mark as prompted
                    subprocess.run([
                        'python3', 'skills/hydro-heartbeat/scripts/manage.py', 'mark-prompt', '--kind', 'standalone'
                    ], capture_output=True)
                    
                    return True
                else:
                    print(f"Failed to send: {send_result.stderr}")
                    return False
                    
            except Exception as e:
                print(f"Send error: {e}")
                return False
        else:
            print(f"No prompt needed at {datetime.now()}")
            return False
            
    except Exception as e:
        print(f"Check error: {e}")
        return False

def main():
    """Main monitoring loop."""
    print(f"Starting hydro heartbeat monitor at {datetime.now()}")
    
    while True:
        check_and_send_hydration()
        time.sleep(1800)  # Check every 30 minutes

if __name__ == '__main__':
    main()