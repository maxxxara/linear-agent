from src.graph.state import State
def select_route(state: State):
    if state['next_node'] == 'fallback':
        return 'fallback_node'
    elif state['next_node'] == 'create_task':   
        return 'create_task_node'
    elif state['next_node'] == 'get_current_issues':
        return 'get_current_issues_node'
    elif state['next_node'] == 'get_user_issues':
        return 'get_user_issues_node'
    else:
        return 'fallback_node'

