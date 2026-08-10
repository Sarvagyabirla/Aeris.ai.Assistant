import pytest
import os
import json
from google.genai.types import FunctionCall
from aeris.core.agent import AerisAgent
from aeris.core.conversation import Conversation
from aeris.core.context import ContextManager
from aeris.tools.registry import ToolRegistry
from aeris.ai.types import AIResponse
from aeris.flows.coding import CodingFlow
from aeris.tools.computer.fs import FileSystemTool
from aeris.config.settings import settings


class MockProvider:
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0

    async def send_message(self, request):
        if self.call_count < len(self.responses):
            resp = self.responses[self.call_count]
            self.call_count += 1
            return resp
        return AIResponse(content="Default mock response")


@pytest.fixture
def workflow_setup():
    original_dry_run = settings.dry_run
    settings.dry_run = False  # Physically execute tools
    yield
    settings.dry_run = original_dry_run


@pytest.mark.asyncio
async def test_coding_workflow_physical_write(tmp_path, workflow_setup):
    """
    Test a real-world workflow:
    1. Enter CodingFlow.
    2. Agent is asked to write a Python script.
    3. Agent calls FileSystemTool to write physical file.
    4. Verify file was written.
    """
    conversation = Conversation()
    context_manager = ContextManager(conversation)
    tool_registry = ToolRegistry()
    
    # Add real FileSystemTool
    tool_registry.register(FileSystemTool())
    
    target_file = tmp_path / "hello.py"
    
    # Pre-configure the allowed paths to allow writing to tmp_path
    original_paths = settings.allowed_paths
    settings.allowed_paths = [str(tmp_path)]

    # Mock the LLM deciding to write the file
    write_args = {"action": "write", "path": str(target_file), "content": 'print("Hello, World!")'}
    func_call = FunctionCall(name="fs_control", args=write_args)
    
    provider = MockProvider([
        AIResponse(content="Writing script now.", tool_calls=[func_call]),
        AIResponse(content="Script written successfully!")
    ])
    
    agent = AerisAgent(provider, conversation, context_manager, tool_registry)
    
    # Enter CodingFlow
    flow = CodingFlow(agent)
    # Use flow to execute the workflow
    result = await flow.execute("Please write a hello world python script.")
    
    assert result == "Script written successfully!"
    
    # Debug tool response
    msgs = conversation.get_messages()
    tool_msgs = [m for m in msgs if m.role == "tool"]
    if tool_msgs:
        print("TOOL RESPONSES:", tool_msgs[0].tool_responses[0].response)
        
    assert target_file.exists()
    
    with open(target_file, "r") as f:
        content = f.read()
        assert 'print("Hello, World!")' in content

    # Cleanup
    settings.allowed_paths = original_paths
