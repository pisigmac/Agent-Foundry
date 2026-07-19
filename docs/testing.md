# Testing Guide

Every template includes a test script. Run it after setup:

```bash
python test.py
```

## Test Categories

1. **Unit Tests**: Individual agent reasoning steps
2. **Integration Tests**: Agent + tool interactions
3. **End-to-End Tests**: Full user workflow
4. **Load Tests**: Concurrent agent execution

## Writing Tests

Use the `test.py` in any template as a reference:

```python
from agent import Assistant

def test_reasoning():
    assistant = Assistant()
    result = assistant.handle_request("What is 2+2?")
    assert "4" in result

def test_tool_call():
    assistant = Assistant()
    result = assistant.handle_request("Search for Python")
    assert result is not None
```

## CI/CD

Add this to your `.github/workflows/test.yml`:

```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python test.py
```
