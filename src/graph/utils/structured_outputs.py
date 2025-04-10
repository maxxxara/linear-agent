from pydantic import BaseModel, Field
from src.modules.linear.linear import TicketStatus

class CreateTaskResponse(BaseModel):
    task_name: str = Field(description="The name of the task")
    description: str = Field(description="The description of the task. If description is not provided, or is not clear, generate a description based on the task name and fill it.")
    assignee_email: str | None = Field(description="The email address of the assignee. If user do not mention any email address, return empty string.")
    message: str = Field(description="The message to the user. This message should be short and concise, About the task that was created.")

class GetCurrentIssuesResponse(BaseModel):
    status: TicketStatus = Field(description="The status of the task. If user do not mention any status, default to TODO")
    message: str = Field(description="The message to the user. Ask user what they want to do next.")

class GetUserIssuesResponse(BaseModel):
    email: str = Field(description="The email address of the user. If user do not mention any email address, return empty string.")
    message: str = Field(description="The message to the user. If user ask something, follow the user's instructions, if not, just ask what should you do next.")
