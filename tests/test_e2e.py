import pytest
from aeris.core.application import AerisCore
from aeris.ai.types import AIResponse

pytestmark = pytest.mark.integration


# A mock provider to inject into the core for testing
class MockProvider:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    async def send_message(self, request):
        if self.should_fail:
            return AIResponse(content="", error="Simulated API Error", is_success=False)
        return AIResponse(content="This is a mock response", is_success=True)

    async def stream_message(self, request):
        pass

    async def validate_connection(self):
        return not self.should_fail

    def get_model_information(self):
        return "MockModel"


@pytest.mark.asyncio
async def test_end_to_end_success():
    core = AerisCore()
    # Inject mock provider
    core.provider = MockProvider(should_fail=False)

    # Initialize
    is_online = await core.initialize()
    assert is_online is True

    # Send message
    response = await core.process_user_message("Hello Aeris")
    assert response == "This is a mock response"

    # Check conversation history
    msgs = core.conversation.get_messages()
    assert len(msgs) == 2
    assert msgs[0].role == "user"
    assert msgs[1].role == "assistant"


@pytest.mark.asyncio
async def test_end_to_end_failure():
    core = AerisCore()
    # Inject mock provider that fails
    core.provider = MockProvider(should_fail=True)

    # Initialize
    is_online = await core.initialize()
    assert is_online is False

    # Attempt to send message while offline
    response = await core.process_user_message("Hello Aeris")
    assert "offline" in response.lower()

    # Force online but provider fails during send
    core.is_online = True
    response = await core.process_user_message("Hello again")
    assert "Error communicating with AI" in response
    assert "Simulated API Error" in response
