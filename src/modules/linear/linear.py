import requests
import os
from src.modules.linear.linear_queries import GET_TEAM_BY_NAME, GET_TODO_ISSUES_BY_TEAM, GET_USER_BY_EMAIL, GET_USER_ISSUES, GET_TEAM_STATES, CREATE_TEAM_ISSUE
from pydantic import BaseModel
from enum import Enum
from dotenv import load_dotenv

load_dotenv(override=True)

class TicketStatus(Enum):
    TODO = "Todo"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    CANCELED = "Canceled"
    BACKLOG = "Backlog"


class Assignee(BaseModel):
    name: str | None = None
    email: str

class Ticket(BaseModel):
    id: str | None = None
    title: str
    description: str | None = None
    priority: int | None = None
    state: str | None = None
    assignee: Assignee | None = None
    url: str | None = None
    created_at: str | None = None
    due_date: str | None = None

class Linear:
    def __init__(self):
        self.api_key = os.getenv("LINEAR_API_KEY")
        self.team_name = os.getenv("LINEAR_TEAM_NAME")
        if not self.api_key:
            raise Exception("Not found. that's what she said.")

    def _run_query(self, query, variables=None):
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        response = requests.post(
            "https://api.linear.app/graphql",
            json={"query": query, "variables": variables},
            headers=headers
        )
        if response.status_code != 200:
            raise Exception(f"Query failed with status code {response.status_code}. Response: {response.text}")
        
        result = response.json()
        
        if "errors" in result:
            error_message = result.get("errors", [])[0].get("message", "Unknown GraphQL error")
            raise Exception(f"GraphQL error: {error_message}")
        
        return result


    def _get_team_id_by_name(self, name: str) -> str:
        result = self._run_query(GET_TEAM_BY_NAME)
        teams = result.get("data", {}).get("teams", {}).get("nodes", [])
        for team in teams:
            if team.get("name") == name:
                return team.get("id")
        raise Exception(f"Team not found: {name}")

    def _map_issue_to_ticket(self, issue: dict) -> Ticket:
        return Ticket(
            id=issue.get("id"),
            title=issue.get("title"),
            description=issue.get("description"),
            priority=issue.get("priority"),
            state=issue.get("state", {}).get("name") or "",
            assignee=Assignee(
                name=(issue.get("assignee") or {}).get("name") or "",
                email=(issue.get("assignee") or {}).get("email") or ""
            ) if issue.get("assignee") else None,
            url=issue.get("url") or "",
            created_at=issue.get("createdAt") or "",
            due_date=issue.get("dueDate")
        )
    
    def _get_user_id_by_email(self, email):
        result = self._run_query(GET_USER_BY_EMAIL, {"email": email})
        users = result.get("data", {}).get("users", {}).get("nodes", [])
        if not users:
            raise Exception(f"User not found with email: {email}")
        return users[0].get("id")

    def _get_team_states(self, team_id: str, status: TicketStatus):
        states_result = self._run_query(GET_TEAM_STATES, {"teamId": team_id})
        states = states_result.get("data", {}).get("team", {}).get("states", {}).get("nodes", [])
        
        for state_item in states:
            if state_item.get("name") == status.value:
                return state_item.get("id")
        raise Exception(f"State not found: {status.value}")
    
    def get_team_tickets(self, status: TicketStatus) -> list[Ticket]:
        team_id = self._get_team_id_by_name(self.team_name)
        
        variables = {"teamId": team_id, "status": status.value}
        result = self._run_query(GET_TODO_ISSUES_BY_TEAM, variables)
        
        issues = result.get("data", {}).get("issues", {}).get("nodes", [])
        return [self._map_issue_to_ticket(issue) for issue in issues]

    def create_team_ticket(self, ticket: Ticket) -> Ticket:
        try:
            team_id = self._get_team_id_by_name(self.team_name)
            
            todo_state_id = self._get_team_states(team_id, TicketStatus.TODO)
            
            variables = {
                "teamId": team_id,
                "title": ticket.title,
                "description": ticket.description or "",
                "stateId": todo_state_id
            }
            
            if ticket.assignee and ticket.assignee.email:
                variables["assigneeId"] = self._get_user_id_by_email(ticket.assignee.email)
            
            result = self._run_query(CREATE_TEAM_ISSUE, variables)
            issue = result.get("data", {}).get("issueCreate", {}).get("issue", {})
            return self._map_issue_to_ticket(issue)
        except Exception as e:
            raise Exception(f"Error creating ticket: {e}")

    def get_user_issues(self, user_email: str) -> list[Ticket]:
        user_id = self._get_user_id_by_email(user_email)
        
        result = self._run_query(GET_USER_ISSUES, {"userId": user_id})
        
        issues = result.get("data", {}).get("user", {}).get("assignedIssues", {}).get("nodes", [])
        
        return [self._map_issue_to_ticket(issue) for issue in issues]
    
    def format_tickets(self, tickets: list[Ticket]) -> str:
        return "\n".join([f"{i+1}. {ticket.title} - {ticket.state}" for i, ticket in enumerate(tickets)])

def get_linear_client():
    return Linear()