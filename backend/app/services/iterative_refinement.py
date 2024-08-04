from typing import Dict, List
from app.schemas.task import TaskCreate
from app.services.dynamic_model_chain import dynamic_model_chain

class IterativeRefinement:
    @staticmethod
    async def refine_invalid_result(db, task: TaskCreate, invalid_result: Dict) -> Dict:
        refinement_steps = [
            IterativeRefinement._refine_syntax_errors,
            IterativeRefinement._refine_semantic_issues,
            IterativeRefinement._refine_style_issues,
        ]
        
        current_result = invalid_result
        for step in refinement_steps:
            if current_result["is_valid"]:
                break
            current_result = await step(db, task, current_result)
        
        return current_result

    @staticmethod
    async def _refine_syntax_errors(db, task: TaskCreate, result: Dict) -> Dict:
        if not result.get("errors"):
            return result
        
        refinement_prompt = f"""
        The original task was: {task.description}
        
        The generated code had the following syntax errors:
        {result['errors']}
        
        Please correct the code to address these syntax errors.
        """
        return await dynamic_model_chain.process_task(db, TaskCreate(description=refinement_prompt))

    @staticmethod
    async def _refine_semantic_issues(db, task: TaskCreate, result: Dict) -> Dict:
        if not result.get("warnings"):
            return result
        
        refinement_prompt = f"""
        The original task was: {task.description}
        
        The generated code had the following semantic issues:
        {result['warnings']}
        
        Please refactor the code to address these semantic issues.
        """
        return await dynamic_model_chain.process_task(db, TaskCreate(description=refinement_prompt))

    @staticmethod
    async def _refine_style_issues(db, task: TaskCreate, result: Dict) -> Dict:
        if not result.get("style_issues"):
            return result
        
        refinement_prompt = f"""
        The original task was: {task.description}
        
        The generated code had the following style issues:
        {result['style_issues']}
        
        Please refactor the code to adhere to Python style guidelines.
        """
        return await dynamic_model_chain.process_task(db, TaskCreate(description=refinement_prompt))

iterative_refinement = IterativeRefinement()