import pytest
import os
from aeris.security.secrets import SecretManager
from aeris.core.conversation import Conversation, Message
from aeris.memory.interface import SessionMemory
from aeris.ai.types import AIRequest, AIResponse

def test_secret_manager_redaction():
    sm = SecretManager()
    sm.register_secret("my_super_secret_api_key")
    
    text = "Connecting to API with key my_super_secret_api_key!"
    redacted = sm.redact(text)
    
    assert "my_super_secret_api_key" not in redacted
    assert "***REDACTED***" in redacted

def test_conversation_add_retrieve():
    conv = Conversation()
    conv.add_message("user", "Hello")
    conv.add_message("assistant", "Hi there")
    
    msgs = conv.get_messages()
    assert len(msgs) == 2
    assert msgs[0].role == "user"
    assert msgs[1].content == "Hi there"

def test_session_memory():
    mem = SessionMemory()
    mem.add("user_name", "Alice")
    
    results = mem.retrieve("user_name")
    assert len(results) == 1
    assert results[0]["value"] == "Alice"
    
    results = mem.retrieve("Alice")
    assert len(results) == 1
    
    mem.update("user_name", "Bob")
    assert mem.retrieve("user_name")[0]["value"] == "Bob"
    
    mem.delete("user_name")
    assert len(mem.retrieve("user_name")) == 0

def test_ai_types():
    msg = Message("user", "test")
    req = AIRequest(messages=[msg])
    assert req.temperature == 0.7
    
    res = AIResponse(content="Success")
    assert res.is_success is True
    assert res.error is None
