from pydantic import BaseModel
from enum import StrEnum


class HostType(StrEnum):
    """Defines the supported categories of remote infrastructure, such as web or database servers. Can and should be extended."""

    WEB_SERVER = "webservers"
    DB_SERVER = "dbservers"


class TaskStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Task(BaseModel):
    """A data model representing a single remote operation consisting of a descriptive name and a bash command."""

    name: str
    bash: str


class PlaybookIn(BaseModel):
    """The raw structure of a playbook as defined in YAML, mapping a host group to a sequence of tasks."""

    hosts: HostType
    tasks: list[Task]


class Playbook(PlaybookIn):
    """The final execution model that extends the base playbook with a resolved list of specific IP addresses."""

    addresses: list[str]
