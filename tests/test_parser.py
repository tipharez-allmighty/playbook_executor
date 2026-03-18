from src.schema import HostType
from src.parser import _parse_playbook, _parse_hosts


def test_playbook_parser(mock_yaml):
    result = _parse_playbook(mock_yaml)
    assert HostType.WEB_SERVER in result
    assert HostType.DB_SERVER in result


def test_hosts_parser(mock_hosts, mock_yaml):
    playbook_dict = _parse_playbook(mock_yaml)
    result = _parse_hosts(mock_hosts, playbook_dict)
    web_addresses = result[HostType.WEB_SERVER].addresses
    web_addresses_tasks = result[HostType.WEB_SERVER].tasks
    host_types = playbook_dict.keys()
    assert len(web_addresses) == 1
    assert len(web_addresses_tasks) == 2
    assert len(host_types) <= len(HostType.__members__)
