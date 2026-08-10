import pytest
import asyncio
from aeris.core.application import AerisCore
from aeris.config.settings import settings
from aeris.ai.types import AIResponse
from aeris.flows.coding import CodingFlow

class MockProviderRegression:
    def __init__(self):
        self.call_count = 0
        self.history = []

    async def send_message(self, request):
        self.call_count += 1
        self.history.append(request)
        return AIResponse(content=f"Processed message {self.call_count}")

    async def stream_message(self, request):
        pass

    async def validate_connection(self):
        return True

    def get_model_information(self):
        return "MockRegression"


@pytest.mark.asyncio
async def test_full_regression_cycle(tmp_path):
    """
    Test a full regression cycle simulating application startup, 
    memory injection, tool filtering, and provider execution.
    """
    # Force dry run for safety
    original_dry_run = settings.dry_run
    settings.dry_run = True

    # Setup core
    core = AerisCore()
    core.provider = MockProviderRegression()
    
    # Init
    is_online = await core.initialize()
    assert is_online is True
    
    # 1. Base State Execution
    response_1 = await core.process_user_message("Hello Aeris")
    assert "Processed message 1" in response_1
    
    # Verify memory contains the first message
    msgs = core.conversation.get_messages()
    assert any(m.content == "Hello Aeris" for m in msgs)
    
    # 2. Enter Coding Flow (Ecosystem override)
    flow = CodingFlow(core.agent)
    
    # Send another message while in flow
    response_2 = await flow.execute("Write some code")
    assert "Processed message 2" in response_2
    
    # Verify System Instructions were overridden by flow (temporarily during flow execute, so we check mock provider)
    assert "You are operating in the Coding Flow" in core.provider.history[-1].system_instruction
    
    # 3. Teardown
    settings.dry_run = original_dry_run
