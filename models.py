from openenv.core.env_server import Action, Observation, State

# 1. THE ACTION SPACE (What the AI can do)
class SupportAction(Action):
    tool_name: str  # The AI must choose: "reply", "issue_refund", or "escalate"
    tool_arg: str   # The argument: e.g., "https://reset.link", "20", or "Retention_Team"

# 2. THE OBSERVATION SPACE (What the AI sees)
class SupportObservation(Observation):
    # 'done' and 'reward' are automatically handled by OpenEnv
    email_text: str
    customer_profile: str
    policy_snippet: str
    feedback: str  # We use this to tell the AI if its last action failed or succeeded

# 3. THE STATE (Background tracking)
class SupportState(State):
    current_task_level: str = "easy"