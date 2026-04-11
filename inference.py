import asyncio
import os
import json
from typing import List, Optional
from openai import OpenAI
from client import SupportEnvClient
from models import SupportAction

# These environment variables are mandatory for the hackathon
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or "YOUR_API_KEY_HERE"
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
BENCHMARK = "customer_support_v1"
MAX_STEPS = 5

def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

async def run_task(client: OpenAI, env: SupportEnvClient, task_level: str):
    log_start(task=task_level, env=BENCHMARK, model=MODEL_NAME)
    
    # Load the specific difficulty level (Easy, Medium, or Hard)
    result = await env.reset(task_level=task_level)
    obs = result.observation
    
    rewards = []
    steps_taken = 0
    score = 0.0
    success = False
    
    system_prompt = "You are a customer support agent. Reply strictly in JSON format: {'tool_name': '...', 'tool_arg': '...'}"

    try:
        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break
            
            # Show the AI the current ticket
            user_prompt = f"Email: {obs.email_text}\nProfile: {obs.customer_profile}\nPolicy: {obs.policy_snippet}\nFeedback: {obs.feedback}\nChoose tool_name (reply, issue_refund, escalate) and tool_arg."
            
            # Ask the AI what to do
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            # Parse the AI's JSON response
            raw_response = completion.choices[0].message.content
            action_data = json.loads(raw_response)
            
            tool_n = action_data.get('tool_name', '')
            tool_a = action_data.get('tool_arg', '')
            action_str = f"{tool_n}('{tool_a}')"
            
            # Submit the AI's action to our OpenEnv server
            result = await env.step(SupportAction(tool_name=tool_n, tool_arg=tool_a))
            obs = result.observation
            reward = result.reward or 0.0
            
            rewards.append(reward)
            steps_taken = step
            log_step(step=step, action=action_str, reward=reward, done=result.done, error=None)

        score = max(0.0, sum(rewards))
        score = min(score, 1.0)
        success = score >= 1.0

    except Exception as e:
        print(f"[DEBUG] Run failed: {e}", flush=True)
        success = False
    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

async def main():
    # Set up the OpenAI client
    openai_client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    # Connect to our local OpenEnv server
    env = SupportEnvClient(base_url="http://localhost:8000")
    
    # Loop through all 3 tasks to prove they work!
    for task in ["easy", "medium", "hard"]:
        await run_task(openai_client, env, task)

if __name__ == "__main__":
    asyncio.run(main())