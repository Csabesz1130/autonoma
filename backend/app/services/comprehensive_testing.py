import ast
import asyncio
from typing import List, Dict
from app.services.dynamic_model_chain import dynamic_model_chain
from app.schemas.task import TaskCreate

class ComprehensiveTesting:
    @staticmethod
    async def generate_and_run_tests(db, task: TaskCreate, code: str) -> Dict:
        test_cases = await ComprehensiveTesting._generate_test_cases(db, task, code)
        test_results = await ComprehensiveTesting._run_tests(code, test_cases)
        return {
            "test_cases": test_cases,
            "test_results": test_results,
            "all_tests_passed": all(result["passed"] for result in test_results)
        }

    @staticmethod
    async def _generate_test_cases(db, task: TaskCreate, code: str) -> List[Dict]:
        function_names = ComprehensiveTesting._extract_function_names(code)
        test_case_prompts = [
            f"Generate a test case for the function '{func_name}' in the following code:\n\n{code}\n\nProvide the test case in the format: {{\"input\": ..., \"expected_output\": ...}}"
            for func_name in function_names
        ]
        
        test_cases = []
        for prompt in test_case_prompts:
            test_case_result = await dynamic_model_chain.process_task(db, TaskCreate(description=prompt))
            try:
                test_case = eval(test_case_result["code"])
                test_cases.append(test_case)
            except:
                # If there's an error in parsing the test case, skip it
                continue
        
        return test_cases

    @staticmethod
    def _extract_function_names(code: str) -> List[str]:
        tree = ast.parse(code)
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    @staticmethod
    async def _run_tests(code: str, test_cases: List[Dict]) -> List[Dict]:
        # This is a simplified version. In a real-world scenario, you'd need to handle different types of inputs and outputs,
        # as well as potential security issues with executing arbitrary code.
        test_results = []
        for test_case in test_cases:
            test_code = f"""
{code}

result = {test_case['input']}
expected = {test_case['expected_output']}
print(result == expected)
"""
            process = await asyncio.create_subprocess_exec(
                'python', '-c', test_code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            passed = stdout.decode().strip() == 'True'
            test_results.append({
                "input": test_case['input'],
                "expected_output": test_case['expected_output'],
                "passed": passed,
                "error": stderr.decode() if stderr else None
            })
        
        return test_results

comprehensive_testing = ComprehensiveTesting()import ast
import asyncio
from typing import List, Dict
from app.services.dynamic_model_chain import dynamic_model_chain
from app.schemas.task import TaskCreate

class ComprehensiveTesting:
    @staticmethod
    async def generate_and_run_tests(db, task: TaskCreate, code: str) -> Dict:
        test_cases = await ComprehensiveTesting._generate_test_cases(db, task, code)
        test_results = await ComprehensiveTesting._run_tests(code, test_cases)
        return {
            "test_cases": test_cases,
            "test_results": test_results,
            "all_tests_passed": all(result["passed"] for result in test_results)
        }

    @staticmethod
    async def _generate_test_cases(db, task: TaskCreate, code: str) -> List[Dict]:
        function_names = ComprehensiveTesting._extract_function_names(code)
        test_case_prompts = [
            f"Generate a test case for the function '{func_name}' in the following code:\n\n{code}\n\nProvide the test case in the format: {{\"input\": ..., \"expected_output\": ...}}"
            for func_name in function_names
        ]
        
        test_cases = []
        for prompt in test_case_prompts:
            test_case_result = await dynamic_model_chain.process_task(db, TaskCreate(description=prompt))
            try:
                test_case = eval(test_case_result["code"])
                test_cases.append(test_case)
            except:
                # If there's an error in parsing the test case, skip it
                continue
        
        return test_cases

    @staticmethod
    def _extract_function_names(code: str) -> List[str]:
        tree = ast.parse(code)
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    @staticmethod
    async def _run_tests(code: str, test_cases: List[Dict]) -> List[Dict]:
        # This is a simplified version. In a real-world scenario, you'd need to handle different types of inputs and outputs,
        # as well as potential security issues with executing arbitrary code.
        test_results = []
        for test_case in test_cases:
            test_code = f"""
{code}

result = {test_case['input']}
expected = {test_case['expected_output']}
print(result == expected)
"""
            process = await asyncio.create_subprocess_exec(
                'python', '-c', test_code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            passed = stdout.decode().strip() == 'True'
            test_results.append({
                "input": test_case['input'],
                "expected_output": test_case['expected_output'],
                "passed": passed,
                "error": stderr.decode() if stderr else None
            })
        
        return test_results

comprehensive_testing = ComprehensiveTesting()