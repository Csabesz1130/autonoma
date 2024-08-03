import pytest
from unittest.mock import Mock, patch
from app.services.task_distributor import TaskDistributor
from app.schemas.task import TaskCreate

@pytest.fixture
def task_distributor():
    return TaskDistributor()

@pytest.mark.asyncio
async def test_select_models(task_distributor):
    description = "Optimize this Python code for better performance"
    selected_models = task_distributor._select_models(description)
    assert len(selected_models) == 2
    assert "codex" in selected_models  # Codex should be selected for code optimization

@pytest.mark.asyncio
async def test_process_task(task_distributor):
    mock_db = Mock()
    mock_task = TaskCreate(description="Create a Python function to calculate fibonacci numbers", code_snippet="")
    
    with patch.object(task_distributor, '_execute_task') as mock_execute:
        mock_execute.return_value = {
            "codex": "```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)\n```",
            "gpt4": "Here's a Python function to calculate Fibonacci numbers:\n\n```python\ndef fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a\n```"
        }
        
        result = await task_distributor.process_task(mock_db, mock_task)
        
        assert result["is_valid"]
        assert "fibonacci" in result["code"]

@pytest.mark.asyncio
async def test_validate_result(task_distributor):
    valid_code = "```python\ndef greet(name):\n    return f'Hello, {name}!'\n```"
    invalid_code = "```python\ndef greet(name)\n    return f'Hello, {name}!'\n```"
    
    valid_result = task_distributor._validate_result(valid_code)
    invalid_result = task_distributor._validate_result(invalid_code)
    
    assert valid_result["is_valid"]
    assert not invalid_result["is_valid"]
    assert "SyntaxError" in str(invalid_result["errors"])

# Add more tests for other methods...