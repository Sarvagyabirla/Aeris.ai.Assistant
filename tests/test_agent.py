import pytest
from aeris.core.agent import AerisAgent
from aeris.core.conversation import Conversation
from aeris.core.context import ContextManager
from aeris.tools.registry import ToolRegistry
from aeris.ai.types import AIResponse
from aeris.tools.types import ToolResult
from google.genai.types import FunctionCall


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


class MockTool:
    name = "mock_tool"
    description = "A mock tool"
    parameters = {}
    permission_level = 0

    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    async def execute(self, **kwargs):
        if self.should_fail:
            return ToolResult(
                False, self.name, "execute", "", error="Tool execution failed"
            )
        return ToolResult(True, self.name, "execute", "Tool executed successfully")


class ExceptionTool:
    name = "exception_tool"
    description = "A tool that raises an exception"
    parameters = {}
    permission_level = 0

    async def execute(self, **kwargs):
        raise ValueError("Simulated catastrophic failure")


@pytest.fixture
def agent_setup():
    conversation = Conversation()
    context_manager = ContextManager(conversation)
    tool_registry = ToolRegistry()
    tool_registry.register(MockTool())
    tool_registry.register(ExceptionTool())
    return conversation, context_manager, tool_registry


@pytest.mark.asyncio
async def test_agent_single_step(agent_setup):
    conversation, context_manager, tool_registry = agent_setup
    provider = MockProvider([AIResponse(content="Final answer")])
    agent = AerisAgent(provider, conversation, context_manager, tool_registry)

    result = await agent.run("Hello")
    assert result == "Final answer"
    assert provider.call_count == 1

    messages = conversation.get_messages()
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"


@pytest.mark.asyncio
async def test_agent_tool_call(agent_setup):
    conversation, context_manager, tool_registry = agent_setup

    mock_func_call = FunctionCall(name="mock_tool", args={})
    provider = MockProvider(
        [
            AIResponse(content="Thinking...", tool_calls=[mock_func_call]),
            AIResponse(content="I have used the tool."),
        ]
    )
    agent = AerisAgent(provider, conversation, context_manager, tool_registry)

    result = await agent.run("Do something")
    assert result == "I have used the tool."
    assert provider.call_count == 2

    messages = conversation.get_messages()
    # 1. User: "Do something"
    # 2. Assistant: "Thinking..." + tool_calls
    # 3. Tool: tool_responses
    # 4. Assistant: "I have used the tool."
    assert len(messages) == 4
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    assert len(messages[1].tool_calls) == 1
    assert messages[2].role == "tool"
    assert len(messages[2].tool_responses) == 1
    assert messages[2].tool_responses[0].response["success"] is True
    assert messages[3].role == "assistant"
    assert messages[3].content == "I have used the tool."


@pytest.mark.asyncio
async def test_agent_max_iterations(agent_setup):
    conversation, context_manager, tool_registry = agent_setup

    mock_func_call = FunctionCall(name="mock_tool", args={})

    # Provider always returns tool calls
    class InfiniteProvider:
        async def send_message(self, request):
            return AIResponse(content="Looping...", tool_calls=[mock_func_call])

    agent = AerisAgent(InfiniteProvider(), conversation, context_manager, tool_registry)
    agent.max_iterations = 3

    result = await agent.run("Loop forever")
    assert result == "Agent exceeded maximum iterations."
    messages = conversation.get_messages()
    assert messages[-1].role == "system"


@pytest.mark.asyncio
async def test_agent_tool_exception_recovery(agent_setup):
    conversation, context_manager, tool_registry = agent_setup

    exception_func_call = FunctionCall(name="exception_tool", args={})
    provider = MockProvider(
        [
            AIResponse(content="I will try the exception tool.", tool_calls=[exception_func_call]),
            AIResponse(content="The tool failed, but I recovered."),
        ]
    )
    agent = AerisAgent(provider, conversation, context_manager, tool_registry)

    result = await agent.run("Crash the tool")
    assert result == "The tool failed, but I recovered."
    assert provider.call_count == 2
    
    messages = conversation.get_messages()
    assert messages[2].role == "tool"
    assert messages[2].tool_responses[0].response["success"] is False
    assert "Simulated catastrophic failure" in messages[2].tool_responses[0].response["error"]
