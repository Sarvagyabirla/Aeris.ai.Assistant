import pytest
from aeris.tools.security import kill_switch, PermissionManager, PermissionLevel

def test_kill_switch_activation():
    # Ensure it's reset initially
    kill_switch.reset()
    assert not kill_switch.is_active
    
    # Activate and check
    kill_switch.activate()
    assert kill_switch.is_active
    
    # PermissionManager should block if kill switch is active
    allowed = PermissionManager.check_execution_allowed("test_tool", PermissionLevel.SAFE)
    assert not allowed
    
    # Reset and check
    kill_switch.reset()
    assert not kill_switch.is_active
    allowed = PermissionManager.check_execution_allowed("test_tool", PermissionLevel.SAFE)
    assert allowed

def test_permission_manager_levels():
    kill_switch.reset()
    
    # Safe and low risk should pass
    assert PermissionManager.check_execution_allowed("safe_tool", PermissionLevel.SAFE)
    assert PermissionManager.check_execution_allowed("low_risk_tool", PermissionLevel.LOW_RISK)
    
    # Currently in Part 2 foundation, HIGH_RISK still returns True because we assume UI confirmation
    # If we modify it in the future, this test will break and require an update.
    assert PermissionManager.check_execution_allowed("high_risk_tool", PermissionLevel.HIGH_RISK)
