import logging
import yaml

import aiofiles

from src.schema import PlaybookIn, Playbook, HostType


async def read_file(path: str) -> str:
    try:
        async with aiofiles.open(path, "r") as file:
            content = await file.read()
    except Exception as e:
        logging.error(f"Error opening file at {path}: {e}", exc_info=True)
        raise e
    return content


def get_playbook_hosts(playbook_content: str, hosts_content: str) -> list[Playbook]:
    playbook_dict = _parse_playbook(playbook_content)
    playbook_hosts = _parse_hosts(hosts_content, playbook_dict)
    return playbook_hosts


def _parse_playbook(content: str) -> dict[HostType, PlaybookIn]:
    playbook: dict[HostType, PlaybookIn] = {}
    playbook_dict = yaml.safe_load(content)
    for item in playbook_dict:
        playbook_item = PlaybookIn.model_validate(item)
        playbook[playbook_item.hosts] = playbook_item

    return playbook


def _parse_hosts(
    content: str, playbook_dict: dict[HostType, PlaybookIn]
) -> list[Playbook]:
    lines = content.splitlines()
    result_playbook: list[Playbook] = []
    current_hosts_group: HostType | None = None
    for line in lines:
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("#"):
            continue
        if clean_line.startswith("[") and clean_line.endswith("]"):
            try:
                host_type = HostType(clean_line[1:-1])
            except ValueError:
                logging.warning(f"Host type {clean_line[1:-1]} is not supported yet.")
                current_hosts_group = None
                continue
            if host_type in playbook_dict:
                current_hosts_group = host_type
            else:
                current_hosts_group = None
        else:
            host_address = clean_line
            playbook_item = (
                playbook_dict.get(current_hosts_group) if current_hosts_group else None
            )
            if current_hosts_group is None or playbook_item is None:
                continue
            if not result_playbook or result_playbook[-1].hosts != current_hosts_group:
                result_playbook.append(
                    Playbook(**playbook_item.model_dump(), addresses=[host_address])
                )
            else:
                result_playbook[-1].addresses.append(host_address)
    if not result_playbook:
        logging.error(
            "No execution plan created. Check if your hosts file groups "
            "match the 'hosts' keys in your playbook YAML."
        )
    return result_playbook
