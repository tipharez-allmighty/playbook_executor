import pytest

from src.schema import HostType, Task, Playbook


@pytest.fixture
def mock_yaml():
    return """
- hosts: webservers
  tasks:
    - name: Server uptime
      bash: uptime
    - name: Server disk usage
      bash: du -h
- hosts: dbservers
  tasks:
    - name: Server uptime
      bash: uptime
"""


@pytest.fixture
def mock_hosts():
    return """
    # This is a comment
    [webservers]
    192.168.1.1
    192.168.1.1

    [dbservers]
    192.168.1.2

    [unknown_group]
    10.0.0.1
    """


@pytest.fixture
def playbook_data():
    """Provides a standard playbook with 1 group, 2 hosts, and 2 tasks."""
    return {
        HostType.WEB_SERVER: Playbook(
            hosts=HostType.WEB_SERVER,
            tasks=[Task(name="Task 1", bash="uptime"), Task(name="Task 2", bash="ls")],
            addresses=["1.1.1.1", "2.2.2.2"],
        )
    }
