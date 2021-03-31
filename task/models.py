from __future__ import annotations

from collections import UserList
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

nl = "\n"


class SerializeError(Exception):
    def __init__(self, field):
        super().__init__()
        self.field = field

    def __str__(self):
        return f"""Error отсутствуeт полe: {self.field}"""


@dataclass
class User:
    id_: int
    name: str
    username: str
    email: str
    company_name: str
    date: datetime = field(init=False)

    def __post_init__(self):
        self.date = datetime.now().strftime("%d.%m.%y %H:%M")

    @classmethod
    def from_json(cls, obj) -> User:
        try:
            id_ = obj["id"]
            name = obj["name"]
            username = obj["username"]
            email = obj["email"]
            company_name = obj["company"]["name"]
        except KeyError as e:
            raise SerializeError(e.args)
        else:
            return User(id_, name, username, email, company_name)

    def __repr__(self):
        return "User({self.id_}, {self.name}, {self.username}, {self.email}, {self.company_name}, {self.date})".format(
            self=self
        )


@dataclass
class Task:
    user_id: int
    id_: int
    title: str
    completed: bool

    @classmethod
    def from_json(cls, obj) -> Task:
        try:
            user_id = obj["userId"]
            id_ = obj["id"]
            title = obj["title"]
            completed = obj["completed"]
        except KeyError as e:
            raise SerializeError(e.args)
        else:
            return Task(user_id, id_, title, completed)

    def __repr__(self):
        return (
            "Task({self.user_id}, {self.id_}, {self.title}, {self.completed})".format(
                self=self
            )
        )


@dataclass
class Profile:
    user: User
    tasks: List[Task] = field(default_factory=list)

    @property
    def completed(self) -> List[Task]:
        return [i for i in self.tasks if i.completed is True]

    def tasks_str(self, tasks) -> str:
        strings = []
        for task in tasks:
            strings.append(self.prune(task.title))
        if len(strings) == 0:
            return "Нет задач"
        return nl.join(strings)

    @property
    def uncompleted(self) -> List[Task]:
        return [i for i in self.tasks if i.completed is False]

    def prune(self, string):
        if len(string) > 50:
            return f"{string[:50]}..."
        return string

    def __str__(self):
        return f"""{self.user.name} <{self.user.email}> {self.user.date}
{self.user.company_name}

Завершённые задачи:
{self.tasks_str(self.completed)}

Оставшиеся задачи:
{self.tasks_str(self.uncompleted)}
"""
