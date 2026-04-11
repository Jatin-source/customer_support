---
title: Customer Support Env
emoji: 🏢
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Customer Support Escalation Desk (OpenEnv)

## Environment Description & Motivation
This environment simulates a real-world Customer Support triage desk. Resolving customer support tickets accurately is a highly valuable, deterministic task that challenges an LLM's ability to read policies, analyze user metadata, and execute specific tool-calling actions. It moves beyond standard chat by forcing strict tool usage and penalizing destructive actions (like unauthorized VIP refunds).

## Action and Observation Spaces
* **Action Space:** The agent must output two strings: `tool_name` (must be `reply`, `issue_refund`, or `escalate`) and `tool_arg` (the argument for the tool, such as a URL, dollar amount, or department name).
* **Observation Space:** The agent observes the `email_text` from the customer, the `customer_profile` (account tenure/tier), a `policy_snippet` detailing the company rules, and `feedback` from previous actions.

## Tasks & Difficulty
This environment features 3 tasks with an automated agent grader:
1. **Easy:** Password Reset. The agent must read the policy and use the `reply` tool with the exact reset URL.
2. **Medium:** Product Refund. The agent must verify the customer profile and use the `issue_refund` tool with the correct dollar amount.
3. **Hard:** VIP Escalation. The agent must recognize a high-value customer threatening to churn, ignore the demand to cancel the account, and use the `escalate` tool to alert the Retention Team. (Destructive penalty applied if a refund is issued instead).

## Setup and Usage Instructions
1. Clone this repository and install dependencies: `pip install openenv-core uvicorn fastapi pydantic openai`
2. Start the local server: `python -m uvicorn server.app:app --port 8000`
3. Export your Hugging Face API key: `export HF_TOKEN="your_token_here"` (Linux/Mac) or `$env:HF_TOKEN="your_token_here"` (Windows).
4. Run the inference baseline: `python inference.py`

## Baseline Scores
Using `Qwen/Qwen2.5-72B-Instruct` via Hugging Face routing:
* **Easy:** 1.000 (Success)
* **Medium:** 1.000 (Success)
* **Hard:** 1.000 (Success)