"""
NHR-Management App - A comprehensive task and productivity management system
Features:
- Task management with priorities
- Color-coded tasks
- Notes and reminders
- Reporting and analytics
- Data persistence with JSON
"""

import os
import json
import time
from datetime import datetime, timedelta
from enum import Enum
import sys

# Constants
TASKS_FILE = "tasks.json"
APP_NAME = "NHR-Management App"
VERSION = "1.0.0"

# Color options
class TaskColor(Enum):
    NONE = ""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    END = "\033[0m"

# Global variables
tasks = []

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    """Display the application banner."""
    clear_screen()
    print(f"\n==== {APP_NAME} v{VERSION} ====")
    print("=" * (len(APP_NAME) + 16))

def load_tasks():
    """Load tasks from the JSON file if it exists."""
    global tasks
    try:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r') as file:
                tasks = json.load(file)
            print(f"Loaded {len(tasks)} tasks.")
        else:
            tasks = []
            print("No saved tasks found. Starting with an empty list.")
    except json.JSONDecodeError:
        print("Error loading tasks. File might be corrupted. Starting with empty list.")
        tasks = []
    except (OSError, IOError) as e:
        print(f"File error: {e}. Starting with empty list.")
        tasks = []

def save_tasks():
    """Save tasks to the JSON file."""
    try:
        with open(TASKS_FILE, 'w') as file:
            json.dump(tasks, file, indent=2)
        return True
    except (OSError, IOError) as e:
        print(f"File error while saving tasks: {e}")
        return False

def show_color_options():
    """Display available color options."""
    print("\nAvailable Colors:")
    for i, color in enumerate(TaskColor, 1):
        if color not in [TaskColor.NONE, TaskColor.END]:
            print(f"{i}. {color.value}{color.name}{TaskColor.END.value}")
    print("0. No color")

def select_color():
    """Let user select a color for the task."""
    show_color_options()
    try:
        choice = int(input("\nSelect color (0-7): "))
        if 0 <= choice <= len(TaskColor.__members__) - 2:
            return list(TaskColor)[choice].value
    except ValueError:
        pass
    return TaskColor.NONE.value

