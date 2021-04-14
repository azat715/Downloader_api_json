import json
from datetime import datetime
from json import JSONDecodeError
from os import environ
from pathlib import Path

import requests
from requests.exceptions import HTTPError

from task.models import Profile, Task, User, SerializeError
from task.views import as_str
from task.app_logger import get_logger

USERS_URL = "https://jsonplaceholder.typicode.com/users"
TASK_URL = "https://jsonplaceholder.typicode.com/todos"
nl = "\n"
env = environ

logger = get_logger("task")

BASE_DIR = Path(__file__).resolve().parent

if env.get("FOLDER"):
    FOLDER = Path(env["FOLDER"])
else:
    FOLDER = BASE_DIR.joinpath("tasks2")

class Base:
    def __init__(self):
        self.data = []

    def get(self, url, model):
        logger.info(f"Загрузка {url}")
        try:
            r = requests.get(url)
            r.raise_for_status()
            res = [model.from_json(i) for i in r.json()]
        except HTTPError as e:
            logger.warning(f"""При обработке URL {url} произошла ошибка 
{e}""")
        except JSONDecodeError as e:
            logger.warning(f"""При обработке URL {url} произошла ошибка 
{e}""")
        except SerializeError as e:
            logger.warning(f"""При обработке URL {url} произошла ошибка 
{e}""")
        else:
            return res

    def save_item(self, item, path):
        try:
            with path.open("w", encoding="utf-8") as f:
                f.write(as_str(item))
        except EnvironmentError as e:
            logger.warning(f"""При записи файла {p} произошла ошибка 
{e}""")


class Downloader(Base):
    def __init__(self, user_url, task_url, folder):
        super().__init__()
        self.folder = Path(folder)
        self._create_folder()
        try:
            self.get_data(user_url, task_url)
            for profile in self.data:
                self.save(profile)
        except:
            raise Exception

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
        except FileExistsError as e:
            logger.info(f"Каталог {self.folder} существует")
        else:
            logger.info(f"Каталог {self.folder} создан")

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
        logger.info(f"Файл {path} переименован")


def cli():
    logger.info("Запуск")
    Downloader(USERS_URL, TASK_URL, FOLDER)
