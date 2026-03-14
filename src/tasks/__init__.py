"""Celery tasks for Academic Research Assistant."""
from .briefing import generate_briefing, check_new_papers
from .parser import parse_paper_task

__all__ = [
    "generate_briefing",
    "check_new_papers",
    "parse_paper_task",
]
