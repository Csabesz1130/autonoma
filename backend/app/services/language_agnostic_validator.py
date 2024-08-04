import subprocess
from typing import Dict, List
import tempfile
import os

class LanguageAgnosticValidator:
    @staticmethod
    def validate_code(code: str, language: str) -> Dict:
        validator = LanguageValidatorFactory.get_validator(language)
        return validator.validate(code)

class LanguageValidatorFactory:
    @staticmethod
    def get_validator(language: str):
        if language.lower() == 'python':
            return PythonValidator()
        elif language.lower() == 'javascript':
            return JavaScriptValidator()
        # Add more language validators as needed
        else:
            raise ValueError(f"Unsupported language: {language}")

class LanguageValidator:
    def validate(self, code: str) -> Dict:
        raise NotImplementedError

class PythonValidator(LanguageValidator):
    def validate(self, code: str) -> Dict:
        syntax_errors = self.check_syntax(code)
        style_issues = self.check_style(code)
        return {
            "is_valid": len(syntax_errors) == 0,
            "errors": syntax_errors,
            "style_issues": style_issues
        }

    def check_syntax(self, code: str) -> List[str]:
        try:
            compile(code, '<string>', 'exec')
            return []
        except SyntaxError as e:
            return [f"Syntax error at line {e.lineno}: {e.msg}"]

    def check_style(self, code: str) -> List[str]:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            result = subprocess.run(['flake8', temp_file_path], capture_output=True, text=True)
            return result.stdout.splitlines()
        finally:
            os.unlink(temp_file_path)

class JavaScriptValidator(LanguageValidator):
    def validate(self, code: str) -> Dict:
        syntax_errors = self.check_syntax(code)
        style_issues = self.check_style(code)
        return {
            "is_valid": len(syntax_errors) == 0,
            "errors": syntax_errors,
            "style_issues": style_issues
        }

    def check_syntax(self, code: str) -> List[str]:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            result = subprocess.run(['node', '--check', temp_file_path], capture_output=True, text=True)
            return result.stderr.splitlines() if result.returncode != 0 else []
        finally:
            os.unlink(temp_file_path)

    def check_style(self, code: str) -> List[str]:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            result = subprocess.run(['eslint', temp_file_path], capture_output=True, text=True)
            return result.stdout.splitlines()
        finally:
            os.unlink(temp_file_path)

language_agnostic_validator = LanguageAgnosticValidator()