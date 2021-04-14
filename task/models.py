from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


class SerializeError(Exception):
    def __init__(self, field_):
        super().__init__()
        self.field_ = field_

    def __str__(self):
        return f"""Error отсутствуeт полe: {self.field_}"""


class ValidateError(Exception):
    def __init__(self, user, task):
        super().__init__()
        self.user = user
        self.task = task

    def __str__(self):
        return """Error ошибка валидации: Не соотвествует id пользователя id задачи"""


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
            raise SerializeError(e.args) from e
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
            raise SerializeError(e.args) from e
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

    def __post_init__(self):
        self._validate()

    def _validate(self):
        for task in self.tasks:
            if task.user_id != self.user.id_:
                raise ValidateError(self.user, task)

    def is_valid(self):
        try:
            self._validate()
        except ValidateError:
            return False
        else:
            return True
