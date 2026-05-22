#!/usr/bin/env python3
import json
from datetime import datetime, timedelta
import sys

# Load task data
with open('/home/node/.openclaw/workspace/tasks.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

tasks = data['tasks']

# Current date (2026-04-12 as given in the prompt)
current_date = datetime(2026, 4, 12).date()
three_days_ago = current_date - timedelta(days=3)

print("=== 滴答清单任务分析报告 ===\n")

# Find overdue tasks (from past 3 days)
overdue_tasks = []
today_tasks = []

for task in tasks:
    # Skip completed tasks
    if task.get('status') == 2:
        continue
        
    # Parse due date
    due_date_str = task.get('dueDate')
    if not due_date_str:
        continue
        
    try:
        # Parse the date string (format: 2026-04-14T15:59:59.000+0000)
        due_date = datetime.strptime(due_date_str[:10], '%Y-%m-%d').date()
        
        # Check if overdue (from past 3 days)
        if three_days_ago <= due_date < current_date:
            overdue_tasks.append(task)
        # Check if due today
        elif due_date == current_date:
            today_tasks.append(task)
    except:
        continue

print(f"1. 过期任务检查 (过去3天内): {len(overdue_tasks)} 个任务\n")

if overdue_tasks:
    print("发现以下过期未完成任务:")
    for i, task in enumerate(overdue_tasks, 1):
        due_date_str = task.get('dueDate', '')
        due_date = due_date_str[:10] if due_date_str else '无日期'
        title = task.get('title', '无标题')
        project_id = task.get('projectId', '')
        
        # Find project name
        project_name = '未知项目'
        for project in data['projects']:
            if project['id'] == project_id:
                project_name = project['name']
                break
                
        print(f"  {i}. [{project_name}] {title} (原定: {due_date})")
    print()
else:
    print("✅ 过去3天内没有过期未完成任务\n")

print(f"2. 今日任务清单: {len(today_tasks)} 个任务\n")

if today_tasks:
    print("今日需要完成的任务:")
    for i, task in enumerate(today_tasks, 1):
        title = task.get('title', '无标题')
        project_id = task.get('projectId', '')
        priority = task.get('priority', 0)
        
        # Find project name
        project_name = '未知项目'
        for project in data['projects']:
            if project['id'] == project_id:
                project_name = project['name']
                break
        
        # Priority indicators
        priority_map = {0: '', 1: '🔵', 3: '🟡', 5: '🔴'}
        priority_icon = priority_map.get(priority, '')
        
        print(f"  {i}. [{project_name}] {title} {priority_icon}")
    print()
else:
    print("✅ 今天没有安排具体任务\n")

print("3. 任务处理建议:")
if overdue_tasks:
    print("   • 建议将过期任务日期更新到今天")
    print("   • 优先处理高优先级任务")
print("   • 合理安排今日任务时间")

print("\n=== 分析完成 ===")
