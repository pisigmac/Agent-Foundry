# API Testing Agent

An autonomous agent that generates test cases, executes API requests, validates responses, and reports coverage gaps for REST and GraphQL APIs.

## Features

- **Test Generation**: AI-powered test case creation from endpoint descriptions and schemas
- **Multi-Type Coverage**: Positive, negative, edge case, security, and performance tests
- **Schema Validation**: Request/response schema conformance checking
- **Coverage Analysis**: Endpoint and test type coverage gap identification
- **Execution Simulation**: Simulated test execution with timing and status tracking
- **Assertion Management**: Automated assertion generation for response validation

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run api_testing_agent.py
```

## Architecture

1. Endpoint description and schema ingestion
2. LLM-powered multi-type test case generation
3. Test execution simulation with response validation
4. Coverage analysis across endpoints and test types
5. Gap identification and additional test recommendations

## License

Apache-2.0
