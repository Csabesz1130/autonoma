import asyncio
from typing import List, Dict
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import aiohttp
from app.core.config import settings
from app.models.project import Project
from app.schemas.task import TaskCreate

nltk.download('punkt')
nltk.download('stopwords')

class TaskDistributor:
    def __init__(self):
        self.model_strengths = {
            "gpt-4": ["creativity", "general_understanding", "natural_language"],
            "claude": ["research", "analysis", "long_context"],
            "codex": ["code_generation", "debugging", "optimization"]
        }
        self.stop_words = set(stopwords.words('english'))

    async def process_task(self, task: TaskCreate, project: Project) -> Dict:
        preprocessed_input = self._preprocess_input(task.description)
        selected_models = self._select_models(preprocessed_input)
        results = await self._execute_task(selected_models, task, project)
        aggregated_result = self._aggregate_results(results)
        validated_result = self._validate_result(aggregated_result)
        return validated_result

    def _preprocess_input(self, input_text: str) -> List[str]:
        tokens = word_tokenize(input_text.lower())
        return [word for word in tokens if word.isalnum() and word not in self.stop_words]

    def _select_models(self, preprocessed_input: List[str]) -> List[str]:
        model_scores = {model: 0 for model in self.model_strengths.keys()}
        for word in preprocessed_input:
            for model, strengths in self.model_strengths.items():
                if word in strengths:
                    model_scores[model] += 1
        return [model for model, score in sorted(model_scores.items(), key=lambda x: x[1], reverse=True)][:2]

    async def _execute_task(self, models: List[str], task: TaskCreate, project: Project) -> Dict[str, str]:
        async with aiohttp.ClientSession() as session:
            tasks = [self._call_model(session, model, task, project) for model in models]
            results = await asyncio.gather(*tasks)
        return dict(zip(models, results))

    async def _call_model(self, session: aiohttp.ClientSession, model: str, task: TaskCreate, project: Project) -> str:
        api_url = f"{settings.AI_API_BASE_URL}/{model}"
        headers = {"Authorization": f"Bearer {settings.AI_API_KEY}"}
        data = {
            "task_type": task.task_type,
            "description": task.description,
            "project_context": project.description,
            "code_snippet": task.code_snippet
        }
        async with session.post(api_url, json=data, headers=headers) as response:
            if response.status == 200:
                return await response.text()
            else:
                return f"Error calling {model}: {response.status}"

    def _aggregate_results(self, results: Dict[str, str]) -> str:
        # Simple aggregation strategy: use the result from the highest-priority model
        return next(iter(results.values()))

    def _validate_result(self, result: str) -> Dict:
        # Placeholder for code validation logic
        is_valid = True
        errors = []
        return {"code": result, "is_valid": is_valid, "errors": errors}

task_distributor = TaskDistributor()