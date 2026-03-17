from pydantic import BaseModel
from enum import StrEnum


class HostType(StrEnum):
    WEB_SERVER = "webservers"
    DB_SERVER = "dbservers"


class TaskStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Task(BaseModel):
    name: str
    bash: str


class PlaybookIn(BaseModel):
    hosts: HostType
    tasks: list[Task]


class Playbook(PlaybookIn):
    addresses: list[str]
