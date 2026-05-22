#!/usr/bin/env python3
import json
from datetime import datetime, timedelta
import subprocess

def fix_date_format(date_str):
    """Fix the date format for dida365 CLI"""
    dt = datetime.fromisoformat(date_str.replace('+0000', ''))
    return dt.strftime('%Y-%m-%dT%H:%M:%S.000+0000')

def execute_reorganization():
    # Load tasks data
    with open('/tmp/all_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tasks = data.get('tasks', [])
    current_time = datetime.now()
    
    # Find overdue tasks
    overdue_tasks = []
    for task in tasks:
        if task.get('status') != 0:
            continue
            
        due_date_str = task.get('dueDate')
        if not due_date_str:
            continue
            
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            due_date = due_date.replace(tzinfo=None)
        except:
            continue
            
        if due_date < current_time:
            overdue_tasks.append(task)
    
    # Create reorganization plan
    start_date = current_time + timedelta(days=1)
    end_date = start_date + timedelta(days=14)
    
    # Generate time slots (weekdays only)
    time_slots = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Weekdays
            time_slots.append(current_date.replace(hour=10, minute=0, second=0))
            time_slots.append(current_date.replace(hour=14, minute=0, second=0))
        current_date += timedelta(days=1)
    
    # Categorize and prioritize tasks
    learning_tasks = []
    project_tasks = []
    maintenance_tasks = []
    
    for task in overdue_tasks:
        title = task.get('title', '').lower()
        tags = task.get('tags', [])
        
        is_learning = any(keyword in title for keyword in ['学习', '课程', '教程', '加密']) or \
                     any(tag in ['在线课程', '对称加密', '系统架构', 'ddd'] for tag in tags)
        
        is_project = any(keyword in title for keyword in ['项目', '规划', '治理', '系统']) or \
                    any(tag in ['项目规划', '治理', '微服务', '系统建模'] for tag in tags)
        
        if is_learning:
            learning_tasks.append(task)
        elif is_project:
            project_tasks.append(task)
        else:
            maintenance_tasks.append(task)
    
    # Execute updates
    slot_index = 0
    updated_count = 0
    
    print("🚀 开始重新安排任务...")
    
    # Update learning tasks (priority 5)
    for task in learning_tasks:
        if slot_index >= len(time_slots):
            break
        
        new_time = time_slots[slot_index]
        start_date_fixed = fix_date_format(new_time.isoformat() + '+0000')
        due_date_fixed = start_date_fixed
        project_id = task.get('projectId', 'inbox1011383017')
        
        # Use JSON format to update task
        json_data = {
            "startDate": start_date_fixed,
            "dueDate": due_date_fixed,
            "priority": 5
        }
        
        cmd = f'npx dida365 task update {task["id"]} -p {project_id} --json \'{json.dumps(json_data)}\''
        
        print(f"更新学习任务: {task['title']}")
        print(f"命令: {cmd}")
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                print(f"✅ 成功更新: {task['title']}")
                updated_count += 1
            else:
                print(f"❌ 更新失败: {task['title']}")
                print(f"错误: {result.stderr}")
                if result.stdout:
                    print(f"输出: {result.stdout}")
        except Exception as e:
            print(f"❌ 执行错误: {e}")
        
        slot_index += 1
    
    # Update project tasks (priority 3)
    for task in project_tasks:
        if slot_index >= len(time_slots):
            break
            
        new_time = time_slots[slot_index]
        start_date_fixed = fix_date_format(new_time.isoformat() + '+0000')
        due_date_fixed = start_date_fixed
        project_id = task.get('projectId', 'inbox1011383017')
        
        json_data = {
            "startDate": start_date_fixed,
            "dueDate": due_date_fixed,
            "priority": 3
        }
        
        cmd = f'npx dida365 task update {task["id"]} -p {project_id} --json \'{json.dumps(json_data)}\''
        
        print(f"更新项目任务: {task['title']}")
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                print(f"✅ 成功更新: {task['title']}")
                updated_count += 1
            else:
                print(f"❌ 更新失败: {task['title']}")
        except Exception as e:
            print(f"❌ 执行错误: {e}")
        
        slot_index += 1
    
    # Update maintenance tasks (priority 1)
    for task in maintenance_tasks:
        if slot_index >= len(time_slots):
            break
            
        new_time = time_slots[slot_index]
        start_date_fixed = fix_date_format(new_time.isoformat() + '+0000')
        due_date_fixed = start_date_fixed
        project_id = task.get('projectId', 'inbox1011383017')
        
        json_data = {
            "startDate": start_date_fixed,
            "dueDate": due_date_fixed,
            "priority": 1
        }
        
        cmd = f'npx dida365 task update {task["id"]} -p {project_id} --json \'{json.dumps(json_data)}\''
        
        print(f"更新维护任务: {task['title']}")
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                print(f"✅ 成功更新: {task['title']}")
                updated_count += 1
            else:
                print(f"❌ 更新失败: {task['title']}")
        except Exception as e:
            print(f"❌ 执行错误: {e}")
        
        slot_index += 1
    
    print(f"\n📊 重新安排完成!")
    print(f"成功更新任务数量: {updated_count}")
    print(f"总共处理任务数量: {len(overdue_tasks)}")

if __name__ == '__main__':
    execute_reorganization()