def add_task():
    """Add a new task to the list."""
    display_banner()
    print("=== ADD NEW TASK ===\n")
    
    title = input("Enter task title: ").strip()
    if not title:
        print("Task title cannot be empty!")
        time.sleep(1.5)
        return
        
    description = input("Enter task description (optional): ").strip()
    
    # Handle task priority
    priority_options = ["Low", "Medium", "High"]
    print("\nSelect priority:")
    for i, option in enumerate(priority_options, 1):
        print(f"{i}. {option}")
    
    priority = "Medium"  # Default
    try:
        choice = int(input("\nEnter priority (1-3) or press Enter for Medium: ") or "2")
        if 1 <= choice <= 3:
            priority = priority_options[choice-1]
    except ValueError:
        print("Invalid input. Setting priority to Medium.")
    
    # Select color
    color = select_color()
    
    # Add notes
    notes = []
    print("\nAdd notes (leave empty to finish):")
    while True:
        note = input("Note: ").strip()
        if not note:
            break
        notes.append({
            "content": note,
            "created_at": datetime.now().isoformat()
        })
    
    # Add reminder
    reminder = None
    add_reminder = input("\nAdd reminder? (y/n): ").lower() == 'y'
    if add_reminder:
        try:
            days = int(input("Days from now (0 for today): ") or "0")
            hours = int(input("Hours from now: ") or "0")
            reminder_time = datetime.now() + timedelta(days=days, hours=hours)
            reminder = reminder_time.isoformat()
            print(f"Reminder set for {reminder_time.strftime('%Y-%m-%d %H:%M')}")
        except ValueError:
            print("Invalid time input. No reminder set.")
    
    # Create a new task dictionary
    max_id = max((task["id"] for task in tasks), default=0)
            
    task = {
        "id": max_id + 1,
        "title": title,
        "description": description,
        "priority": priority,
        "color": color,
        "notes": notes,
        "reminder": reminder,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    
    tasks.append(task)
    if save_tasks():
        print(f"\nTask '{title}' added successfully!")
    time.sleep(1.5)

def display_task(task):
    """Display a single task with formatting."""
    color_code = task.get("color", "")
    end_color = TaskColor.END.value if color_code else ""
    
    status = "✓" if task["completed"] else "○"
    priority_indicator = ""
    if task["priority"] == "High":
        priority_indicator = "[!!!]"
    elif task["priority"] == "Medium":
        priority_indicator = "[!!]"
    elif task["priority"] == "Low":
        priority_indicator = "[!]"
        
    print(f"{color_code}{task['id']}. [{status}] {priority_indicator} {task['title']}{end_color}")
    if task["description"]:
        print(f"   Description: {task['description']}")
    
    # Display notes if any
    if task.get("notes"):
        print("   Notes:")
        for note in task["notes"]:
            note_time = datetime.fromisoformat(note["created_at"]).strftime("%m/%d %H:%M")
            print(f"     - {note['content']} ({note_time})")
    
    # Display reminder if set
    if task.get("reminder"):
        reminder_time = datetime.fromisoformat(task["reminder"])
        now = datetime.now()
        if reminder_time > now:
            time_left = reminder_time - now
            days = time_left.days
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60
            print(f"   Reminder: {reminder_time.strftime('%Y-%m-%d %H:%M')} (in {days}d {hours}h {minutes}m)")
        else:
            print(f"   Reminder: {reminder_time.strftime('%Y-%m-%d %H:%M')} (passed)")
    
    print(f"   Created: {datetime.fromisoformat(task['created_at']).strftime('%Y-%m-%d %H:%M')}")
    print(f"   Priority: {task['priority']}")
    print("-" * 50)

def list_tasks():
    """Display all tasks with their status."""
    display_banner()
    
    if not tasks:
        print("No tasks found.")
        input("\nPress Enter to continue...")
        return
    
    filters = input("Filter tasks (a=all, c=completed, p=pending, h=high priority, r=with reminders): ").lower() or "a"
    
    display_banner()
    filtered_tasks = []
    
    if filters == "a":
        filtered_tasks = tasks
        print("\n===== ALL TASKS =====")
    elif filters == "c":
        filtered_tasks = [task for task in tasks if task["completed"]]
        print("\n===== COMPLETED TASKS =====")
    elif filters == "p":
        filtered_tasks = [task for task in tasks if not task["completed"]]
        print("\n===== PENDING TASKS =====")
    elif filters == "h":
        filtered_tasks = [task for task in tasks if task["priority"] == "High"]
        print("\n===== HIGH PRIORITY TASKS =====")
    elif filters == "r":
        filtered_tasks = [task for task in tasks if task.get("reminder")]
        print("\n===== TASKS WITH REMINDERS =====")
    else:
        filtered_tasks = tasks
        print("\n===== ALL TASKS =====")
    
    if not filtered_tasks:
        print("No tasks match your filter.")
        input("\nPress Enter to continue...")
        return
        
    # Sort tasks by priority and reminder time
    priority_order = {"High": 1, "Medium": 2, "Low": 3}
    filtered_tasks.sort(key=lambda x: (
        priority_order[x["priority"]],
        x.get("reminder", "9999-12-31"),  # Tasks without reminders go last
        x["id"]
    ))
    
    for task in filtered_tasks:
        display_task(task)
    
    input("\nPress Enter to continue...")

def complete_task():
    """Mark a task as completed."""
    display_banner()
    print("=== MARK TASK AS COMPLETE ===\n")
    
    # Show only pending tasks
    pending_tasks = [task for task in tasks if not task["completed"]]
    
    if not pending_tasks:
        print("No pending tasks found.")
        input("\nPress Enter to continue...")
        return
    
    print("Pending Tasks:")
    for task in pending_tasks:
        print(f"{task['id']}. {task['title']} ({task['priority']})")
    
    try:
        task_id = int(input("\nEnter the ID of the task to mark as complete: "))
        for task in tasks:
            if task["id"] == task_id and not task["completed"]:
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
                if save_tasks():
                    print(f"\nTask '{task['title']}' marked as complete!")
                time.sleep(1.5)
                return
                
        print(f"No pending task found with ID {task_id}")
        time.sleep(1.5)
    except ValueError:
        print("Please enter a valid task ID (number).")
        time.sleep(1.5)

def delete_task():
    """Delete a task from the list."""
    display_banner()
    print("=== DELETE TASK ===\n")
    
    if not tasks:
        print("No tasks found.")
        input("\nPress Enter to continue...")
        return
    
    print("All Tasks:")
    for task in tasks:
        status = "completed" if task["completed"] else "pending"
        print(f"{task['id']}. {task['title']} ({status})")
        
    try:
        task_id = int(input("\nEnter the ID of the task to delete: "))
        for i, task in enumerate(tasks):
            if task["id"] == task_id:
                confirm = input(f"Are you sure you want to delete '{task['title']}'? (y/n): ").lower()
                if confirm == 'y':
                    deleted_task = tasks.pop(i)
                    if save_tasks():
                        print(f"\nTask '{deleted_task['title']}' deleted!")
                    time.sleep(1.5)
                return
        print(f"\nNo task found with ID {task_id}")
        time.sleep(1.5)
    except ValueError:
        print("Please enter a valid task ID (number).")
        time.sleep(1.5)

def search_tasks():
    """Search for tasks by keyword."""
    display_banner()
    print("=== SEARCH TASKS ===\n")
    
    if not tasks:
        print("No tasks found.")
        input("\nPress Enter to continue...")
        return
    
    keyword = input("Enter search term: ").lower().strip()
    
    if not keyword:
        print("Search term cannot be empty!")
        time.sleep(1.5)
        return
    
    results = []
    for task in tasks:
        if (keyword in task["title"].lower() or 
            (task["description"] and keyword in task["description"].lower())):
            results.append(task)
    
    display_banner()
    print(f"=== SEARCH RESULTS FOR '{keyword}' ===\n")
    
    if not results:
        print("No matching tasks found.")
    else:
        for task in results:
            display_task(task)
    
    input("\nPress Enter to continue...")

def add_note_to_task():
    """Add a note to an existing task."""
    display_banner()
    print("=== ADD NOTE TO TASK ===\n")
    
    if not tasks:
        print("No tasks found.")
        input("\nPress Enter to continue...")
        return
    
    print("Available Tasks:")
    for task in tasks:
        print(f"{task['id']}. {task['title']}")
    
    try:
        task_id = int(input("\nEnter the ID of the task to add a note: "))
        for task in tasks:
            if task["id"] == task_id:
                note = input("Enter your note: ").strip()
                if note:
                    if "notes" not in task:
                        task["notes"] = []
                    task["notes"].append({
                        "content": note,
                        "created_at": datetime.now().isoformat()
                    })
                    if save_tasks():
                        print("\nNote added successfully!")
                else:
                    print("Note cannot be empty!")
                time.sleep(1.5)
                return
                
        print(f"No task found with ID {task_id}")
        time.sleep(1.5)
    except ValueError:
        print("Please enter a valid task ID (number).")
        time.sleep(1.5)

def set_reminder():
    """Set or update a reminder for a task."""
    display_banner()
    print("=== SET REMINDER ===\n")
    
    if not tasks:
        print("No tasks found.")
        input("\nPress Enter to continue...")
        return
    
    print("Available Tasks:")
    for task in tasks:
        existing_reminder = ""
        if task.get("reminder"):
            reminder_time = datetime.fromisoformat(task["reminder"])
            existing_reminder = f" (existing: {reminder_time.strftime('%m/%d %H:%M')})"
        print(f"{task['id']}. {task['title']}{existing_reminder}")
    
    try:
        task_id = int(input("\nEnter the ID of the task to set reminder: "))
        for task in tasks:
            if task["id"] == task_id:
                try:
                    days = int(input("Days from now (0 for today): ") or "0")
                    hours = int(input("Hours from now: ") or "0")
                    reminder_time = datetime.now() + timedelta(days=days, hours=hours)
                    task["reminder"] = reminder_time.isoformat()
                    if save_tasks():
                        print(f"\nReminder set for {reminder_time.strftime('%Y-%m-%d %H:%M')}")
                    time.sleep(1.5)
                    return
                except ValueError:
                    print("Invalid time input. Reminder not set.")
                    time.sleep(1.5)
                    return
                
        print(f"No task found with ID {task_id}")
        time.sleep(1.5)
    except ValueError:
        print("Please enter a valid task ID (number).")
        time.sleep(1.5)

def check_reminders():
    """Check for upcoming or passed reminders."""
    display_banner()
    print("=== REMINDERS ===\n")
    
    if not tasks:
        print("No tasks found.")
        input("\nPress Enter to continue...")
        return
    
    now = datetime.now()
    upcoming_reminders = []
    passed_reminders = []
    
    for task in tasks:
        if task.get("reminder"):
            reminder_time = datetime.fromisoformat(task["reminder"])
            if reminder_time > now:
                time_left = reminder_time - now
                upcoming_reminders.append((task, time_left))
            else:
                passed_reminders.append(task)
    
    if not upcoming_reminders and not passed_reminders:
        print("No reminders set for any tasks.")
        input("\nPress Enter to continue...")
        return
    
    if upcoming_reminders:
        print("\nUPCOMING REMINDERS:")
        for task, time_left in sorted(upcoming_reminders, key=lambda x: x[1]):
            days = time_left.days
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60
            print(f"- {task['title']} (in {days}d {hours}h {minutes}m)")
    
    if passed_reminders:
        print("\nPASSED REMINDERS:")
        for task in passed_reminders:
            reminder_time = datetime.fromisoformat(task["reminder"])
            print(f"- {task['title']} (was due {reminder_time.strftime('%Y-%m-%d %H:%M')})")
    
    input("\nPress Enter to continue...")

def generate_report():
    """Generate a summary report of all tasks."""
    display_banner()
    print("=== TASK REPORT ===\n")
    
    if not tasks:
        print("No tasks found to generate report.")
        input("\nPress Enter to continue...")
        return
    
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task["completed"])
    pending_tasks = total_tasks - completed_tasks
    
    high_priority = sum(1 for task in tasks if task["priority"] == "High")
    high_priority_pending = sum(1 for task in tasks if task["priority"] == "High" and not task["completed"])
    
    tasks_with_notes = sum(1 for task in tasks if task.get("notes"))
    tasks_with_reminders = sum(1 for task in tasks if task.get("reminder"))
    
    print(f"Total Tasks: {total_tasks}")
    print(f"Completed: {completed_tasks} ({int(completed_tasks/total_tasks*100) if total_tasks else 0}%)")
    print(f"Pending: {pending_tasks} ({int(pending_tasks/total_tasks*100) if total_tasks else 0}%)")
    print(f"High Priority: {high_priority} (Pending: {high_priority_pending})")
    print(f"Tasks with notes: {tasks_with_notes}")
    print(f"Tasks with reminders: {tasks_with_reminders}")
    
    # Most recent task
    if tasks:
        sorted_by_date = sorted(tasks, key=lambda x: x["created_at"], reverse=True)
        print(f"\nMost Recent Task: {sorted_by_date[0]['title']} ({datetime.fromisoformat(sorted_by_date[0]['created_at']).strftime('%Y-%m-%d')})")
    
    input("\nPress Enter to continue...")

