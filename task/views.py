nl = "\n"


def prune(string):
    if len(string) > 50:
        return f"{string[:50]}..."
    return string


def tasks_str(tasks):
    strings = []
    for task in tasks:
        strings.append(prune(task.title))
    if len(strings) == 0:
        return "Нет задач"
    return nl.join(strings)


def as_str(profile):
    user = profile.user
    completed = tasks_str(profile.completed)
    uncompleted = tasks_str(profile.uncompleted)
    return f"""{user.name} <{user.email}> {user.date.strftime("%d.%m.%y %H:%M")}
{user.company_name}

Завершённые задачи:
{completed}

Оставшиеся задачи:
{uncompleted}
"""
