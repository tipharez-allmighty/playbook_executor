from pydantic import BaseModel
from enum import StrEnum


class HostType(StrEnum):
    """Defines the categories of remote infrastructure. Can and should be extended."""

    WEB_SERVER = "webservers"
    DB_SERVER = "dbservers"


class TaskStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Task(BaseModel):
    """Represents a remote operation with a name and a bash command."""

    name: str
    bash: str


class PlaybookBase(BaseModel):
    """Maps a host group to a sequence of tasks from YAML input."""

    hosts: HostType
    tasks: list[Task]


class Playbook(PlaybookBase):
    """Adds a resolved list of IP addresses to the base playbook."""

    addresses: list[str]
