import json
from pathlib import Path
from datetime import datetime

import pytest

BASE_DIR = Path(__file__).resolve().parent

FIXTURE_DIR = BASE_DIR.joinpath("test_files")


FAKE_TIME = datetime(2020, 12, 25, 17, 5, 55)

@pytest.fixture
def patch_datetime_now(monkeypatch):

    class mydatetime:
        @classmethod
        def now(cls):
            return FAKE_TIME

    monkeypatch.setattr('task.models.datetime', mydatetime)


@pytest.fixture
def patch_datetime_now_future(monkeypatch):

    class mydatetime:
        @classmethod
        def now(cls):
            return FAKE_TIME + timedelta(hours=1)

    monkeypatch.setattr('task.models.datetime', mydatetime)


@pytest.fixture()
def setup_folder(monkeypatch, tmpdir_factory):
    temp_dir = tmpdir_factory.mktemp("temp")
    monkeypatch.setenv("FOLDER", str(temp_dir))
    yield
    monkeypatch.delenv("FOLDER")

@pytest.fixture()
def users():
    return json.loads(
        """
    [
      {
        "id": 1,
        "name": "Leanne Graham",
        "username": "Bret",
        "email": "Sincere@april.biz",
        "address": {
          "street": "Kulas Light",
          "suite": "Apt. 556",
          "city": "Gwenborough",
          "zipcode": "92998-3874",
          "geo": {
            "lat": "-37.3159",
            "lng": "81.1496"
          }
        },
        "phone": "1-770-736-8031 x56442",
        "website": "hildegard.org",
        "company": {
          "name": "Romaguera-Crona",
          "catchPhrase": "Multi-layered client-server neural-net",
          "bs": "harness real-time e-markets"
        }
      }
    ]
    """
    )


@pytest.fixture()
def users_error():
    return json.loads(
        """
    [
      {
        "id": 1,
        "err": "Leanne Graham",
        "username": "Bret",
        "email": "Sincere@april.biz",
        "address": {
          "street": "Kulas Light",
          "suite": "Apt. 556",
          "city": "Gwenborough",
          "zipcode": "92998-3874",
          "geo": {
            "lat": "-37.3159",
            "lng": "81.1496"
          }
        },
        "phone": "1-770-736-8031 x56442",
        "website": "hildegard.org",
        "company": {
          "name": "Romaguera-Crona",
          "catchPhrase": "Multi-layered client-server neural-net",
          "bs": "harness real-time e-markets"
        }
      }
    ]
    """
    )


@pytest.fixture()
def tasks():
    return json.loads(
        """
  [
    {
      "userId": 1,
      "id": 1,
      "title": "delectus aut autem",
      "completed": false
    },
    {
      "userId": 1,
      "id": 2,
      "title": "quis ut nam facilis et officia qui",
      "completed": false
    },
    {
      "userId": 1,
      "id": 3,
      "title": "fugiat veniam minus",
      "completed": false
    },
    {
      "userId": 1,
      "id": 4,
      "title": "et porro tempora",
      "completed": true
    }
  ]
  """
    )

@pytest.fixture()
def res_file():
  return f"""Leanne Graham <Sincere@april.biz> 25.12.20 17:05
Romaguera-Crona

Завершённые задачи:
et porro tempora

Оставшиеся задачи:
delectus aut autem
quis ut nam facilis et officia qui
fugiat veniam minus
"""