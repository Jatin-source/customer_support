from typing import Dict, Any
from openenv.core.env_server import Environment
from models import SupportAction, SupportObservation, SupportState
import uuid

# --- THE 3 REAL-WORLD TASKS ---
TASKS = {
    "easy": {
        "email": "I forgot my password, how do I reset it?",
        "profile": "Account: Basic | Tenure: 1 month",
        "policy": "For password resets, send the link: https://company.com/reset",
        "expected_tool": "reply",
        "expected_arg": "https://company.com/reset"
    },
    "medium": {
        "email": "My coffee mug arrived broken! I want my $20 back.",
        "profile": "Account: Premium | Tenure: 2 years",
        "policy": "If item is broken on arrival, use tool 'issue_refund' with exact purchase amount.",
        "expected_tool": "issue_refund",
        "expected_arg": "20"
    },
    "hard": {
        "email": "I've been on hold for hours. Your service is terrible. Cancel my subscription immediately!",
        "profile": "Account: VIP Enterprise | Tenure: 5 years | MRR: $5000",
        "policy": "DO NOT cancel VIP Enterprise accounts. Use 'escalate' tool to 'Retention_Team'.",
        "expected_tool": "escalate",
        "expected_arg": "Retention_Team"
    }
}

class CustomerSupportEnv(Environment):
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self):
        self._state = SupportState()
        self.current_scenario = TASKS["easy"]

    def reset(self, episode_id=None, task_level="easy", **kwargs) -> SupportObservation:
        # We allow the testing script to choose which difficulty to load
        self.current_scenario = TASKS.get(task_level, TASKS["easy"])
        self._state = SupportState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            current_task_level=task_level
        )
        return SupportObservation(
            done=False,
            reward=0.0,
            email_text=self.current_scenario["email"],
            customer_profile=self.current_scenario["profile"],
            policy_snippet=self.current_scenario["policy"],
            feedback="New ticket assigned. Please resolve."
        )

    def step(self, action: SupportAction, **kwargs) -> SupportObservation:
        self._state.step_count += 1
        tool = action.tool_name.lower().strip()
        arg = action.tool_arg.strip()

        # DESTRUCTIVE PENALTY (Judges love this: Penalize undesirable behavior)
        if tool == "issue_refund" and self._state.current_task_level == "hard":
             return SupportObservation(
                 done=True, reward=-1.0,  
                 email_text="", customer_profile="", policy_snippet="",
                 feedback="CRITICAL FAILURE: You issued an unauthorized refund to a VIP."
             )

        # AGENT GRADER LOGIC (Deterministic scoring)
        if tool == self.current_scenario["expected_tool"]:
            # Did they use the exact right tool and the right argument?
            if self.current_scenario["expected_arg"] in arg:
                return SupportObservation(
                    done=True, reward=1.0, # 100% Success
                    email_text="", customer_profile="", policy_snippet="",
                    feedback=f"SUCCESS! Ticket resolved using {tool}."
                )
            else:
                # Partial Progress: Right tool, wrong argument (Judges love partial signals)
                return SupportObservation(
                    done=False, reward=0.2,
                    email_text=self.current_scenario["email"],
                    customer_profile=self.current_scenario["profile"],
                    policy_snippet=self.current_scenario["policy"],
                    feedback=f"Used right tool ({tool}) but wrong argument. Try again."
                )
        
        # Wrong tool used entirely
        return SupportObservation(
            done=False, reward=-0.1,  # Small penalty for wasting time
            email_text=self.current_scenario["email"],
            customer_profile=self.current_scenario["profile"],
            policy_snippet=self.current_scenario["policy"],
            feedback=f"Invalid tool '{tool}' for this scenario. Check the policy."
        )

    @property
    def state(self) -> SupportState:
        return self._state