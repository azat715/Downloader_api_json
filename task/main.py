import json
from datetime import datetime
from json import JSONDecodeError
from os import environ
from pathlib import Path

import requests
from requests.exceptions import HTTPError

from task.models import Profile, Task, User, SerializeError
from task.app_logger import get_logger

USERS_URL = "https://jsonplaceholder.typicode.com/users"
TASK_URL = "https://jsonplaceholder.typicode.com/todos"
nl = "\n"
env = environ

logger = get_logger("task")

if env.get("FOLDER"):
    FOLDER = Path(env["FOLDER"])
else:
    BASE_DIR = Path(__file__).resolve().parent
    FOLDER = BASE_DIR.joinpath("tasks2")


class Downloader:
    def __init__(self, user_url, task_url, folder):
        self.folder = Path(folder)
        self._create_folder()
        try:
            self.profiles = self._get_profiles(user_url, task_url)
        except:
            raise Exception
        for profile in self.profiles:
            p = self.folder.joinpath(profile.user.username).with_suffix(".txt")
            if p.exists():
                date = self._get_date(p)
                self._rename(p, date)
            try:
                with p.open("w", encoding="utf-8") as f:
                    f.write(str(profile))
            except EnvironmentError as e:
                logger.warning(f"""При записи файла {p} произошла ошибка 
{e}""")
        logger.info("Конец")

    def _get(self, url):
        logger.info(f"Загрузка {url}")
        try:
            r = requests.get(url)
            r.raise_for_status()
            res = r.json()
        except HTTPError as e:
            logger.warning(f"""При обработке URL {url} произошла ошибка 
{e}""")
        except JSONDecodeError as e:
            logger.warning(f"""При обработке URL {url} произошла ошибка 
{e}""")
        else:
            return res

    def _users(self, url):
        obj = self._get(url)
        return [User.from_json(i) for i in obj]

    def _tasks(self, url):
        obj = self._get(url)
        return [Task.from_json(i) for i in obj]

    def _get_profiles(self, user_url, task_url):
        profiles = []
        try:
            users = self._users(user_url)
        except SerializeError as e:
            logger.warning(f"""При обработке URL {user_url} произошла ошибка 
{e}""")
        try:
            tasks = self._tasks(task_url)
        except SerializeError as e:
            logger.warning(f"""При обработке URL {task_url} произошла ошибка 
{e}""")
        for user in users:
            profiles.append(
                Profile(user, [task for task in tasks if task.user_id == user.id_])
            )
        return profiles

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
