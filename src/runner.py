import asyncio
import logging
import asyncssh

from src.config import settings
from src.schema import Playbook, Task, TaskStatus


async def run_playbook(
    semaphore: asyncio.Semaphore,
    playbook: list[Playbook],
    username: str,
) -> None:
    tasks = []
    for play in playbook:
        for address in play.addresses:
            for task in play.tasks:
                tasks.append(
                    run_remote_task(
                        semaphore=semaphore,
                        current_user=username,
                        host=address,
                        task=task,
                    )
                )
    await asyncio.gather(*tasks)


async def run_remote_task(
    semaphore: asyncio.Semaphore, current_user: str, host: str, task: Task
) -> None:
    try:
        async with semaphore:
            async with asyncssh.connect(
                host=host,
                username=current_user,
                login_timeout=settings.TIMEOUT,
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
        logging.error(f"Connection error for {host}. Error: {e}", exc_info=True)
