import pytest
import os
import shutil

from aeris.tools.computer.mouse import MouseTool
from aeris.tools.computer.keyboard import KeyboardTool
from aeris.tools.computer.fs import FileSystemTool
from aeris.tools.computer.browser import BrowserTool
from aeris.tools.computer.command import CommandTool

from aeris.tools.security import kill_switch
from aeris.config.settings import settings


# Test environment setup
@pytest.fixture(autouse=True)
def setup_test_env():
    # Make sure we're always in dry run during tests unless testing specific behavior
    original_dry_run = settings.dry_run
    settings.dry_run = True

    # Setup test workspace
    test_dir = os.path.join(os.getcwd(), "test_workspace")
    os.makedirs(test_dir, exist_ok=True)
    original_allowed = settings.allowed_paths
    settings.allowed_paths = [test_dir]

    yield

    # Teardown
    settings.dry_run = original_dry_run
    settings.allowed_paths = original_allowed
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_mouse_tool_dry_run():
    tool = MouseTool()
    result = await tool.execute(action="move", x=100, y=100)
    assert result.success is True
    assert "[DRY RUN]" in result.result


@pytest.mark.asyncio
async def test_keyboard_tool_dry_run():
    tool = KeyboardTool()
    result = await tool.execute(action="type", text="hello")
    assert result.success is True
    assert "[DRY RUN]" in result.result


@pytest.mark.asyncio
async def test_fs_tool_allowed_paths():
    tool = FileSystemTool()

    # Outside allowed path
    result = await tool.execute(action="read", path="C:/Windows/System32/config/SAM")
    assert result.success is False
    assert "not in allowed_paths" in result.error

    # Inside allowed path
    test_file = os.path.join(settings.allowed_paths[0], "test.txt")
    result = await tool.execute(action="write", path=test_file, content="test")
    assert (
        result.success is True
    )  # It's in dry run, so it succeeds the path check and returns dry run message
    assert "[DRY RUN]" in result.result


@pytest.mark.asyncio
async def test_command_tool_allowlist():
    tool = CommandTool()

    # Not in allowlist
    result = await tool.execute(action="execute", command="rm -rf /")
    assert result.success is False
    assert "not in the allowlist" in result.error

    # In allowlist
    # Temporarily add 'echo' if not present
    original_allowlist = settings.command_allowlist
    settings.command_allowlist = ["echo"]

    result = await tool.execute(action="execute", command="echo hello")
    assert result.success is True
    assert "[DRY RUN]" in result.result

    settings.command_allowlist = original_allowlist


@pytest.mark.asyncio
async def test_kill_switch_blocks_execution():
    tool = MouseTool()

    # Enable kill switch
    kill_switch.activate()
    assert kill_switch.is_active is True

    # Attempt execution
    result = await tool.execute(action="move", x=100, y=100)

    # Should be blocked
    assert result.success is False
    assert result.error == "Blocked"

    # Reset kill switch
    kill_switch.reset()


@pytest.mark.asyncio
async def test_browser_url_validation():
    # Make sure kill switch is off
    kill_switch.reset()

    tool = BrowserTool()

    # Safe scheme
    result = await tool.execute(action="open", url="https://google.com")
    assert result.success is True

    # Unsafe scheme
    result = await tool.execute(
        action="open", url="file:///C:/Windows/System32/cmd.exe"
    )
    assert result.success is False
    assert "Invalid or unsafe URL scheme" in result.error
