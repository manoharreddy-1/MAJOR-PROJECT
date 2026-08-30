"""NER model for entity extraction from resumes."""
import logging
import threading
from typing import Dict, List

from config.settings import NER_MODEL_NAME

logger = logging.getLogger(__name__)

_ner_pipeline = None
_ner_lock = threading.Lock()


def get_ner_pipeline():
    """Load and cache Hugging Face NER pipeline."""
    global _ner_pipeline
    if _ner_pipeline is not None:
        return _ner_pipeline

    with _ner_lock:
        if _ner_pipeline is not None:
            return _ner_pipeline
        try:
            from transformers import pipeline
            logger.info("Loading NER model: %s", NER_MODEL_NAME)
            _ner_pipeline = pipeline(
                "ner",
                model=NER_MODEL_NAME,
                aggregation_strategy="simple",
            )
            logger.info("NER model loaded successfully.")
            return _ner_pipeline
        except Exception as exc:
            logger.warning("NER model unavailable: %s", exc)
            return None


class NERModel:
    """Wrapper for NER entity extraction."""

    def extract_entities(self, text: str, max_length: int = 512) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        pipeline = get_ner_pipeline()
        if pipeline is None:
            return {"persons": [], "organizations": [], "locations": [], "misc": []}

        # Process in chunks for long text
        chunk = text[:max_length * 4]
        try:
            entities = pipeline(chunk)
        except Exception as exc:
            logger.warning("NER extraction failed: %s", exc)
            return {"persons": [], "organizations": [], "locations": [], "misc": []}

        result = {"persons": [], "organizations": [], "locations": [], "misc": []}
        label_map = {
            "PER": "persons",
            "PERSON": "persons",
            "ORG": "organizations",
            "ORGANIZATION": "organizations",
            "LOC": "locations",
            "LOCATION": "locations",
            "MISC": "misc",
        }

        seen = set()
        for ent in entities:
            word = ent.get("word", "").strip()
            label = ent.get("entity_group", ent.get("entity", ""))
            if not word or word in seen:
                continue
            seen.add(word)
            category = label_map.get(label.upper(), "misc")
            if word not in result[category]:
                result[category].append(word)

        return result
