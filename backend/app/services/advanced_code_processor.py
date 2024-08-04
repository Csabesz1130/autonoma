import ast
import astroid
from typing import Dict, List
import subprocess
import tempfile
import os
from pylint import epylint as lint
from radon.complexity import cc_visit
from radon.metrics import mi_visit
import asyncio
from app.core.config import settings

class AdvancedCodeProcessor:
    @staticmethod
    async def aggregate_results(results: Dict[str, str]) -> str:
        combined_code = ""
        for model_output in results.values():
            combined_code += model_output + "\n\n"

        # Semantic analysis and code merging
        merged_code = await AdvancedCodeProcessor._merge_code(combined_code)

        # Conflict resolution
        resolved_code = await AdvancedCodeProcessor._resolve_conflicts(merged_code)

        # Quality assessment and improvement
        final_code = await AdvancedCodeProcessor._improve_code_quality(resolved_code)

        return final_code

    @staticmethod
    async def validate_result(code: str) -> Dict:
        is_valid = True
        errors = []
        warnings = []
        metrics = {}

        # Syntax checking
        syntax_errors = AdvancedCodeProcessor._check_syntax(code)
        if syntax_errors:
            is_valid = False
            errors.extend(syntax_errors)

        # Static analysis
        lint_results = await AdvancedCodeProcessor._run_linter(code)
        errors.extend(lint_results['errors'])
        warnings.extend(lint_results['warnings'])

        # Unit testing
        test_results = await AdvancedCodeProcessor._run_unit_tests(code)
        if not test_results["passed"]:
            is_valid = False
            errors.extend(test_results["errors"])

        # Performance analysis
        performance_issues, perf_metrics = await AdvancedCodeProcessor._analyze_performance(code)
        warnings.extend(performance_issues)
        metrics.update(perf_metrics)

        # Code complexity analysis
        complexity_metrics = AdvancedCodeProcessor._analyze_complexity(code)
        metrics.update(complexity_metrics)

        return {
            "code": code,
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "metrics": metrics
        }

    @staticmethod
    async def _merge_code(code: str) -> str:
        # This is a placeholder for more sophisticated code merging logic
        # In a real-world scenario, you might use a library like LibCST for code transformation
        return code

    @staticmethod
    async def _resolve_conflicts(code: str) -> str:
        # Placeholder for conflict resolution logic
        # This could involve analyzing the AST to detect and resolve naming conflicts
        tree = ast.parse(code)
        transformer = ConflictResolver()
        new_tree = transformer.visit(tree)
        return ast.unparse(new_tree)

    @staticmethod
    async def _improve_code_quality(code: str) -> str:
        # Placeholder for code quality improvement logic
        # This could involve using tools like Black for code formatting
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            subprocess.run(['black', temp_file_path], check=True)
            with open(temp_file_path, 'r') as file:
                improved_code = file.read()
            return improved_code
        finally:
            os.unlink(temp_file_path)

    @staticmethod
    def _check_syntax(code: str) -> List[str]:
        try:
            ast.parse(code)
            return []
        except SyntaxError as e:
            return [f"Syntax Error: {e}"]

    @staticmethod
    async def _run_linter(code: str) -> Dict[str, List[str]]:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            (pylint_stdout, pylint_stderr) = lint.py_run(temp_file_path, return_std=True)
            errors = []
            warnings = []
            for line in pylint_stdout:
                if 'error' in line.lower():
                    errors.append(line.strip())
                elif 'warning' in line.lower():
                    warnings.append(line.strip())
            return {"errors": errors, "warnings": warnings}
        finally:
            os.unlink(temp_file_path)

    @staticmethod
    async def _run_unit_tests(code: str) -> Dict:
        # This is a placeholder for running unit tests
        # In a real-world scenario, you would need to set up a testing framework and generate tests
        return {"passed": True, "errors": []}

    @staticmethod
    async def _analyze_performance(code: str) -> Tuple[List[str], Dict]:
        issues = []
        metrics = {}

        # Use the cProfile module to get performance metrics
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            prof = cProfile.Profile()
            prof.run(f'exec(open("{temp_file_path}").read())')
            stats = pstats.Stats(prof)
            stats.sort_stats('cumulative')
            
            # Get the top 10 time-consuming functions
            top_stats = stats.stats.items()
            sorted_stats = sorted(top_stats, key=lambda x: x[1][2], reverse=True)[:10]
            
            for func, (cc, nc, tt, ct, callers) in sorted_stats:
                if ct > 0.1:  # If cumulative time is more than 0.1 seconds
                    issues.append(f"Performance issue: Function {func} takes {ct:.2f} seconds")
                metrics[func] = ct

        finally:
            os.unlink(temp_file_path)

        return issues, metrics

    @staticmethod
    def _analyze_complexity(code: str) -> Dict:
        # Analyze code complexity using radon
        complexity = cc_visit(code)
        maintainability = mi_visit(code, multi=True)
        
        metrics = {
            "cyclomatic_complexity": sum(cc.complexity for cc in complexity),
            "maintainability_index": maintainability
        }
        
        return metrics

class ConflictResolver(ast.NodeTransformer):
    def __init__(self):
        self.defined_names = set()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            if node.id in self.defined_names:
                new_name = f"{node.id}_{len(self.defined_names)}"
                self.defined_names.add(new_name)
                return ast.Name(id=new_name, ctx=node.ctx)
            self.defined_names.add(node.id)
        return node

advanced_code_processor = AdvancedCodeProcessor()