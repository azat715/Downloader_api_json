from datetime import datetime
from json import JSONDecodeError
from os import environ
from pathlib import Path

import requests
from requests.exceptions import HTTPError

from task.app_logger import get_logger
from task.models import Profile, SerializeError, Task, User
from task.views import as_str

USERS_URL = "https://jsonplaceholder.typicode.com/users"
TASK_URL = "https://jsonplaceholder.typicode.com/todos"
nl = "\n"
env = environ

logger = get_logger("task")

if env.get("FOLDER"):
    FOLDER = Path(env["FOLDER"])
else:
    FOLDER = Path("tasks2")


class Base:
    def __init__(self):
        self.data = []

    def get(self, url, model):
        logger.info("Загрузка %s", url)
        try:
            r = requests.get(url)
            r.raise_for_status()
            res = [model.from_json(i) for i in r.json()]
        except HTTPError as e:
            logger.warning("При обработке URL %s произошла ошибка \n %s", url, e)
        except (JSONDecodeError, SerializeError) as e:
            logger.warning("При обработке URL %s произошла ошибка \n %s", url, e)
        else:
            return res

    def save_item(self, item, path):
        try:
            with path.open("w", encoding="utf-8") as f:
                f.write(as_str(item))
        except EnvironmentError as e:
            logger.warning("При записи файла %s произошла ошибка \n %s", path, e)


class Downloader(Base):
    def __init__(self, user_url, task_url, folder):
        super().__init__()
        self.folder = Path(folder)
        self._create_folder()
        try:
            self.get_data(user_url, task_url)
            for profile in self.data:
                self.save(profile)
        except Exception as e:
            raise Exception from e

    def save(self, profile):
        p = self.folder.joinpath(profile.user.username).with_suffix(".txt")
        if p.exists():
            date = self._get_date(p)
            self._rename(p, date)
        self.save_item(profile, p)

    def get_data(self, user_url, task_url):
        users = self.get(user_url, User)
        tasks = self.get(task_url, Task)
        for user in users:
            self.data.append(
                Profile(user, [task for task in tasks if task.user_id == user.id_])
            )

    def _create_folder(self):
        try:
            self.folder.mkdir()
        except FileExistsError:
            logger.info("Каталог %s существует", self.folder)
        else:
            logger.info("Каталог %s создан", self.folder)

    def _get_date(self, path):
        with path.open() as f:
            first_line = f.readline()
            date_string = " ".join(first_line.split()[-2:])
            dt = datetime.strptime(date_string, "%d.%m.%y %H:%M")
            return dt.isoformat(timespec="minutes")

    def _rename(self, path, date):
        new_filename = path.stem + "_" + date
        new_path = Path(path.parent / new_filename)
        path.rename(new_path.with_suffix(".txt"))
        logger.info("Файл %s переименован", path)


def cli():
    logger.info("Запуск")
    Downloader(USERS_URL, TASK_URL, FOLDER)
