# Translation & Localization Agent

An autonomous agent that translates content, adapts cultural references, localizes UI strings, and maintains terminology consistency across languages.

## Features

- **Multi-Language Translation**: 11+ languages with quality scoring
- **Cultural Adaptation**: Idioms, metaphors, and cultural references adapted for target audiences
- **UI Localization**: Length constraints, truncation handling, formal/informal register
- **Terminology Consistency**: Glossary management and cross-batch consistency checks
- **Back-Translation**: Verification through reverse translation
- **Batch Processing**: Bulk translation with consistency validation
- **Quality Assessment**: Automated quality scoring with issue detection

## Content Types

UI strings, marketing, technical, legal, medical, casual, formal

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run translation_localization_agent.py
```

## Architecture

1. Text ingestion with content type and language pair specification
2. LLM-powered translation with cultural context awareness
3. Back-translation verification for quality assurance
4. Terminology glossary extraction and consistency checking
5. Batch processing with cross-text consistency validation
6. Quality scoring and issue reporting

## License

MIT
