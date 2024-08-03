import ast
import subprocess
from typing import Dict, List
import tempfile
import os

class CodeValidator:
    @staticmethod
    def validate_result(result: Dict) -> Dict:
        if "code" not in result or not result["code"]:
            result["is_valid"] = False
            result["errors"] = ["No code generated in the result"]
            return result

        code = result["code"]
        syntax_errors = CodeValidator.check_syntax(code)
        semantic_issues = CodeValidator.run_semantic_tests(code)

        result["is_valid"] = len(syntax_errors) == 0 and len(semantic_issues) == 0
        result["errors"] = syntax_errors
        result["warnings"] = semantic_issues

        return result

    @staticmethod
    def check_syntax(code: str) -> List[str]:
        try:
            ast.parse(code)
            return []
        except SyntaxError as e:
            return [f"Syntax error at line {e.lineno}: {e.msg}"]

    @staticmethod
    def run_semantic_tests(code: str) -> List[str]:
        issues = []

        # Check for undefined variables
        tree = ast.parse(code)
        defined_vars = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    defined_vars.add(node.id)
                elif isinstance(node.ctx, ast.Load) and node.id not in defined_vars:
                    issues.append(f"Potentially undefined variable: {node.id}")

        # Run static type checking with mypy
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            result = subprocess.run(['mypy', temp_file_path], capture_output=True, text=True)
            if result.returncode != 0:
                issues.extend(result.stdout.splitlines())
        finally:
            os.unlink(temp_file_path)

        return issues

    @staticmethod
    def run_code_with_timeout(code: str, timeout: int = 5) -> Dict:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            result = subprocess.run(['python', temp_file_path], capture_output=True, text=True, timeout=timeout)
            return {
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "output": "",
                "errors": f"Code execution timed out after {timeout} seconds",
                "return_code": -1
            }
        finally:
            os.unlink(temp_file_path)

code_validator = CodeValidator()