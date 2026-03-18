import sys
import asyncio
import logging
import getpass

from src.config import settings
from src.parser import read_file, get_playbook_hosts
from src.runner import run_playbook


async def main():
    playbook_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not playbook_path:
        logging.error("No input provided. Usage: python main.py <playbook.yaml>")
        return
    tasks = [
        read_file(playbook_path),
        read_file(settings.HOSTS),
    ]
    playbook_content, hosts_content = await asyncio.gather(*tasks)
    playbook_data = get_playbook_hosts(playbook_content, hosts_content)

    current_user = getpass.getuser()
    semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_TASKS)
    try:
        await asyncio.wait_for(
            run_playbook(
                semaphore=semaphore, playbook=playbook_data, username=current_user
            ),
            timeout=settings.GLOBAL_TIMEOUT,
        )
        logging.info("\nPlaybook execution finished.")
    except asyncio.TimeoutError:
        logging.critical(
            (
                f"\nGlobal timeout of {settings.GLOBAL_TIMEOUT} seconds has been reached! "
                "Some tasks were still running and have been cancelled."
            )
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExecution interrupted by user. Exiting...")
