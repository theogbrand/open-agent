from setup import initialize_services
from actions import GmailActions, CalendarActions
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
import json
import os
from dotenv import load_dotenv
import inspect

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Existing imports and setup...

class Agent(BaseModel):
    name: str = "Agent"
    model: str = "gpt-4o-mini"
    instructions: str = "You are a helpful Agent"
    tools: list = []

class Response(BaseModel):
    agent: Optional[Agent]
    messages: list

def run_full_turn(agent, messages):
    current_agent = agent
    num_init_messages = len(messages)
    messages = messages.copy()

    while True:
        # turn python functions into tools and save a reverse map
        tool_schemas = [function_to_schema(tool) for tool in current_agent.tools]
        tools = {tool.__name__: tool for tool in current_agent.tools}

        # === 1. get openai completion ===
        response = client.chat.completions.create(
            model=current_agent.model,
            messages=[{"role": "system", "content": current_agent.instructions}]
            + messages,
            tools=tool_schemas or None,
        )
        message = response.choices[0].message
        messages.append(message)

        if message.content:  # print agent response
            print(f"{current_agent.name}:", message.content)

        if not message.tool_calls:  # if finished handling tool calls, break
            break

        # === 2. handle tool calls ===
        for tool_call in message.tool_calls:
            result = execute_tool_call(tool_call, tools, current_agent.name)

            if isinstance(result, Agent):  # if agent transfer, update current agent
                current_agent = result
                result = f"Transfered to {current_agent.name}. Adopt persona immediately."

            result_message = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
            messages.append(result_message)

    # ==== 3. return last agent used and new messages =====
    return Response(agent=current_agent.dict(), messages=messages[num_init_messages:])

def execute_tool_call(tool_call, tools, agent_name):
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    print(f"{agent_name}:", f"{name}({args})")

    return tools[name](**args)  # call corresponding function with provided arguments

def function_to_schema(func) -> dict:
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }

# Modify the gmail_agent function to return an Agent instance directly
gmail_agent = Agent(
    name="Gmail Agent",
    instructions=(
        "You are a Gmail assistant. Help the user with email-related tasks "
        "such as listing messages, sending emails, and managing the inbox."
        """Email Actions:
        You can manage emails through the Gmail platform using the following formats:
        {"action": "Get Emails", "max_results": 100, "query": "search_query"}
        This will retrieve a list of emails from inbox with optional query and pagination support.
        """
    ),
    # tools=[
    #     gmail_actions.list_messages,
    #     gmail_actions.get_message,
    #     gmail_actions.send_message,
    #     gmail_actions.delete_message,
    # ],
)

# Modify the calendar_agent function to return an Agent instance directly
calendar_agent = Agent(
    name="Google Calendar Agent",
    instructions=(
        "You are a Calendar assistant. Help the user with calendar-related tasks "
        "such as listing events, creating events, updating events, and deleting events."
    ),
    # tools=[
    #     calendar_actions.list_events,
    #     calendar_actions.create_event,
    #     calendar_actions.update_event,
    #     calendar_actions.delete_event,
    # ],
)

def transfer_to_gmail_agent():
    """Transfer to the Gmail Agent for email-related tasks."""
    return gmail_agent

def transfer_to_calendar_agent():
    """Transfer to the Calendar Agent for calendar-related tasks."""
    return calendar_agent

# Modify the triage_agent function to return an Agent instance directly
triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "You are a triage agent for an AI assistant that can handle both email and calendar tasks. "
        "Introduce yourself briefly. Determine whether the user needs help with email or calendar tasks. "
        "Transfer to the appropriate agent based on the user's needs. "
        "If the task is unclear, ask for clarification."
    ),
    tools=[
        transfer_to_gmail_agent,
        transfer_to_calendar_agent,
    ],
)

def main():
    gmail_service, calendar_service = initialize_services()
    gmail_actions = GmailActions(gmail_service)
    calendar_actions = CalendarActions(calendar_service)

    # Update the tools for gmail_agent and calendar_agent
    gmail_agent.tools = [
        gmail_actions.list_messages,
        gmail_actions.get_message,
        gmail_actions.send_message,
        gmail_actions.delete_message,
    ]
    calendar_agent.tools = [
        calendar_actions.list_events,
        calendar_actions.create_event,
        calendar_actions.update_event,
        calendar_actions.delete_event,
    ]

    agent = triage_agent  # Start with Triage agent
    messages = []

    while True:
        print("messages: ", messages)
        user = input("User: ")
        messages.append({"role": "user", "content": user})

        response = run_full_turn(agent, messages)
        agent = response.agent
        messages.extend(response.messages)

if __name__ == "__main__":
    main()
