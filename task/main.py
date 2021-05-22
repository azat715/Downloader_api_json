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

FOLDER = Path("tasks2")

class Downloader():
    def __init__(self, folder):
        self.data = []
        self.folder = Path(folder)
        self._create_folder()

    def get(self, url, model):
        logger.info("Загрузка %s", url)
        try:
            r = requests.get(url)
            r.raise_for_status()
            res = [model.from_json(i) for i in r.json()]
        except (JSONDecodeError, SerializeError, HTTPError) as e:
            logger.warning("При обработке URL %s произошла ошибка \n %s", url, e)
            raise Exception from e
        else:
            return res

    def save(self):
        for profile in self.data:
            try:
                p = self.folder.joinpath(profile.user.username).with_suffix(".txt")
                if p.exists():
                    date = self._get_date(p)
                    self._rename(p, date)
                with p.open("w", encoding="utf-8") as f:
                    f.write(as_str(profile))
            except EnvironmentError as e:
                logger.warning("При записи файла %s произошла ошибка \n %s", p, e)

    
    def users(self, url, model):
        return self.get(url, model)

    def tasks(self, url, model):
        return self.get(url, model)

    def get_data(self, user_url, task_url):
        users = self.users(user_url, User)
        tasks = self.tasks(task_url, Task)
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
    main = Downloader(FOLDER)
    main.get_data(USERS_URL, TASK_URL)
    main.save()
