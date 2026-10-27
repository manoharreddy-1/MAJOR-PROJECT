"""Unit tests for clean, canonical skill extraction and noisy fragment filtering."""
import pytest
from utils.clean_skill_extractor import (
    clean_missing_skills,
    split_compound_phrase,
    strip_filler_words_and_punctuation,
    canonicalize_skill,
)


def test_dirty_fragment_examples_part1():
    """Verify all dirty fragments specified in the problem statement are cleanly extracted."""
    dirty_inputs = [
        "IT",
        "Ai/Ml Or Data Science.",
        "Oriented Programming.",
        "Strong Problem",
        "Solving And Analytical Skills.",
        "Paced Environment.",
        "Good To Have",
        "Academic Or Personal Projects In Ai/Ml",
        "Exposure To Numpy",
        "Pandas And Scikit",
        "Learn.",
        "Familiarity With Tensorflow Or Pytorch.",
        "Exposure To Llms",
    ]

    # Assume TensorFlow is already matched on resume
    matched = ["TensorFlow"]

    cleaned = clean_missing_skills(dirty_inputs, matched_skills=matched)

    # 1. Non-skills must be dropped
    assert "IT" not in cleaned
    assert "it" not in [s.lower() for s in cleaned]
    assert "Good To Have" not in cleaned
    assert "Learn" not in cleaned
    assert "Learn." not in cleaned
    assert "Paced Environment" not in cleaned
    assert "Paced Environment." not in cleaned

    # 2. Compound phrases must be split
    assert "Pandas" in cleaned
    assert "scikit-learn" in cleaned or "Scikit-Learn" in cleaned
    assert "AI/ML" in cleaned
    assert "Data Science" in cleaned

    # 3. Trailing punctuation and filler words stripped
    assert "NumPy" in cleaned
    assert "LLMs" in cleaned

    # 4. Broken fragments merged/repaired
    assert "Object-Oriented Programming" in cleaned
    assert "Problem Solving" in cleaned
    assert "Analytical Skills" in cleaned

    # 5. Deduplicated against matched skills (TensorFlow was matched, so PyTorch is missing, but not TensorFlow)
    assert "PyTorch" in cleaned
    assert "TensorFlow" not in cleaned


def test_split_compound_phrase():
    """Verify compound phrase splitting with and/or/as well as."""
    res1 = split_compound_phrase("Pandas And Scikit")
    assert any("pandas" in r.lower() for r in res1)
    assert any("scikit" in r.lower() for r in res1)

    res2 = split_compound_phrase("Familiarity With Tensorflow Or Pytorch.")
    assert any("tensorflow" in r.lower() for r in res2)
    assert any("pytorch" in r.lower() for r in res2)

    res3 = split_compound_phrase("Ai/Ml Or Data Science.")
    assert any("ai/ml" in r.lower() for r in res3)
    assert any("data science" in r.lower() for r in res3)


def test_broken_fragment_repair():
    """Verify standalone fragment repair."""
    assert canonicalize_skill("Oriented Programming.") == "Object-Oriented Programming"
    assert canonicalize_skill("oriented programming") == "Object-Oriented Programming"


def test_filler_stripping():
    """Verify removal of filler prefixes and trailing punctuation."""
    assert strip_filler_words_and_punctuation("Exposure To Numpy.") == "Numpy"
    assert strip_filler_words_and_punctuation("Familiarity With Tensorflow;") == "Tensorflow"
    assert strip_filler_words_and_punctuation("Academic Or Personal Projects In Ai/Ml") == "Ai/Ml"
    assert strip_filler_words_and_punctuation("Exposure To Llms") == "Llms"


def test_canonical_casing():
    """Verify proper canonical casing for industry acronyms and technologies."""
    assert canonicalize_skill("numpy") == "NumPy"
    assert canonicalize_skill("pytorch") == "PyTorch"
    assert canonicalize_skill("tensorflow") == "TensorFlow"
    assert canonicalize_skill("nlp") == "NLP"
    assert canonicalize_skill("llms") == "LLMs"
    assert canonicalize_skill("generative ai") == "Generative AI"
