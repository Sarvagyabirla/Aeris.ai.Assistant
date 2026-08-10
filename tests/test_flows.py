import pytest
from aeris.flows.base import BaseFlow
from aeris.flows.coding import CodingFlow
from aeris.core.agent import AerisAgent
from aeris.core.conversation import Conversation
from aeris.core.context import ContextManager
from aeris.tools.registry import ToolRegistry
from aeris.ai.types import AIResponse


class MockProvider:
    def __init__(self):
        self.last_request = None

    async def send_message(self, request):
        self.last_request = request
        return AIResponse(content="Flow complete")


class DummyTool:
    def __init__(self, name):
        self.name = name
        self.description = "Dummy"
        self.parameters = {}
        self.permission_level = 0


@pytest.fixture
def agent_setup():
    conv = Conversation()
    cm = ContextManager(conv)
    tr = ToolRegistry()
    tr.register(DummyTool("fs_control"))
    tr.register(DummyTool("random_tool"))

    provider = MockProvider()
    agent = AerisAgent(provider, conv, cm, tr)
    return agent, provider


@pytest.mark.asyncio
async def test_base_flow(agent_setup):
    agent, provider = agent_setup
    flow = BaseFlow(agent)

    await flow.execute("Hello")
    assert provider.last_request is not None
    assert "random_tool" in [t.name for t in provider.last_request.tools]
    assert "[FLOW OVERRIDE]" not in provider.last_request.system_instruction


@pytest.mark.asyncio
async def test_coding_flow(agent_setup):
    agent, provider = agent_setup
    flow = CodingFlow(agent)

    await flow.execute("Write some code")

    req = provider.last_request
    assert req is not None

    # Check that system instruction was overridden
    assert "[FLOW OVERRIDE]" in req.system_instruction
    assert "You are operating in the Coding Flow." in req.system_instruction

    # Check that tools were filtered
    tool_names = [t.name for t in req.tools]
    assert "fs_control" in tool_names
    assert "random_tool" not in tool_names

    # Check cleanup (restoration of methods)
    sys_inst = agent.context_manager.get_system_instruction()
    assert "[FLOW OVERRIDE]" not in sys_inst

    all_tools = [t.name for t in agent.tool_registry.get_all_tools()]
    assert "random_tool" in all_tools
