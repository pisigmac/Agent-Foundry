# Code Review Assistant

An autonomous agent that reviews pull requests, detects issues, suggests improvements, and generates review comments.

## Features

- **Multi-Language Support**: Python, JavaScript, TypeScript, Java, Go, Rust, C++
- **Severity Scoring**: Critical, High, Medium, Low, Info
- **GitHub Integration**: Fetch PR diffs directly (optional)
- **Diff Parsing**: Extract changed lines from git diffs

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run code_review_assistant.py
```

## Architecture

1. Code ingestion (paste or GitHub PR)
2. Multi-category analysis (bugs, security, performance, style)
3. Severity scoring and ranking
4. Structured output with line-specific suggestions

## License

MIT
