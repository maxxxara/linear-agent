from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import List, Literal
from src.graph.utils.prompts import FALLBACK_PROMPT, ROUTER_PROMPT
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

RouterResponseLiteral = Literal["fallback", "create_task", "get_current_issues", "get_user_issues"]

class RouterResponse(BaseModel):
    next_node: RouterResponseLiteral = Field(
        description="The next node to go to. It must be one of: 'fallback', 'create_task', 'get_current_issues', 'get_user_issues'"
    )

def get_router_chain():
    prompt = ChatPromptTemplate.from_messages([
        ("system", ROUTER_PROMPT),
        MessagesPlaceholder(variable_name="messages")
    ])
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash").with_structured_output(RouterResponse)
    return prompt | llm


def get_fallback_chain():
    system_message = FALLBACK_PROMPT
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="messages")
    ])
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    return prompt | llm

def create_function_chain(prompt_template, output_model):
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_template),
        MessagesPlaceholder(variable_name="messages")
    ])
    return prompt | llm.with_structured_output(output_model)
