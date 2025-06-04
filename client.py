import requests

BASE_URL = "http://127.0.0.1:8009"

def menu():
    print("\nTo-Do List Menu:")
    print("1. Add Task")
    print("2. View All Tasks")
    print("3. View Task by ID")
    print("4. Update Task")
    print("5. Delete Task")
    print("6. Filter by Status")
    print("7. Filter by Due Date")
    print("8. Search Tasks")
    print("9. Exit")

def add_task():
    title = input("Title: ")
    description = input("Description: ")
    status = input("Status (pending/completed): ")
    due_date = input("Due Date (YYYY-MM-DD or leave blank): ")
    priority = input("Priority (low/medium/high): ")

    data = {
        "title": title,
        "description": description,
        "status": status,
        "due_date": due_date or None,
        "priority": priority
    }

    response = requests.post(f"{BASE_URL}/tasks/", json=data)
    print("Response:", response.status_code, response.json())

def view_all_tasks():
    response = requests.get(f"{BASE_URL}/tasks/")
    print("Tasks:", response.json())

def view_task_by_id():
    task_id = input("Enter Task ID: ")
    response = requests.get(f"{BASE_URL}/tasks/{task_id}")
    print("Task:", response.json())

def update_task():
    task_id = input("Enter Task ID to update: ")
    print("Leave field empty to skip update")
    title = input("New Title: ")
    description = input("New Description: ")
    status = input("New Status (pending/completed): ")
    due_date = input("New Due Date (YYYY-MM-DD): ")
    priority = input("New Priority (low/medium/high): ")

    data = {}
    if title: data["title"] = title
    if description: data["description"] = description
    if status: data["status"] = status
    if due_date: data["due_date"] = due_date
    if priority: data["priority"] = priority

    response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=data)
    print("Updated Task:", response.json())

def delete_task():
    task_id = input("Enter Task ID to delete: ")
    response = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    print("Deleted (204 expected):", response.status_code)

def filter_by_status():
    status = input("Enter status (pending/completed): ")
    response = requests.get(f"{BASE_URL}/tasks/status/{status}")
    print("Filtered Tasks:", response.json())

def filter_by_due_date():
    due_date = input("Enter Due Date (YYYY-MM-DD): ")
    response = requests.get(f"{BASE_URL}/tasks/due/{due_date}")
    print("Tasks due on date:", response.json())

def search_tasks():
    query = input("Enter search query: ")
    print("Enter Either Title or Description")
    response = requests.get(f"{BASE_URL}/tasks/search/?query={query}")
    print("Search Results:", response.json())

# Main loop
if __name__ == "__main__":
    while True:
        menu()
        choice = input("Choose an option: ")
        match choice:
            case "1": add_task()
            case "2": view_all_tasks()
            case "3": view_task_by_id()
            case "4": update_task()
            case "5": delete_task()
            case "6": filter_by_status()
            case "7": filter_by_due_date()
            case "8": search_tasks()
            case "9": break
            case _: print("Invalid choice. Try again.")
