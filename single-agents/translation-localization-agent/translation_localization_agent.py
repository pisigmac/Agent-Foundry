"""
Translation & Localization Agent

An autonomous agent that translates content, adapts cultural references,
localizes UI strings, and maintains terminology consistency across languages.
"""

import os
import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import streamlit as st
from agno.assistant import Assistant
from agno.models.openai import OpenAIChat
import pandas as pd


class ContentType(Enum):
    UI_STRING = "ui_string"
    MARKETING = "marketing"
    TECHNICAL = "technical"
    LEGAL = "legal"
    MEDICAL = "medical"
    CASUAL = "casual"
    FORMAL = "formal"


class TranslationQuality(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    NEEDS_REVIEW = "needs_review"


@dataclass
class TranslationResult:
    source_text: str
    translated_text: str
    source_language: str
    target_language: str
    content_type: ContentType
    cultural_adaptations: List[str]
    terminology_glossary: Dict[str, str]
    quality_score: float
    quality_rating: TranslationQuality
    back_translation: str
    consistency_check: bool
    issues: List[str]


@dataclass
class LocalizationContext:
    locale: str
    region: str
    currency: str
    date_format: str
    number_format: str
    cultural_notes: List[str]
    forbidden_terms: List[str]
    preferred_terms: Dict[str, str]


class TranslationLocalizationAgent:
    """
    Primary entry point for translation, cultural adaptation, and localization.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.assistant = Assistant(
            model=OpenAIChat(id="gpt-4o", api_key=api_key),
            description="Translation, cultural adaptation, UI localization, and terminology consistency management",
            instructions=[
                "Translate content while preserving meaning, tone, and intent across languages",
                "Adapt cultural references, idioms, and metaphors for target audiences",
                "Localize UI strings with proper length constraints and truncation handling",
                "Maintain terminology consistency using glossaries and style guides"
            ]
        )
        self.glossaries: Dict[str, Dict[str, str]] = {}

    def translate(self, text: str, source_lang: str, target_lang: str,
                  content_type: ContentType = ContentType.UI_STRING,
                  context: Optional[LocalizationContext] = None) -> TranslationResult:
        """
        Translate text with cultural adaptation and quality checks.
        """
        context_text = ""
        if context:
            context_text = f"""
            Localization Context:
            - Region: {context.region}
            - Currency: {context.currency}
            - Date format: {context.date_format}
            - Cultural notes: {', '.join(context.cultural_notes)}
            - Preferred terms: {json.dumps(context.preferred_terms)}
            - Forbidden terms: {', '.join(context.forbidden_terms)}
            """

        prompt = f"""
        Translate this {content_type.value} content from {source_lang} to {target_lang}:

        Source text: "{text}"

        {context_text}

        Requirements:
        1. Preserve the exact meaning, tone, and intent
        2. Adapt cultural references, idioms, and metaphors for {target_lang} speakers
        3. For UI strings: ensure proper length, handle truncation gracefully
        4. Use formal/informal register appropriately for the content type
        5. Maintain consistency with provided terminology
        6. Identify any terms that need glossary entries

        Provide:
        1. Translated text
        2. Cultural adaptations made (list)
        3. Terminology glossary used (key-value pairs)
        4. Quality assessment (excellent/good/fair/poor/needs_review)
        5. Quality score (0-100)
        6. Back-translation to source language for verification
        7. Any issues or concerns

        Respond in JSON format:
        {{
            "translated_text": "<translation>",
            "cultural_adaptations": ["<adaptation1>", "<adaptation2>"],
            "terminology_glossary": {{"<term>": "<translation>"}},
            "quality_rating": "<rating>",
            "quality_score": <number>,
            "back_translation": "<back-translation>",
            "issues": ["<issue1>", "<issue2>"]
        }}
        """

        response = self.assistant.run(prompt)
        content = response.content

        try:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)

            return TranslationResult(
                source_text=text,
                translated_text=data.get("translated_text", ""),
                source_language=source_lang,
                target_language=target_lang,
                content_type=content_type,
                cultural_adaptations=data.get("cultural_adaptations", []),
                terminology_glossary=data.get("terminology_glossary", {}),
                quality_score=data.get("quality_score", 50),
                quality_rating=TranslationQuality(data.get("quality_rating", "needs_review")),
                back_translation=data.get("back_translation", ""),
                consistency_check=True,
                issues=data.get("issues", [])
            )
        except (json.JSONDecodeError, ValueError):
            return TranslationResult(
                source_text=text,
                translated_text="[Translation error]",
                source_language=source_lang,
                target_language=target_lang,
                content_type=content_type,
                cultural_adaptations=[],
                terminology_glossary={},
                quality_score=0,
                quality_rating=TranslationQuality.NEEDS_REVIEW,
                back_translation="",
                consistency_check=False,
                issues=["Translation failed - please retry"]
            )

    def batch_translate(self, texts: List[str], source_lang: str, target_lang: str,
                       content_type: ContentType = ContentType.UI_STRING) -> List[TranslationResult]:
        """
        Translate a batch of texts with consistency checks.
        """
        results = []

        for text in texts:
            result = self.translate(text, source_lang, target_lang, content_type)
            results.append(result)

        # Consistency check across batch
        all_glossaries = {}
        for r in results:
            all_glossaries.update(r.terminology_glossary)

        # Check for inconsistent translations
        for i, result in enumerate(results):
            for term, translation in all_glossaries.items():
                if term in result.source_text and translation not in result.translated_text:
                    result.issues.append(f"Terminology inconsistency: '{term}' should be '{translation}'")
                    result.consistency_check = False

        return results

    def handle_request(self, text: str, source_lang: str, target_lang: str,
                      content_type: str = "ui_string",
                      batch_texts: Optional[List[str]] = None) -> Dict:
        """
        Process a translation request.
        """
        ct = ContentType(content_type)

        if batch_texts:
            results = self.batch_translate(batch_texts, source_lang, target_lang, ct)
            return {
                "type": "batch_translation",
                "source_language": source_lang,
                "target_language": target_lang,
                "content_type": content_type,
                "translations": [{
                    "source": r.source_text,
                    "translated": r.translated_text,
                    "quality_score": r.quality_score,
                    "quality_rating": r.quality_rating.value,
                    "cultural_adaptations": r.cultural_adaptations,
                    "issues": r.issues,
                    "consistent": r.consistency_check
                } for r in results],
                "average_quality": sum(r.quality_score for r in results) / len(results) if results else 0,
                "consistency_issues": sum(1 for r in results if not r.consistency_check)
            }
        else:
            result = self.translate(text, source_lang, target_lang, ct)

            return {
                "type": "translation",
                "source_text": result.source_text,
                "translated_text": result.translated_text,
                "source_language": result.source_language,
                "target_language": result.target_language,
                "content_type": result.content_type.value,
                "quality_score": result.quality_score,
                "quality_rating": result.quality_rating.value,
                "cultural_adaptations": result.cultural_adaptations,
                "terminology_glossary": result.terminology_glossary,
                "back_translation": result.back_translation,
                "issues": result.issues
            }


# Streamlit interface
st.title("Translation & Localization Agent")
st.caption("Translate content, adapt cultural references, localize UI strings, and maintain terminology consistency")

api_key = st.text_input("OpenAI API Key", type="password")

tab1, tab2 = st.tabs(["Single Translation", "Batch Translation"])

with tab1:
    source_lang = st.selectbox("Source Language", ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Korean", "Arabic", "Portuguese", "Russian", "Italian"])
    target_lang = st.selectbox("Target Language", ["Spanish", "French", "German", "Chinese", "Japanese", "Korean", "Arabic", "Portuguese", "Russian", "Italian", "English"], index=2)
    content_type = st.selectbox("Content Type", [ct.value for ct in ContentType])
    text = st.text_area("Text to Translate", placeholder="Enter text to translate...", height=100)

    if api_key and text:
        agent = TranslationLocalizationAgent(api_key)
        result = agent.handle_request(text, source_lang, target_lang, content_type)

        st.subheader("Translation Result")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Quality Score", f"{result['quality_score']}/100")
        with col2:
            quality_color = {"excellent": "green", "good": "green", "fair": "yellow", "poor": "orange", "needs_review": "red"}
            st.markdown(f"Quality: :{quality_color.get(result['quality_rating'], 'gray')}[{result['quality_rating'].upper().replace('_', ' ')}]")
        with col3:
            st.metric("Issues", len(result["issues"]))

        st.write("**Translated Text:**")
        st.write(result["translated_text"])

        if result["back_translation"]:
            with st.expander("Back-Translation (for verification)"):
                st.write(result["back_translation"])

        if result["cultural_adaptations"]:
            st.write("**Cultural Adaptations:**")
            for adaptation in result["cultural_adaptations"]:
                st.markdown(f"- {adaptation}")

        if result["terminology_glossary"]:
            with st.expander("Terminology Glossary"):
                for term, translation in result["terminology_glossary"].items():
                    st.markdown(f"- **{term}**: {translation}")

        if result["issues"]:
            st.warning("Issues detected:")
            for issue in result["issues"]:
                st.markdown(f"- {issue}")

with tab2:
    source_lang = st.selectbox("Source Language (Batch)", ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Korean", "Arabic", "Portuguese", "Russian", "Italian"], key="batch_source")
    target_lang = st.selectbox("Target Language (Batch)", ["Spanish", "French", "German", "Chinese", "Japanese", "Korean", "Arabic", "Portuguese", "Russian", "Italian", "English"], index=2, key="batch_target")
    content_type = st.selectbox("Content Type (Batch)", [ct.value for ct in ContentType], key="batch_type")

    batch_text = st.text_area("Texts to Translate (one per line)", placeholder="Welcome to our app\nClick here to continue\nSettings\nProfile", height=150)

    if api_key and batch_text:
        texts = [t.strip() for t in batch_text.split("\n") if t.strip()]

        agent = TranslationLocalizationAgent(api_key)
        result = agent.handle_request("", source_lang, target_lang, content_type, batch_texts=texts)

        st.subheader("Batch Translation Results")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Texts", len(result["translations"]))
        with col2:
            st.metric("Avg Quality", f"{result['average_quality']:.0f}/100")
        with col3:
            st.metric("Consistency Issues", result["consistency_issues"], delta_color="inverse")

        for t in result["translations"]:
            with st.container():
                st.markdown(f"**Source:** {t['source']}")
                st.markdown(f"**Translation:** {t['translated']}")
                st.caption(f"Quality: {t['quality_score']}/100 | {t['quality_rating'].upper().replace('_', ' ')} | Consistent: {'✅' if t['consistent'] else '❌'}")

                if t['issues']:
                    for issue in t['issues']:
                        st.warning(issue)

                st.divider()
