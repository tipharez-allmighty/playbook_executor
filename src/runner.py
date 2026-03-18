import asyncio
import logging

import asyncssh

from src.config import settings
from src.schema import HostType, Playbook, Task, TaskStatus


async def run_playbook(
    semaphore: asyncio.Semaphore,
    playbook: dict[HostType, Playbook],
    username: str,
) -> None:
    """Executes all tasks across all hosts defined in the playbook."""
    tasks = []
    for play in playbook.values():
        for address in play.addresses:
            for task in play.tasks:
                tasks.append(
                    run_remote_task(
                        semaphore=semaphore,
                        current_user=username,
                        address=address,
                        task=task,
                    )
                )
    await asyncio.gather(*tasks)


async def run_remote_task(
    semaphore: asyncio.Semaphore, current_user: str, address: str, task: Task
) -> None:
    """Connects to a remote host via SSH and executes a task within the provided concurrency limit."""
    try:
        host, port = _get_host_and_port(address)
        async with semaphore:
            async with asyncssh.connect(
                host=host,
                port=port,
                username=current_user,
                login_timeout=settings.TASK_TIMEOUT,
                known_hosts=settings.SSH_KNOWN_HOSTS_FILE
                if settings.SSH_KNOWN_HOSTS_FILE
                else None,
            ) as conn:
                result = await conn.run(task.bash, check=False)

                output = None
                status = TaskStatus.FAILED
                if result.exit_status == 0:
                    output = result.stdout
                    status = TaskStatus.SUCCESS
                else:
                    output = result.stderr
                if output:
                    for line in output.strip().splitlines():
                        clean_line = str(line).replace("\t", " ")
                        logging.info(
                            f"[{status} | {host} | Task: {task.name}] | {clean_line}"
                        )
    except Exception as e:
        logging.error(f"Connection error for {address}. Error: {e}")


def _get_host_and_port(address: str) -> tuple[str, int]:
    """Parses a string address into a host and port tuple, defaulting to port 22."""
    address_parts = address.strip().split(":")
    host = address_parts[0]
    port = int(address_parts[1]) if len(address_parts) > 1 else 22
    return host, port
