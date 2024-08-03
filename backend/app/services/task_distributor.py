import asyncio
from typing import List, Dict
import aiohttp
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.task import Task
from app.schemas.task import TaskCreate
from app.services.cache_service import cache_result
from app.services.error_handling import call_api_with_retry, APIError
from app.services.result_aggregator import aggregate_results
from app.services.code_validator import validate_code, extract_code_blocks
from app.services.feedback_loop import feedback_loop
from app.services.api_usage_tracker import api_usage_tracker

class TaskDistributor:
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

    @cache_result(expire_time=3600)
    async def process_task(self, db: Session, task: TaskCreate) -> Dict:
        selected_models = self._select_models(task.description)
        results = await self._execute_task(db, selected_models, task)
        aggregated_result = self._aggregate_results(results)
        validated_result = self._validate_result(aggregated_result)
        return validated_result

    def _select_models(self, description: str) -> List[str]:
        model_scores = {model: 0 for model in self.models.keys()}
        for word in description.lower().split():
            for model, info in self.models.items():
                if word in info["strengths"]:
                    model_scores[model] += 1 * feedback_loop.get_model_weight(model)
        
        selected_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        return [model for model, _ in selected_models[:2]]

    async def _execute_task(self, db: Session, models: List[str], task: TaskCreate) -> Dict[str, str]:
        async with aiohttp.ClientSession() as session:
            tasks = [self._call_model(db, session, model, task) for model in models]
            results = await asyncio.gather(*tasks)
        return dict(zip(models, results))

    async def _call_model(self, db: Session, session: aiohttp.ClientSession, model: str, task: TaskCreate) -> str:
        model_info = self.models[model]
        headers = {"Authorization": f"Bearer {model_info['api_key']}"}
        data = {
            "model": model_info["name"],
            "messages": [
                {"role": "system", "content": "You are an AI assistant specialized in coding tasks."},
                {"role": "user", "content": f"Task: {task.description}\nCode snippet: {task.code_snippet}"}
            ]
        }
        try:
            response = await call_api_with_retry(session, model_info["api_url"], headers, data, model_info["name"])
            tokens_used = response["usage"]["total_tokens"]
            cost = self._calculate_cost(model, tokens_used)
            api_usage_tracker.log_usage(db, model, tokens_used, cost)
            return response["choices"][0]["message"]["content"]
        except APIError as e:
            return f"Error: {str(e)}"

    def _aggregate_results(self, results: Dict[str, str]) -> str:
        return aggregate_results(results)

    def _validate_result(self, result: str) -> Dict:
        code_blocks = extract_code_blocks(result)
        if not code_blocks:
            return {"is_valid": False, "errors": ["No code block found in the result"]}
        
        # Assume Python for now. In a real scenario, you'd detect or specify the language.
        validation_result = validate_code(code_blocks[0], 'python')
        return {
            "code": result,
            "is_valid": validation_result["is_valid"],
            "errors": validation_result.get("syntax_errors", []) + validation_result.get("style_issues", [])
        }

    def _calculate_cost(self, model: str, tokens: int) -> float:
        # Implement cost calculation based on the pricing of each model
        # This is a placeholder implementation
        cost_per_token = {
            "claude": 0.00002,
            "gpt4": 0.00003,
            "codex": 0.00001
        }
        return tokens * cost_per_token.get(model, 0.00001)

    def update_model_weights(self, db: Session):
        feedback_loop.update_weights(db)

task_distributor = TaskDistributor()