from __future__ import annotations

from collections import UserList
from dataclasses import dataclass, field
from datetime import datetime
from typing import List




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

    def __post_init__(self) -> datetime:
        self.date = datetime.now()

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

    @property
    def uncompleted(self) -> List[Task]:
        return [i for i in self.tasks if i.completed is False]

