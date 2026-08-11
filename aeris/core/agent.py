from google.genai.types import FunctionResponse

from aeris.core.conversation import Conversation
from aeris.core.context import ContextManager
from aeris.core.events import event_manager, Events
from aeris.ai.provider import AIProvider
from aeris.ai.types import AIRequest
from aeris.tools.registry import ToolRegistry
from aeris.app_logger.logger import log


class AerisAgent:
    """Orchestrates the autonomous loop of Model -> Tool -> Model."""

    def __init__(
        self,
        provider: AIProvider,
        conversation: Conversation,
        context_manager: ContextManager,
        tool_registry: ToolRegistry,
    ):
        self.provider = provider
        self.conversation = conversation
        self.context_manager = context_manager
        self.tool_registry = tool_registry
        self.max_iterations = 10

    async def run(self, user_text: str, image_data=None) -> str:
        """Run the agent loop for a given user input."""
        log.info(f"Agent starting run for input: '{user_text}'")

        # 1. Add user message
        self.conversation.add_message("user", content=user_text, image=image_data)
        await event_manager.emit(Events.USER_MESSAGE_RECEIVED, message=user_text)

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            log.debug(f"Agent iteration {iteration}")

            # 2. Get Context
            messages = self.context_manager.get_prompt_context()

            # 3. Create Request
            tools = self.tool_registry.get_all_tools()
            sys_inst = self.context_manager.get_system_instruction()
            request = AIRequest(
                messages=messages, tools=tools, system_instruction=sys_inst
            )

            # 4. Send to Provider
            await event_manager.emit(Events.AI_REQUEST_STARTED)
            response = await self.provider.send_message(request)
            await event_manager.emit(Events.AI_RESPONSE_RECEIVED)

            if not response.is_success:
                err_msg = f"Error communicating with AI: {response.error}"
                self.conversation.add_message("system", content=err_msg)
                return err_msg

            # 5. Handle Tool Calls
            if response.tool_calls:
                log.info(f"Agent received {len(response.tool_calls)} tool calls.")
                # Add the assistant's tool calls to conversation
                self.conversation.add_message(
                    role="assistant",
                    content=response.content or "",
                    tool_calls=response.tool_calls,
                )

                tool_responses = []
                for tc in response.tool_calls:
                    log.info(f"Executing tool: {tc.name}")
                    try:
                        args = tc.args if hasattr(tc, "args") else {}
                        args_dict = args if isinstance(args, dict) else dict(args)

                        tool = self.tool_registry.get_tool(tc.name)
                        if tool:
                            await event_manager.emit(Events.TOOL_EXECUTION_STARTED, tool_name=tc.name, args=args_dict)
                            result = await tool.execute(**args_dict)
                        else:
                            from aeris.tools.types import ToolResult
                            result = ToolResult(
                                False, tc.name, "execute", "", error="Tool not found"
                            )

                        # Format the result appropriately
                        response_dict = result.to_dict()
                        if response_dict.get("success", False):
                            await event_manager.emit(Events.TOOL_EXECUTION_COMPLETED, tool_name=tc.name, result=response_dict)
                        else:
                            await event_manager.emit(Events.TOOL_EXECUTION_FAILED, tool_name=tc.name, error=response_dict.get("error", "Failed"))
                            
                    except Exception as e:
                        log.error(f"Error executing tool {tc.name}: {e}")
                        if type(e).__name__ == "PermissionRequiredError":
                            await event_manager.emit(Events.PERMISSION_STATE_CHANGED, tool_name=tc.name, state="REQUESTED", details=str(e))
                            response_dict = {
                                "success": False, 
                                "error": f"{str(e)}. You MUST ask the user for confirmation. Once the user replies with 'yes' or explicitly approves, call this tool again with the argument `confirmed=True`."
                            }
                        else:
                            await event_manager.emit(Events.TOOL_EXECUTION_FAILED, tool_name=tc.name, error=str(e))
                            response_dict = {"success": False, "error": str(e)}

                    tool_responses.append(
                        FunctionResponse(name=tc.name, response=response_dict)
                    )

                # Add tool responses to conversation
                self.conversation.add_message(
                    role="tool", tool_responses=tool_responses
                )
                # Continue loop to send tool responses back to model
            else:
                # No tool calls, final response
                self.conversation.add_message("assistant", content=response.content)
                return response.content

        err_msg = "Agent exceeded maximum iterations."
        self.conversation.add_message("system", content=err_msg)
        return err_msg