def display_help():
    """Display help information about how to use the app."""
    display_banner()
    print(f"=== {APP_NAME} HELP ===\n")
    print("This application helps you manage your tasks efficiently.\n")
    
    print("MAIN MENU OPTIONS:")
    print("1. Add Task - Create a new task with title, description, priority, color, notes, and reminder")
    print("2. List Tasks - View all tasks with filtering options")
    print("3. Complete Task - Mark a task as finished")
    print("4. Delete Task - Remove a task from the list")
    print("5. Search - Find tasks by keyword")
    print("6. Add Note - Add a note to an existing task")
    print("7. Set Reminder - Set or update a reminder for a task")
    print("8. Check Reminders - View upcoming and passed reminders")
    print("9. Report - Generate statistics about your tasks")
    print("10. Help - Display this help information")
    print("11. Exit - Close the application\n")
    
    print("TIPS:")
    print("- Use colors to visually categorize tasks")
    print("- Add notes to keep additional information about tasks")
    print("- Set reminders for time-sensitive tasks")
    print("- Check reminders regularly to stay on track")
    
    input("\nPress Enter to continue...")

def main_menu():
    """Display the main menu and handle user choices."""
    load_tasks()
    
    while True:
        display_banner()
        print("1. Add a new task")
        print("2. List all tasks")
        print("3. Mark a task as complete")
        print("4. Delete a task")
        print("5. Search tasks")
        print("6. Add note to task")
        print("7. Set reminder")
        print("8. Check reminders")
        print("9. Generate report")
        print("10. Help")
        print("11. Exit")
        
        choice = input("\nEnter your choice (1-11): ")
        
        if choice == '1':
            add_task()
        elif choice == '2':
            list_tasks()
        elif choice == '3':
            complete_task()
        elif choice == '4':
            delete_task()
        elif choice == '5':
            search_tasks()
        elif choice == '6':
            add_note_to_task()
        elif choice == '7':
            set_reminder()
        elif choice == '8':
            check_reminders()
        elif choice == '9':
            generate_report()
        elif choice == '10':
            display_help()
        elif choice == '11':
            display_banner()
            print(f"Thank you for using {APP_NAME}. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    display_banner()
    print(f"Welcome to {APP_NAME}!")
    print("-" * (len(APP_NAME) + 2))
    main_menu()
