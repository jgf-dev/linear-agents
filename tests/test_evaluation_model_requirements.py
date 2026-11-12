import os
import re
import pytest

DOC_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs",
    "incentive-mechanism",
    "evaluation-model-requirements.md",
)


def test_document_exists():
    """Verify that the evaluation model requirements specification exists and is non-empty."""
    assert os.path.exists(DOC_PATH), f"Document not found at {DOC_PATH}"
    with open(DOC_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert len(content.strip()) > 1000, "Document is too brief or empty"


def test_required_sections_present():
    """Verify that all core sections mandated by AIX-117 are present."""
    with open(DOC_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    required_sections = [
        "Task Characteristics: Open-Ended Compute vs. Deterministic Work",
        "Success Criteria & Verification Framework",
        "Evidence Needed for Model Choice",
        "Decision Matrix & Evaluation Rubric",
        "Downstream Protocol Implications",
    ]

    for section in required_sections:
        assert section.lower() in content.lower(), f"Missing required section: '{section}'"


def test_task_characteristics_taxonomies():
    """Verify that essential task characteristics are documented for both models."""
    with open(DOC_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    required_terms = [
        "determinism",
        "statefulness",
        "hardware heterogeneity",
        "compute asymmetry",
        "open-ended compute",
        "deterministic work",
    ]

    for term in required_terms:
        assert term.lower() in content.lower(), f"Missing task characteristic term: '{term}'"


def test_success_criteria_coverage():
    """Verify that success criteria capture continuous scoring, binary verification, and Yuma Consensus."""
    with open(DOC_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    criteria_terms = [
        "continuous scoring",
        "binary",
        "yuma consensus",
        "latency",
        "throughput",
        "outlier clipping",
    ]

    for term in criteria_terms:
        assert term.lower() in content.lower(), f"Missing success criteria term: '{term}'"


def test_evidence_requirements_coverage():
    """Verify that all dimensions of evidence required to make the model decision are specified."""
    with open(DOC_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    evidence_dimensions = [
        "verification cost",
        "collusion",
        "economic",
        "game-theoretic",
        "commercial utility",
        "operational",
    ]

    for dim in evidence_dimensions:
        assert dim.lower() in content.lower(), f"Missing evidence dimension: '{dim}'"


def test_downstream_issue_traceability():
    """Verify that the requirements document connects to subsequent issues AIX-118 through AIX-121."""
    with open(DOC_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    for issue_id in ["AIX-116", "AIX-118", "AIX-119", "AIX-120", "AIX-121"]:
        assert issue_id in content, f"Missing reference to related issue {issue_id}"
