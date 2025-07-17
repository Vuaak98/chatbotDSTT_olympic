from typing import Any, Dict, List, Literal, Union, cast

from langchain_core.messages import AIMessage, trim_messages
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

from app.rag.config.base_config import BaseConfiguration
from app.rag.factories.chat_factory import create_chat_model

from .tools import retriever_tool
from app.rag.schemas.template import Template
from app.rag.schemas.user import UserProfile
from app.utils import get_value_from_dict
from .system_message_generator import SystemMessageGenerator, SystemMessageGeneratorConfig
from app.rag.config.config_loader import CONFIG as rag_config

import time
from functools import wraps

def measure_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} executed in {end - start:.4f} seconds")
        return result
    return wrapper

# Xóa hoặc comment dòng này:
# rag_config = RAGConfiguration()
# Thay bằng:
from app.rag.config.config_loader import CONFIG as rag_config

# Create the Template instance using the function
templates = Template(
    combined_template=cast(str, rag_config["combined_template"]),
    base_instructions=cast(str, rag_config["base_instructions"]),
    user_info=cast(str, rag_config["user_info"]),
    current_time=cast(str, rag_config["current_time"]),
    conversation_summary=cast(str, rag_config["conversation_summary"]),
    formatting_instructions=cast(str, rag_config["formatting_instructions"]),
    multi_query=cast(str, rag_config["multi_query"]),
)


# Create UserProfile with the new structure
user_profile = UserProfile(
    username="",
    email="",
    company="Hanoi University of Industry",
    department="Engineering",
    country="Vietnam",
    plugins=["plugin1", "plugin2"],
    roles=["admin", "user"],
)

config = SystemMessageGeneratorConfig(
    max_tokens=1200,
    templates=templates,
    user=user_profile,
    user_system_message=""  # ✅ Đúng cú pháp!
)

# Initialize the SystemMessageGenerator with the configuration
message_generator = SystemMessageGenerator(config)

# Create a partially applied function to generates a system message based on the config
generate_message_with_config = message_generator.create_system_message_with_summary()


# Define the state
# We will add a `summary` attribute (in addition to `messages` key,
# which MessagesState already has)
class State(MessagesState):
    summary: str
    prompt_token: int
    completion_token: int


# @title Default title text
class Agent:
    def __init__(self, model):
        self.model = model

    @measure_time  # Apply the decorator
    async def __call__(self, state: State, config: RunnableConfig) -> Dict[str, Union[List[Any], int]]:
        print("\n---CALL AGENT---")
        summary = state.get("summary", "None")
        # system_message = generate_message_with_config(summary=summary)
        system_message = generate_message_with_config(summary)  # TODO: Unable to get the summary
        messages = [system_message] + state["messages"]
        print(f"tokens: {tiktoken_counter(messages)}")
        # filter_messages
        cut_messages = trim_messages(
            messages,
            token_counter=len,
            # Keep the last <= n_count tokens of the messages.
            strategy="last",
            # When token_counter=len, each message
            # will be counted as a single token.
            # Remember to adjust for your use case
            max_tokens=6,
            # Most chat models expect that chat history starts with either:
            # (1) a HumanMessage or
            # (2) a SystemMessage followed by a HumanMessage
            start_on="human",
            # Most chat models expect that chat history ends with either:
            # (1) a HumanMessage or
            # (2) a ToolMessage
            end_on=("human", "tool"),
            # Usually, we want to keep the SystemMessage
            # if it's present in the original history.
            # The SystemMessage has special instructions for the model.
            include_system=True,
        )

        print(f"MSG LENGTH AFTER TRIMMING: {len(cut_messages)}")
        prompt_token = tiktoken_counter(cut_messages)

        state["prompt_token"] = (state.get("prompt_token") or 0) + prompt_token

        response = await self.model.ainvoke(cut_messages, config)
        print(f"DEBUG: Agent response = {repr(response)}")

        completion_token = tiktoken_counter([response])
        state["completion_token"] = (state.get("completion_token") or 0) + completion_token

        return {
            "messages": [response],
            "prompt_token": state["prompt_token"],
            "completion_token": state["completion_token"],
        }


# Define the Workflow Manager Class
@measure_time
async def human_review_node(state):
    print("\n---CALL HUMAN REVIEW---")


def convert_artifact(artifact: List[Dict]) -> List[str]:
    return list(set([x.get("source", None) for x in artifact if x.get("source", None)]))


@measure_time
async def run_tool_retriever(state):
    print("\n---RUN TOOLS RETRIEVER---")
    new_messages = []
    # Cập nhật tên tool cho lĩnh vực toán học
    tools = {"retrieve_linear_algebra_concepts": retriever_tool}
    tool_calls = state["messages"][-1].tool_calls
    for tool_call in tool_calls:
        tool = tools[tool_call["name"]]
        content, artifact = await tool.ainvoke(tool_call["args"])

        new_messages.append(
            {
                "role": "tool",
                "name": tool_call["name"],
                "content": content,
                "artifact": convert_artifact(artifact),
                "tool_call_id": tool_call["id"],
            }
        )
    return {"messages": new_messages}


def route_after_llm(state) -> Literal["human_review_node", "run_tool_retriever", END]:  # type: ignore
    if len(state["messages"][-1].tool_calls) == 0:
        return END
    elif (
        state["messages"][-1].tool_calls
        and state["messages"][-1].tool_calls[0]["name"] == "retrieve_linear_algebra_concepts"
    ):
        return "run_tool_retriever"
    else:
        return "human_review_node"


def route_after_human(state) -> Literal[ "agent"]:
    return "agent"


# Define the Workflow Manager Class
class GraphBuilder:
    def __init__(self, config: BaseConfiguration = BaseConfiguration()):
        self.state_graph = StateGraph(State)
        self.chat_model = create_chat_model(config["chat_model_config"])
        self.tool_model = self.chat_model.bind_tools(
            [
                retriever_tool,
            ],
            # tool_choice="retriever_tool",
            parallel_tool_calls=False,
        )
        self.memory = MemorySaver()  # TODO: Need to use redis checkpointer

        # Initialize nodes
        self.agent = Agent(self.tool_model)

        self.setup_workflow()

    def setup_workflow(self):
        # Add nodes
        self.state_graph.add_node("agent", self.agent)
        self.state_graph.add_node("human_review_node", human_review_node)
        self.state_graph.add_node("run_tool_retriever", run_tool_retriever)

        # Define the edges (connections between the nodes)
        self.state_graph.add_edge(START, "agent")
        self.state_graph.add_conditional_edges("agent", route_after_llm)
        self.state_graph.add_conditional_edges("human_review_node", route_after_human)
        self.state_graph.add_edge("run_tool_retriever", "agent")

        # Compile the workflow
        self.graph = self.state_graph.compile(checkpointer=self.memory)

    def display_workflow(self):
        from IPython.display import Image, display

        try:
            display(Image(self.graph.get_graph().draw_mermaid_png()))
        except Exception:
            pass

# Hàm đếm token đơn giản (có thể thay bằng tokenizer thực tế nếu cần)
def tiktoken_counter(messages):
    total = 0
    for m in messages:
        if isinstance(m, dict):
            total += len(str(m.get("content", "")))
        elif hasattr(m, "content"):
            total += len(str(m.content))
        else:
            total += len(str(m))
    return total

if __name__ == "__main__":
    print("Test import thành công!")