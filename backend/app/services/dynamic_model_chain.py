import asyncio
from typing import List, Dict
import aiohttp
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.task import Task
from app.schemas.task import TaskCreate, SubTask
from app.services.error_handling import call_api_with_retry, APIError
from app.services.api_usage_tracker import api_usage_tracker

class DynamicModelChain:
    def __init__(self):
        self.models = {
            "claude": {
                "name": "Claude 3.5 Sonnet",
                "api_url": settings.CLAUDE_API_URL,
                "api_key": settings.CLAUDE_API_KEY,
                "strengths": ["research", "analysis", "long_context", "natural_language"]
            },
            "gpt4": {
                "name": "GPT-4",
                "api_url": settings.GPT4_API_URL,
                "api_key": settings.GPT4_API_KEY,
                "strengths": ["creativity", "general_understanding", "complex_reasoning"]
            },
            "codex": {
                "name": "Codex (or latest OpenAI coding model)",
                "api_url": settings.CODEX_API_URL,
                "api_key": settings.OPENAI_API_KEY,
                "strengths": ["code_generation", "debugging", "optimization"]
            }
        }

    async def process_task(self, db: Session, task: TaskCreate) -> Dict:
        subtasks = await self.analyze_and_break_down_task(task)
        subtask_results = await asyncio.gather(*[self.process_subtask(db, st) for st in subtasks])
        final_result = await self.compile_results(db, subtask_results, task)
        return final_result

    async def analyze_and_break_down_task(self, task: TaskCreate) -> List[SubTask]:
        # Use GPT-4 to break down the task into subtasks
        analysis_prompt = f"Break down the following coding task into subtasks:\n\nTask: {task.description}\nCode snippet: {task.code_snippet}\n\nProvide a list of subtasks, each with a brief description and the most suitable AI model (Claude, GPT-4, or Codex) to handle it."
        analysis_result = await self._call_model(None, "gpt4", analysis_prompt)
        
        # Parse the analysis result to create SubTask objects
        # This is a simplified parsing, you might need to implement a more robust parser
        subtasks = []
        for line in analysis_result.split('\n'):
            if ':' in line:
                subtask_desc, model = line.split(':')
                subtasks.append(SubTask(description=subtask_desc.strip(), model=model.strip().lower()))
        
        return subtasks

    async def process_subtask(self, db: Session, subtask: SubTask) -> str:
        return await self._call_model(db, subtask.model, subtask.description)

    async def compile_results(self, db: Session, subtask_results: List[str], original_task: TaskCreate) -> Dict:
        compilation_prompt = f"Original task: {original_task.description}\n\nSubtask results:\n" + "\n".join(subtask_results) + "\n\nCompile these results into a coherent solution, providing any necessary explanations or additional code."
        compiled_result = await self._call_model(db, "gpt4", compilation_prompt)
        
        return {
            "code": compiled_result,
            "explanation": "This solution was compiled from multiple AI model outputs.",
            "subtask_results": subtask_results
        }

    async def _call_model(self, db: Session, model: str, prompt: str) -> str:
        model_info = self.models[model]
        headers = {"Authorization": f"Bearer {model_info['api_key']}"}
        data = {
            "model": model_info["name"],
            "messages": [
                {"role": "system", "content": "You are an AI assistant specialized in coding tasks."},
                {"role": "user", "content": prompt}
            ]
        }
        async with aiohttp.ClientSession() as session:
            try:
                response = await call_api_with_retry(session, model_info["api_url"], headers, data, model_info["name"])
                tokens_used = response["usage"]["total_tokens"]
                response_tokens = response["usage"].get("completion_tokens", 0)
                cost = self._calculate_cost(model, tokens_used, response_tokens)
                if db:  # Only log usage if db session is provided
                    api_usage_tracker.log_usage(db, model, tokens_used, cost)
                return response["choices"][0]["message"]["content"]
            except APIError as e:
                return f"Error: {str(e)}"

    def _calculate_cost(self, model: str, tokens_used: int, response_tokens: int) -> float:
        prompt_tokens = tokens_used - response_tokens

        # Pricing details as per your provided calculations
        cost_per_token = {
            "claude": 0.011 / 1000,  # $0.011 per 1,000 tokens
            "gpt4_prompt": 0.03 / 1000,  # $0.03 per 1,000 prompt tokens
            "gpt4_completion": 0.06 / 1000,  # $0.06 per 1,000 completion tokens
            "codex_prompt": 0.02 / 1000,  # $0.02 per 1,000 prompt tokens
            "codex_completion": 0.04 / 1000,  # $0.04 per 1,000 completion tokens
        }

        if model == "claude":
            return tokens_used * cost_per_token["claude"]
        elif model == "gpt4":
            return prompt_tokens * cost_per_token["gpt4_prompt"] + response_tokens * cost_per_token["gpt4_completion"]
        elif model == "codex":
            return prompt_tokens * cost_per_token["codex_prompt"] + response_tokens * cost_per_token["codex_completion"]
        else:
            return 0.0

dynamic_model_chain = DynamicModelChain()