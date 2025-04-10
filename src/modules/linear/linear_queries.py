GET_TODO_ISSUES_BY_TEAM = """
    query TodoIssuesInTeam($teamId: ID!, $status: String!) {
      issues(
        first: 50,
        filter: {
          state: { name: { eq: $status } },
          team: { id: { eq: $teamId } }
        }
      ) {
        nodes {
          id
          title
          description
          priority
          state {
            name
          }
          assignee {
            name
            email
          }
          url
          createdAt
          dueDate
        }
      }
    }
"""

GET_TEAM_BY_NAME = """
    query GetTeamId {
      teams {
        nodes {
          id
          name
        }
      }
    }
"""

GET_USER_BY_EMAIL = """
    query GetUserByEmail($email: String!) {
      users(filter: {email: {eq: $email}}) {
        nodes {
          id
        }
      }
    }
"""


GET_TEAM_STATES = """
    query GetTeamStates($teamId: String!) {
      team(id: $teamId) {
        states {
          nodes {
            id
            name
          }
        }
      }
    }
"""

CREATE_TEAM_ISSUE = """
    mutation CreateIssue($teamId: String!, $title: String!, $description: String!, $stateId: String!, $assigneeId: String) {
      issueCreate(
        input: {
          teamId: $teamId,
          title: $title,
          description: $description,
          stateId: $stateId,
          assigneeId: $assigneeId
        }
      ) {
        success
        issue {
          id
          title
          description
          priority
          state {
            name
          }
          assignee {
            name
            email
          }
          url
          createdAt
          dueDate
        }
      }
    }
"""

GET_USER_ISSUES = """
    query GetUserIssues($userId: String!) {
        user(id: $userId) {
            assignedIssues {
            nodes {
                id
                title
                description
                priority
                state {
                name
                }
                assignee {
                name
                email
                }
                url
                createdAt
                dueDate
            }
            }
        }
    }
"""
