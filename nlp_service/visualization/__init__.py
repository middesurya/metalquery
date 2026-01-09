"""
Visualization Module for MetalQuery NLP Service
LIDA-inspired visualization pipeline for generating chart configurations.
"""

from .viz_summarizer import DataSummarizer
from .viz_goal_finder import VizGoalFinder
from .viz_config_generator import VizConfigGenerator
from .viz_templates import KPI_TEMPLATES, get_template_for_query
from .viz_validator import VizConfigValidator

__all__ = [
    'DataSummarizer',
    'VizGoalFinder',
    'VizConfigGenerator',
    'VizConfigValidator',
    'KPI_TEMPLATES',
    'get_template_for_query',
    'VizPipeline'
]


class VizPipeline:
    """
    Main visualization pipeline that orchestrates:
    1. Data summarization
    2. Visualization goal finding (LLM-powered)
    3. Config generation
    4. Validation
    """

    def __init__(self):
        self.summarizer = DataSummarizer()
        self.goal_finder = VizGoalFinder()
        self.config_generator = VizConfigGenerator()
        self.validator = VizConfigValidator()

    async def generate_config(self, question: str, results: list, llm=None) -> dict:
        """
        Generate a chart configuration for the given question and results.

        Args:
            question: User's original question
            results: SQL query results (list of dicts)
            llm: LLM instance for goal finding

        Returns:
            Chart configuration dict or None if visualization not appropriate
        """
        # Skip if no results
        if not results:
            return None

        # Step 1: Summarize the data
        summary = self.summarizer.summarize(results, question)

        # Skip visualization for very large datasets (table is better)
        if summary['row_count'] > 100:
            return None

        # Step 2: Find visualization goal
        if llm:
            goal = await self.goal_finder.find_goal(summary, question, llm)
        else:
            # Fallback to heuristic-based goal finding
            goal = self.goal_finder.find_goal_heuristic(summary, question)

        # Skip if goal suggests table
        if goal.get('chart_type') == 'table':
            return None

        # Step 3: Generate config
        config = self.config_generator.generate(goal, results)

        # Step 4: Validate
        is_valid, error = self.validator.validate(config)
        if not is_valid:
            return None

        return config

    def generate_config_sync(self, question: str, results: list) -> dict:
        """
        Synchronous version using heuristics only (no LLM).
        """
        if not results:
            return None

        summary = self.summarizer.summarize(results, question)

        if summary['row_count'] > 100:
            return None

        goal = self.goal_finder.find_goal_heuristic(summary, question)

        if goal.get('chart_type') == 'table':
            return None

        config = self.config_generator.generate(goal, results)

        is_valid, _ = self.validator.validate(config)
        if not is_valid:
            return None

        return config
