from langchain_core.messages import AIMessage
from src.graph.utils.chains import get_fallback_chain, get_router_chain, create_function_chain
from src.graph.state import State
from src.modules.memory.memory_service import get_memory_manager
import asyncio
from src.graph.utils.prompts import FUNCTION_DEFINITIONS, CREATE_TASK_PROMPT, GET_CURRENT_ISSUES_PROMPT, GET_USER_ISSUES_PROMPT
from src.modules.linear.linear import get_linear_client, Ticket, Assignee
from src.graph.utils.helpers import error_handler, retry_async
from src.graph.utils.structured_outputs import CreateTaskResponse, GetCurrentIssuesResponse, GetUserIssuesResponse

async def memory_update_node(state: State):
    last_message = state['messages'][-1]
    if last_message.type == "human":
        memory_manager = get_memory_manager()
        asyncio.create_task(memory_manager.extract_and_save_memory(last_message.content))

    return {}

async def memory_injection_node(state: State):
    memory_manager = get_memory_manager()
    memory_context = await memory_manager.get_relevant_memories(state['messages'][-1].content)

    return {
        "memory_context": memory_context
    }

@retry_async(max_retries=3, delay=2, backoff=2, exceptions=(Exception,))
async def router_node(state: State):
    chain = get_router_chain()
    response = await chain.ainvoke({
        "messages": state['messages'],
        "function_definitions": FUNCTION_DEFINITIONS
    })

    return {"next_node": response.next_node}

@error_handler(error_message="Something went wrong. Please try again.")
@retry_async(max_retries=3, delay=2, backoff=2, exceptions=(Exception,))
async def fallback_node(state: State):
    chain = get_fallback_chain()
    response = await chain.ainvoke({
        "messages": state['messages'], 
        "memory_context": state['memory_context'],
        "function_definitions": FUNCTION_DEFINITIONS
    })

    return {"messages": AIMessage(content=response.content)}

@error_handler(error_message="Error creating ticket")
@retry_async(max_retries=3, delay=2, backoff=2, exceptions=(Exception,))
async def create_task_node(state: State):
    chain = create_function_chain(CREATE_TASK_PROMPT, CreateTaskResponse)
    response = await chain.ainvoke({"messages": state['messages']})

    linear_client = get_linear_client()
    ticket = linear_client.create_team_ticket(Ticket(
        title=response.task_name, 
        description=response.description, 
        assignee=Assignee(email=response.assignee_email)
    ))
    
    return {"messages": AIMessage(content=response.message, params={
        "task_name": ticket.title, 
        "description": ticket.description, 
        "task_id": ticket.id,
        "assignee_email": ticket.assignee.email if ticket.assignee else None
    })}

@error_handler(error_message="Error getting current issues")
@retry_async(max_retries=3, delay=2, backoff=2, exceptions=(Exception,))
async def get_current_issues(state: State):
    chain = create_function_chain(GET_CURRENT_ISSUES_PROMPT, GetCurrentIssuesResponse)
    response = await chain.ainvoke({"messages": state['messages']})

    linear_client = get_linear_client()
    tickets = linear_client.get_team_tickets(response.status)
    
    return {"messages": AIMessage(content=response.message + "\n\n" + linear_client.format_tickets(tickets))}

@error_handler(error_message="Error getting user issues")
@retry_async(max_retries=3, delay=2, backoff=2, exceptions=(Exception,))
async def get_user_issues_node(state: State):
    chain = create_function_chain(GET_USER_ISSUES_PROMPT, GetUserIssuesResponse)
    response = await chain.ainvoke({"messages": state['messages']})
    
    linear_client = get_linear_client()
    tickets = linear_client.get_user_issues(response.email)
    
    return {"messages": AIMessage(content=response.message + "\n\n" + linear_client.format_tickets(tickets))}
