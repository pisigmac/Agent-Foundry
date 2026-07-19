# Accessibility Auditor

An autonomous agent that audits web pages and applications for WCAG compliance, identifies accessibility issues, and provides remediation guidance with code fixes.

## Features

- **WCAG 2.1 Compliance**: Checks A, AA, and AAA level requirements
- **HTML Audit**: Alt text, form labels, headings, ARIA, skip links, language attributes
- **CSS Audit**: Color contrast, font sizes, motion preferences, focus styles
- **Code Fixes**: Specific HTML/CSS/JS fixes for each identified issue
- **Compliance Scoring**: Automated score calculation with severity weighting
- **Manual Review Flags**: Identifies issues requiring human judgment

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run accessibility_auditor.py
```

## Architecture

1. HTML/CSS content ingestion
2. LLM-powered WCAG guideline checking against content
3. Issue extraction with guideline references and severity scoring
4. Code fix generation for automated issues
5. Compliance score calculation and report generation

## License

MIT
