from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult
from models import SupportAction, SupportObservation, SupportState

class SupportEnvClient(EnvClient[SupportAction, SupportObservation, SupportState]):
    
    def _step_payload(self, action: SupportAction) -> dict:
        # Converts our Pydantic action into a basic dictionary to send over the web
        return {
            "tool_name": action.tool_name, 
            "tool_arg": action.tool_arg
        }

    def _parse_result(self, payload: dict) -> StepResult:
        # Takes the web response and turns it back into our strict Pydantic Observation
        obs_data = payload.get("observation", {})
        return StepResult(
            observation=SupportObservation(
                done=payload.get("done", False),
                reward=payload.get("reward"),
                email_text=obs_data.get("email_text", ""),
                customer_profile=obs_data.get("customer_profile", ""),
                policy_snippet=obs_data.get("policy_snippet", ""),
                feedback=obs_data.get("feedback", "")
            ),
            reward=payload.get("reward"),
            done=payload.get("done", False)
        )

    def _parse_state(self, payload: dict) -> SupportState:
        # Tracks the background state
        return SupportState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            current_task_level=payload.get("current_task_level", "easy")
        )