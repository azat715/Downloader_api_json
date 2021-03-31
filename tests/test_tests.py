from datetime import datetime
from os import environ
from pathlib import Path

import pytest

from task.main import Downloader
from task.models import Profile, Task, User, SerializeError
from task.views import as_str
from .conftest import FIXTURE_DIR, FAKE_TIME

def test_user(users, patch_datetime_now):
    user = User.from_json(users[0])
    assert user.id_ == 1
    assert user.name == "Leanne Graham"
    assert user.username == "Bret"
    assert user.email == "Sincere@april.biz"
    assert user.company_name == "Romaguera-Crona"
    assert user.date == FAKE_TIME
    

def test_task(tasks):
    task = Task.from_json(tasks[0])
    assert task.user_id == 1
    assert task.id_ == 1
    assert task.title == "delectus aut autem"
    assert task.completed == False


def test_one(mocker, users, tasks, tmp_path, patch_datetime_now, res_file):
    mocker.patch("task.main.Downloader._get", side_effect=[users, tasks])
    main = Downloader("test", "test", tmp_path)
    assert as_str(main.profiles[0]) == res_file

@pytest.mark.datafiles(FIXTURE_DIR / "Bret.txt")
def test_two(mocker, users, tasks, patch_datetime_now, res_file, datafiles):
    mocker.patch("task.main.Downloader._get", side_effect=[users, tasks])
    main = Downloader("test", "test", datafiles)
    new_file = Path(datafiles.listdir()[0])
    assert new_file.name == "Bret_2020-12-25T17:05.txt"


def test_error(mocker, users_error, tasks, tmp_path, patch_datetime_now):
    mocker.patch("task.main.Downloader._get", side_effect=[users_error, tasks])
    with pytest.raises(Exception):
        main = Downloader("test", "test", tmp_path)
    

