from dotenv import load_dotenv
import os
import functools
import operator
from typing import Sequence, TypedDict, Annotated, Optional, Type

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph, START
from langchain.tools import BaseTool, StructuredTool, tool
from langchain.pydantic_v1 import BaseModel, Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

load_dotenv(override=True)



def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str):
    # Each worker node will be given a name and some tools.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor


@tool
def dummy_tool(expression: str) -> str:
    """You do not need to use any tools. Just write the response yourself."""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return str(e)


roles = {
    "Outline_Writer": {
        "system_prompt": "You are an outline writer for a written story. You develop a comprehensive outline that captures the main plot points, character arcs, and setting descriptions. Ensure that the structure supports a clear narrative flow and aligns with the overall themes and settings of the story. Your outline should provide a detailed framework that guides the development of the narrative. Be sure be in line with the overall themes and tone of the story.",
        "tools": [dummy_tool],
        "persona": None,
        "instructions": {},
    },
    "Character_Designer": {
        "system_prompt": "You are a character designer for a written story. You create distinct and expressive character designs, ensuring each reflects its unique personality and backstory. Incorporate traits and emotional nuances that align with the overall story and setting. The visual appearance should cohesively represent the character’s inner world and their role in the narrative. Be sure be in line with the overall themes and tone of the story.",
        "tools": [dummy_tool],
        "persona": None,
        "instructions": {},
    },
    "Environment_Designer": {
        "system_prompt": "You are an environment designer. create detailed and immersive settings and locations that match the story's needs, including thorough physical descriptions, atmosphere, and mood. Ensure that these environments are vivid and contribute effectively to the storytelling, enhancing the overall narrative impact. Be sure be in line with the overall themes and tone of the story.",
        "tools": [dummy_tool],
        "persona": None,
        "instructions": {},
    },
    "Script_Writer": {
        "system_prompt": "You are a script writer. You consolidate all elements of the story, including the outline, characters, and environments, into a cohesive narrative. Deliver a well-structured script that effectively captures the essence and progression of the story, ensuring it resonates with the intended audience.",
        "tools": [dummy_tool],
        "persona": None,
        "instructions": {},
    },
}


def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {"messages": [HumanMessage(content=result["output"], name=name)]}


members = [
    "Outline_Writer",
    "Character_Designer",
    "Environment_Designer",
    "Script_Writer",
]
director_system_prompt = (
    "You are a director that is responsible for writing a story. You are responsible for managing a conversation between the"
    " following workers:  {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
)
# Our team supervisor is an LLM node. It just picks the next agent to process
# and decides when the work is completed
options = ["FINISH"] + members
# Using openai function calling can make output parsing easier for us
function_def = {
    "name": "route",
    "description": "Select the next role.",
    "parameters": {
        "title": "routeSchema",
        "type": "object",
        "properties": {
            "next": {
                "title": "Next",
                "anyOf": [
                    {"enum": options},
                ],
            }
        },
        "required": ["next"],
    },
}

director_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", director_system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            "Given the conversation above, who should act next?"
            " Or should we FINISH? Select one of: {options}",
        ),
    ]
).partial(options=str(options), members=", ".join(members))

llm = ChatOpenAI(model="gpt-4-1106-preview")

director_chain = (
    director_prompt
    | llm.bind_functions(functions=[function_def], function_call="route")
    | JsonOutputFunctionsParser()
)


# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str


outline_writer = create_agent(
    llm,
    [dummy_tool],
    "You are the outline writer,. You are ONLY responsible for creating a consolidated and structured framework for the story, detailing the main events, character arcs, and plot progression to guide the writing process.",
)
outline_writer_node = functools.partial(
    agent_node, agent=outline_writer, name="Outline_Writer"
)

character_designer = create_agent(
    llm,
    [dummy_tool],
    "You are the character designer. You are ONLY responsible for creating the characters, including their look, personality traits, and motivations.",
)
character_designer_node = functools.partial(
    agent_node, agent=character_designer, name="Character_Designer"
)

environment_designer = create_agent(
    llm,
    [dummy_tool],
    "You are the environment designer. You are ONLY responsible for creating the settings and locations that will be featured in the story, including the physical descriptions, atmosphere, and mood.",
)
environment_designer_node = functools.partial(
    agent_node, agent=environment_designer, name="Environment_Designer"
)

script_writer = create_agent(
    llm,
    [dummy_tool],
    "You are the script writer, responsible for consolidating all the elements of the story, including the outline, characters, and environment, into a cohesive narrative. Output only the final script as a raw text without any formatting.",
)
script_writer_node = functools.partial(
    agent_node, agent=script_writer, name="Script_Writer"
)


# outline_writer_system_prompt = (
#     "You are the outline writer, responsible for creating a structured framework for the story, detailing the main events, character arcs, and plot progression to guide the writing process."
# )

# outline_writer_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system", outline_writer_system_prompt,
#         ),
#         MessagesPlaceholder(variable_name="messages"),
#     ]
# )
# outline_writer_chain = outline_writer_prompt | llm

# character_designer_system_prompt = (
#     "You are the character designer, responsible for creating the characters that will inhabit the story, including their appearance, personality traits, and motivations."
# )

# character_designer_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system", character_designer_system_prompt,
#         ),
#         MessagesPlaceholder(variable_name="messages"),
#     ]
# )

# character_designer_chain = character_designer_prompt | llm

# environment_designer_system_prompt = (
#     "You are the environment designer, responsible for creating the settings and locations that will be featured in the story, including the physical descriptions, atmosphere, and mood."
# )

# environment_designer_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system", environment_designer_system_prompt,
#         ),
#         MessagesPlaceholder(variable_name="messages"),
#     ]
# )
#
# environment_designer_chain = environment_designer_prompt | llm

workflow = StateGraph(AgentState)
workflow.add_node("Outline_Writer", outline_writer_node)
workflow.add_node("Character_Designer", character_designer_node)
workflow.add_node("Environment_Designer", environment_designer_node)
workflow.add_node("Script_Writer", script_writer_node)

# workflow.add_node("Outline Writer", outline_writer_chain)
# workflow.add_node("Character Designer", character_designer_chain)
# workflow.add_node("Environment Designer", environment_designer_chain)
workflow.add_node("supervisor", director_chain)

for member in members:
    # We want our workers to ALWAYS "report back" to the supervisor when done
    workflow.add_edge(member, "supervisor")
# The supervisor populates the "next" field in the graph state
# which routes to a node or finishes
conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END
workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
# Finally, add entrypoint
workflow.add_edge(START, "supervisor")

graph = workflow.compile()

if __name__ == "__main__":
    for s in graph.stream(
        {"messages": [HumanMessage(content="Write a sad story about a cat.")]}
    ):
        if "__end__" not in s:
            print(s)
            print("----")
