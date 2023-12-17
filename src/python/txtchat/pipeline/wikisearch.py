"""
Wikisearch module
"""

import logging
import urllib.parse

from txtai.pipeline import Pipeline
from txtai.workflow import Task, Workflow

from ..task import Question, Answer

# Logging configuration
logger = logging.getLogger(__name__)


class Wikisearch(Pipeline):
    """
    Pipeline for conversational search with Wikipedia. This pipeline queries a Wikipedia embeddings index and passes the results
    as context to a large language model (LLM) prompt. Results from the prompt inference are then returned.
    """

    def __init__(self, application):
        """
        Creates a new Wikisearch instance.

        Args:
            application: application instance
        """

        # Application instance
        self.application = application

        # Workflow instance
        self.workflow = None

    def __call__(self, texts, **kwargs):
        """
        Executes a conversational search action for each element in texts.

        Args:
            texts: input texts
            kwargs: additional keyword args to pass to workflow

        Returns:
            responses
        """

        # Defer creation of workflow to ensure application is fully initialized
        if not self.workflow:
            self.workflow = self.create(**kwargs)

        responses = []
        for text in texts:
            # First try top 1%
            response = self.query(text, 0.99, 1.0)

            # Do full query if no answer
            if response.startswith(Answer.NOANSWER):
                response = self.query(text, 0.00, 0.99)

            responses.append(response)

        return responses

    def create(self, **kwargs):
        """
        Creates a search workflow.

        Args:
            kwargs: keyword arguments to pass to workflow

        Returns:
            Workflow
        """

        # Get extractor instance
        extractor = self.application.pipelines["extractor"]

        def action(x):
            return extractor(x, **kwargs)

        # Flag to see if extractor has a template
        template = hasattr(extractor, "template") and extractor.template != "{question} {context}"

        # Define workflow
        return Workflow([Task(action=action) if template else Question(action=action), WikiAnswer()])

    def query(self, text, low, high):
        """
        Runs a prompt-driven query for text. Low and high percentile bounds are used to filter results from the Wikipedia index.

        Args:
            text: input query text
            low: lower percentile bound
            high: upper percentile bound

        Returns:
            response
        """

        # Build similar clause
        clause = self.clause(text)

        # Build SQL query
        query = f"SELECT id, text, score, percentile FROM txtai WHERE similar({clause}) AND percentile >= {low} AND percentile <= {high} limit 3"
        logger.info(query)

        # Run query workflow
        return list(self.workflow([{"query": query, "question": text}]))[0]

    def clause(self, text):
        """
        Builds a similar clause using text.

        Args:
            text: input text

        Returns:
            text for similar clause
        """

        # Remove all single quotes
        text = text.replace("'", "")

        # Wrap clause in single quotes
        return f"'{text}'"


class WikiAnswer(Answer):
    """
    Task that fully resolves Wikipedia URLs.
    """

    def prepare(self, element):
        """
        Formats the reference column as a Wikipedia URL.

        Args:
            element: input data element

        Returns:
            transformed element
        """

        if not element["answer"].startswith(Answer.NOANSWER):
            reference = element["reference"]

            # Resolve full reference URL path
            path = urllib.parse.quote(reference.replace(" ", "_"))
            element["reference"] = f"https://en.wikipedia.org/wiki/{path}"

            # Call parent method
            return super().prepare(element)

        return element["answer"]
