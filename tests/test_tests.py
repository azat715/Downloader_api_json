from datetime import datetime
from os import environ
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from task.main import Downloader
from task.models import Profile, Task, User, SerializeError
from task.views import as_str
from .conftest import FIXTURE_DIR, FAKE_TIME, mocked_requests_get

USERS_URL = "https://jsonplaceholder.typicode.com/users"
TASK_URL = "https://jsonplaceholder.typicode.com/todos"

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

@patch('task.main.requests.get', side_effect=mocked_requests_get)
def test_one(mock_get, tmp_path, patch_datetime_now, res_file):
    main = Downloader(USERS_URL, TASK_URL, tmp_path)
    assert as_str(main.data[0]) == res_file

@pytest.mark.datafiles(FIXTURE_DIR / "Bret.txt")
@patch('task.main.requests.get', side_effect=mocked_requests_get)
def test_two(patch_datetime_now, datafiles):
    main = Downloader(USERS_URL, TASK_URL, datafiles)
    new_file = Path(datafiles.listdir()[0])
    assert new_file.name == "Bret_2020-12-25T17:05.txt"

@patch('task.main.requests.get', side_effect=mocked_requests_get)
def test_error(patch_datetime_now, tmp_path):
    with pytest.raises(Exception):
        main = Downloader("https://non_valid", TASK_URL, tmp_path)  

