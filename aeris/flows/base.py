from typing import List
from aeris.core.agent import AerisAgent


class BaseFlow:
    """Base class for specialized ecosystem flows."""

    def __init__(self, agent: AerisAgent):
        self.agent = agent

    def get_flow_system_instruction(self) -> str:
        """Returns additional system instructions specific to this flow."""
        return ""

    def get_flow_tools(self) -> List[str]:
        """Returns a list of tool names that are specifically relevant. Return empty for all."""
        return []

    async def execute(self, user_text: str) -> str:
        """Executes the specialized flow."""
        # Inject flow specific instruction
        flow_inst = self.get_flow_system_instruction()
        if flow_inst:
            original_get = self.agent.context_manager.get_system_instruction
            self.agent.context_manager.get_system_instruction = (
                lambda: original_get() + f"\n\n[FLOW OVERRIDE]\n{flow_inst}"
            )

        # Filter tools if the flow specifies a subset
        flow_tools = self.get_flow_tools()
        original_get_all_tools = self.agent.tool_registry.get_all_tools
        if flow_tools:
            # Override to only return tools whose names are in flow_tools
            def filtered_get_all_tools():
                all_tools = original_get_all_tools()
                return [t for t in all_tools if t.name in flow_tools]

            self.agent.tool_registry.get_all_tools = filtered_get_all_tools

        try:
            return await self.agent.run(user_text)
        finally:
            # Restore original methods
            if flow_inst:
                self.agent.context_manager.get_system_instruction = original_get
            if flow_tools:
                self.agent.tool_registry.get_all_tools = original_get_all_tools
