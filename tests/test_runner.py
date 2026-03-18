import asyncio
from unittest.mock import AsyncMock, patch
import pytest

from src.runner import run_playbook


@pytest.mark.asyncio
async def test_run_playbook_logic(playbook_data):
    semaphore = asyncio.Semaphore(10)
    expected_calls = sum(
        len(play.addresses) * len(play.tasks) for play in playbook_data.values()
    )
    with patch("src.runner.asyncssh.connect", new_callable=AsyncMock) as mock_connect:
        await run_playbook(semaphore, playbook_data, "admin")
        assert mock_connect.call_count == expected_calls
