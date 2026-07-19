# Content Moderation Agent

An autonomous agent that moderates user-generated content across platforms, detects policy violations, classifies severity, and handles appeals with explanation generation.

## Features

- **Multi-Category Detection**: Hate speech, harassment, misinformation, spam, self-harm, violence, sexual content, copyright, impersonation, manipulation
- **Severity Classification**: Critical, high, medium, low, none with harm-based assessment
- **Action Determination**: Remove, hide, warn, flag, escalate, approve, shadowban
- **Appeal Review**: Automated appeal processing with overturn/confirm decisions
- **Policy References**: Specific policy section citations for transparency
- **Human Review Flags**: Automatic escalation for borderline cases
- **Confidence Scoring**: Decision confidence with uncertainty quantification

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run content_moderation_agent.py
```

## Architecture

1. Content ingestion with type detection (text, image, video, audio)
2. Multi-category policy violation analysis via LLM
3. Severity classification based on harm potential, reach, and intent
4. Action recommendation with confidence scoring
5. Appeal review with decision overturn/confirm logic
6. Explanation generation for all decisions

## License

Apache-2.0
