import json
import os

def migrate():
    if not os.path.exists("tasks.json"):
        print("no tasks.json found")
        return

    with open("tasks.json", "r") as f:
        old_tasks = json.load(f)

    new_tasks = {}

    for task in old_tasks:
        text = task["text"]
        date = task["date"]
        done = task["done"]

        if text not in new_tasks:
            new_tasks[text] = {
                "text": text,
                "done": done,
                "created": date,
                "history": [date]
            }
        else:
            if date not in new_tasks[text]["history"]:
                new_tasks[text]["history"].append(date)
            if done:
                new_tasks[text]["done"] = True

    result = list(new_tasks.values())

    with open("tasks.json", "w") as f:
        json.dump(result, f, indent=4)

    print(f"migrated {len(result)} tasks")

migrate()