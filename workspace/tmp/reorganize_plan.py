#!/usr/bin/env python3
import json
from datetime import datetime, timedelta

def create_reorganization_plan():
    # Load tasks data
    with open('/tmp/all_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tasks = data.get('tasks', [])
    current_time = datetime.now()
    
    # Find overdue tasks
    overdue_tasks = []
    for task in tasks:
        if task.get('status') != 0:  # Skip completed tasks
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
    
    # Define priority mapping based on tags and content
    priority_mapping = {
        # High priority (5) - Learning and career development
        '学习': 5, '技术': 5, '课程': 5, '加密': 5, '架构': 5,
        # Medium-high priority (3) - Projects and important tasks  
        '项目': 3, '规划': 3, '治理': 3, '系统': 3, '微服务': 3,
        # Medium priority (1) - Regular tasks
        '文档': 1, '工具': 1, '试用': 1, '整理': 1
    }
    
    # Generate new schedule for next 2 weeks
    start_date = current_time + timedelta(days=1)  # Start from tomorrow
    end_date = start_date + timedelta(days=14)     # 2 weeks period
    
    # Create time slots - morning and afternoon for each day
    time_slots = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Weekdays only
            time_slots.append(current_date.replace(hour=10, minute=0, second=0))  # 10:00 AM
            time_slots.append(current_date.replace(hour=14, minute=0, second=0))  # 2:00 PM
        current_date += timedelta(days=1)
    
    # Categorize tasks for better distribution
    learning_tasks = []
    project_tasks = []
    maintenance_tasks = []
    
    for task in overdue_tasks:
        title = task.get('title', '').lower()
        tags = task.get('tags', [])
        
        # Determine task category and priority
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
    
    # Assign new priorities and schedule
    reorganized_tasks = []
    slot_index = 0
    
    # First pass: Schedule high-priority learning tasks
    for task in learning_tasks:
        if slot_index >= len(time_slots):
            break
        
        new_priority = 5
        new_start = time_slots[slot_index]
        new_due = new_start
        
        reorganized_tasks.append({
            'task': task,
            'new_priority': new_priority,
            'new_start_date': new_start.isoformat() + '+0000',
            'new_due_date': new_due.isoformat() + '+0000'
        })
        slot_index += 1
    
    # Second pass: Schedule project tasks
    for task in project_tasks:
        if slot_index >= len(time_slots):
            break
            
        new_priority = 3
        new_start = time_slots[slot_index]
        new_due = new_start
        
        reorganized_tasks.append({
            'task': task,
            'new_priority': new_priority,
            'new_start_date': new_start.isoformat() + '+0000',
            'new_due_date': new_due.isoformat() + '+0000'
        })
        slot_index += 1
    
    # Third pass: Schedule maintenance tasks
    for task in maintenance_tasks:
        if slot_index >= len(time_slots):
            break
            
        new_priority = 1
        new_start = time_slots[slot_index]
        new_due = new_start
        
        reorganized_tasks.append({
            'task': task,
            'new_priority': new_priority,
            'new_start_date': new_start.isoformat() + '+0000',
            'new_due_date': new_due.isoformat() + '+0000'
        })
        slot_index += 1
    
    return reorganized_tasks

def generate_update_commands(reorganized_tasks):
    """Generate dida365 CLI commands to update tasks"""
    commands = []
    
    for item in reorganized_tasks:
        task = item['task']
        task_id = task['id']
        
        # Format dates for dida365 CLI
        start_date = item['new_start_date'].replace('+0000', '.000+0000')
        due_date = item['new_due_date'].replace('+0000', '.000+0000')
        
        # Create update command
        cmd = f'npx dida365 task update {task_id} --startDate "{start_date}" --dueDate "{due_date}" --priority {item["new_priority"]}'
        commands.append(cmd)
    
    return commands

if __name__ == '__main__':
    reorganized = create_reorganization_plan()
    commands = generate_update_commands(reorganized)
    
    print(f"📋 重新组织计划:")
    print(f"总共需要重新安排的任务: {len(reorganized)}")
    print()
    
    # Group by priority for display
    by_priority = {}
    for item in reorganized:
        priority = item['new_priority']
        if priority not in by_priority:
            by_priority[priority] = []
        by_priority[priority].append(item)
    
    for priority in sorted(by_priority.keys(), reverse=True):
        items = by_priority[priority]
        print(f"🎯 优先级 {priority}: {len(items)} 个任务")
        for item in items:
            task = item['task']
            date_str = item['new_start_date'].split('T')[0]
            print(f"  - {task['title']} ({date_str})")
        print()
    
    print(f"🔧 执行命令:")
    for i, cmd in enumerate(commands, 1):
        print(f"{i:2d}. {cmd}")
    
    # Save commands to file
    with open('/tmp/update_commands.sh', 'w') as f:
        f.write('#!/bin/bash\n\n')
        f.write('echo "开始重新安排滴答清单任务..."\n')
        for cmd in commands:
            f.write(f'{cmd}\n')
        f.write('echo "任务重新安排完成!"\n')
    
    print(f"\n💾 命令已保存到 /tmp/update_commands.sh")