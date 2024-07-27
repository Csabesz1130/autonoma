import ast
import subprocess
from typing import Dict, List

def validate_python_syntax(code: str) -> List[str]:
    try:
        ast.parse(code)
        return []
    except SyntaxError as e:
        return [f"Syntax error at line {e.lineno}: {e.msg}"]

def run_pylint(code: str) -> List[str]:
    with open('temp.py', 'w') as f:
        f.write(code)
    
    result = subprocess.run(['pylint', 'temp.py'], capture_output=True, text=True)
    
    # Clean up
    subprocess.run(['rm', 'temp.py'])
    
    if result.returncode != 0:
        return result.stdout.split('\n')
    return []

def validate_code(code: str, language: str) -> Dict:
    if language.lower() == 'python':
        syntax_errors = validate_python_syntax(code)
        style_issues = run_pylint(code)
        is_valid = len(syntax_errors) == 0
        return {
            "is_valid": is_valid,
            "syntax_errors": syntax_errors,
            "style_issues": style_issues
        }
    else:
        # For other languages, you would implement similar validation logic
        return {"is_valid": True, "errors": ["Validation for this language is not implemented yet"]}

# Update the _validate_result method in TaskDistributor to use this function
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