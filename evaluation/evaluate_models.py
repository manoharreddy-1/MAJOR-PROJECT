"""
Evaluate SBERT vs TF-IDF baseline for resume-job matching.

Usage:
    python evaluation/evaluate_models.py

Requires test_data.csv with columns:
    resume_text, job_text, label (1 = relevant match, 0 = not relevant)
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ai.sbert_model import encode_texts
from evaluation.metrics import compute_classification_metrics, normalize_similarity_to_score


def load_test_data(path: str) -> list:
    """Load labeled test pairs from CSV."""
    data = []
    if not os.path.exists(path):
        print(f"WARNING: {path} not found. Using built-in sample data.")
        return get_sample_data()

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                "resume_text": row["resume_text"],
                "job_text": row["job_text"],
                "label": int(row["label"]),
            })
    return data


def get_sample_data() -> list:
    """Built-in sample test pairs for demonstration."""
    return [
        {
            "resume_text": "Built CNN models using TensorFlow for image classification. Experience with deep learning and computer vision.",
            "job_text": "Looking for knowledge of Deep Learning and Computer Vision. Experience with neural networks required.",
            "label": 1,
        },
        {
            "resume_text": "Developed REST APIs using Python Flask and MongoDB. Deployed applications on AWS.",
            "job_text": "Machine Learning Engineer with TensorFlow and PyTorch experience. Computer vision skills required.",
            "label": 0,
        },
        {
            "resume_text": "Python developer with experience in data analysis using Pandas and NumPy. SQL and MongoDB databases.",
            "job_text": "Data Analyst role requiring Python, Pandas, SQL, and data visualization skills.",
            "label": 1,
        },
        {
            "resume_text": "Frontend developer specializing in React, HTML, CSS, and JavaScript. Built responsive web applications.",
            "job_text": "Backend Python developer needed for Flask API development and database management.",
            "label": 0,
        },
        {
            "resume_text": "Machine learning projects using Scikit-learn and TensorFlow. Built recommendation systems and NLP models.",
            "job_text": "Seeking ML engineer with Scikit-learn, TensorFlow, and NLP experience for AI product team.",
            "label": 1,
        },
    ]


def evaluate_tfidf(data: list, threshold: float = 0.3) -> dict:
    """Evaluate TF-IDF + Cosine Similarity baseline."""
    similarities = []
    labels = []

    for item in data:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf = vectorizer.fit_transform([item["resume_text"], item["job_text"]])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        similarities.append(sim)
        labels.append(item["label"])

    predictions = [1 if s >= threshold else 0 for s in similarities]
    true_labels = labels

    return {
        "method": "TF-IDF + Cosine Similarity",
        "avg_similarity": round(np.mean(similarities), 4),
        "similarities": [round(s, 4) for s in similarities],
        **compute_classification_metrics(true_labels, predictions),
    }


def evaluate_sbert(data: list, threshold: float = 0.55) -> dict:
    """Evaluate SBERT + Cosine Similarity (main model)."""
    similarities = []
    labels = []

    for item in data:
        embeddings = encode_texts([item["resume_text"], item["job_text"]])
        sim = float(cosine_similarity(
            embeddings[0].reshape(1, -1),
            embeddings[1].reshape(1, -1),
        )[0][0])
        similarities.append(sim)
        labels.append(item["label"])

    predictions = [1 if s >= threshold else 0 for s in similarities]
    true_labels = labels

    return {
        "method": "SBERT (all-MiniLM-L6-v2) + Cosine Similarity",
        "avg_similarity": round(np.mean(similarities), 4),
        "similarities": [round(s, 4) for s in similarities],
        **compute_classification_metrics(true_labels, predictions),
    }


def main():
    test_path = os.path.join(os.path.dirname(__file__), "test_data.csv")
    data = load_test_data(test_path)

    print("=" * 60)
    print("AI Resume Analyzer - Model Evaluation")
    print("=" * 60)
    print(f"Test samples: {len(data)}")
    print(f"Positive labels: {sum(d['label'] for d in data)}")
    print(f"Negative labels: {len(data) - sum(d['label'] for d in data)}")
    print()

    print("Evaluating TF-IDF baseline...")
    tfidf_results = evaluate_tfidf(data)
    print(f"  Method: {tfidf_results['method']}")
    print(f"  Avg Similarity: {tfidf_results['avg_similarity']}")
    print(f"  Precision: {tfidf_results['precision']}")
    print(f"  Recall: {tfidf_results['recall']}")
    print(f"  F1: {tfidf_results['f1']}")
    print()

    print("Evaluating SBERT (main model)...")
    sbert_results = evaluate_sbert(data)
    print(f"  Method: {sbert_results['method']}")
    print(f"  Avg Similarity: {sbert_results['avg_similarity']}")
    print(f"  Precision: {sbert_results['precision']}")
    print(f"  Recall: {sbert_results['recall']}")
    print(f"  F1: {sbert_results['f1']}")
    print()

    print("=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    print(f"{'Metric':<20} {'TF-IDF':<15} {'SBERT':<15}")
    print(f"{'Precision':<20} {tfidf_results['precision']:<15} {sbert_results['precision']:<15}")
    print(f"{'Recall':<20} {tfidf_results['recall']:<15} {sbert_results['recall']:<15}")
    print(f"{'F1 Score':<20} {tfidf_results['f1']:<15} {sbert_results['f1']:<15}")
    print()
    print("NOTE: Metrics computed on the provided test set.")
    print("Expand test_data.csv with more labeled pairs for robust evaluation.")


if __name__ == "__main__":
    main()
