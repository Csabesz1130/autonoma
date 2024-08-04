from typing import Dict, List
from app.services.dynamic_model_chain import dynamic_model_chain
from app.schemas.task import TaskCreate

class InteractiveDebugging:
    @staticmethod
    async def debug_interactively(db, task: TaskCreate, result: Dict) -> Dict:
        issues = result.get("errors", []) + result.get("warnings", []) + result.get("style_issues", [])
        if not issues:
            return result

        refined_code = result["code"]
        for issue in issues:
            user_decision = await InteractiveDebugging._get_user_decision(issue)
            if user_decision == "fix":
                refined_code = await InteractiveDebugging._fix_issue(db, task, refined_code, issue)
            elif user_decision == "ignore":
                continue
            elif user_decision == "explain":
                explanation = await InteractiveDebugging._get_explanation(db, issue)
                print(f"Explanation for '{issue}':\n{explanation}")
            else:
                break

        return {**result, "code": refined_code}

    @staticmethod
    async def _get_user_decision(issue: str) -> str:
        print(f"Issue: {issue}")
        decision = input("Choose an action (fix/ignore/explain/stop): ").lower()
        while decision not in ["fix", "ignore", "explain", "stop"]:
            decision = input("Invalid choice. Please choose fix, ignore, explain, or stop: ").lower()
        return decision

    @staticmethod
    async def _fix_issue(db, task: TaskCreate, code: str, issue: str) -> str:
        fix_prompt = f"""
        The original task was: {task.description}

        The current code is:
        {code}

        Please fix the following issue in the code:
        {issue}

        Return only the fixed code without any explanations.
        """
        fix_result = await dynamic_model_chain.process_task(db, TaskCreate(description=fix_prompt))
        return fix_result["code"]

    @staticmethod
    async def _get_explanation(db, issue: str) -> str:
        explanation_prompt = f