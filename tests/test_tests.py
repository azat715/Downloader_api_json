from datetime import datetime
from os import environ
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from task.main import Downloader
from task.models import Profile, SerializeError, Task, User, ValidateError
from task.views import as_str

from .conftest import FAKE_TIME, FIXTURE_DIR, mocked_requests_get

USERS_URL = "https://jsonplaceholder.typicode.com/users"
TASK_URL = "https://jsonplaceholder.typicode.com/todos"


def test_profile(users, tasks, patch_datetime_now):
    user = User.from_json(users[0])
    assert user.id_ == 1
    assert user.name == "Leanne Graham"
    assert user.username == "Bret"
    assert user.email == "Sincere@april.biz"
    assert user.company_name == "Romaguera-Crona"
    assert user.date == FAKE_TIME
    task1 = Task.from_json(tasks[0])
    assert task1.user_id == 1
    assert task1.id_ == 1
    assert task1.title == "delectus aut autem"
    assert task1.completed == False
    task2 = Task.from_json(tasks[3])
    profile = Profile(user, [task1, task2])
    print(profile.uncompleted)
    uncompleted = len(profile.uncompleted)
    assert uncompleted == 1
    completed = len(profile.completed)
    assert completed == 1
    with pytest.raises(ValidateError):
        task1.user_id = 2
        profile = Profile(user, [task1, task2])
    error_users = users
    error_users[0]["err"] = error_users[0].pop("name")
    with pytest.raises(SerializeError):
        user = User.from_json(error_users[0])


@patch("task.main.requests.get", side_effect=mocked_requests_get)
def test_one(mock_get, tmp_path, patch_datetime_now, res_file):
    main = Downloader(tmp_path)
    main.get_data(USERS_URL, TASK_URL)
    assert as_str(main.data[0]) == res_file


@pytest.mark.datafiles(FIXTURE_DIR / "Bret.txt")
@patch("task.main.requests.get", side_effect=mocked_requests_get)
def test_two(patch_datetime_now, datafiles):
    main = Downloader(datafiles)
    main.get_data(USERS_URL, TASK_URL)
    main.save()
    new_file = Path(datafiles.listdir()[0])
    assert new_file.name == "Bret_2020-12-25T17:05.txt"


@patch("task.main.requests.get", side_effect=mocked_requests_get)
def test_error(patch_datetime_now, tmp_path):
    with pytest.raises(Exception):
        main = Downloader(tmp_path)
        main.get_data("https://non_valid", TASK_URL)
