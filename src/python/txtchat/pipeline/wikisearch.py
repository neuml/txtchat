"""
Wikisearch module
"""

import logging
import urllib.parse

from txtai.pipeline import Pipeline

# Logging configuration
logger = logging.getLogger(__name__)


class Wikisearch(Pipeline):
    """
    Pipeline for multi-step RAG with Wikipedia. This pipeline queries a Wikipedia embeddings index and passes the results
    as context to a Large Language Model (LLM) prompt.
    """

    def __init__(self, application):
        """
        Creates a new Wikisearch instance.

        Args:
            application: application instance
        """

        # Application instance
        self.application = application

    def __call__(self, texts, **kwargs):
        """
        Executes a multi-step RAG action for each element in texts.

        Args:
            texts: input texts
            kwargs: additional keyword args

        Returns:
            responses
        """

        responses = []
        for text in texts:
            # First try top 1%
            response = self.rag(text, 0.99, 1.0)

            # Do full query if no answer
            if not response:
                response = self.rag(text, 0.00, 0.99)

            # Format responses
            responses.append(self.render(response))

        return responses

    def rag(self, text, low, high):
        """
        Runs a RAG pipeline. Low and high percentile bounds are used to filter results from the Wikipedia index.

        Args:
            text: input query text
            low: lower percentile bound
            high: upper percentile bound

        Returns:
            response
        """

        # Get rag pipeline
        rag = self.application.pipelines["rag"]

        # Build similar clause
        clause = self.clause(text)

        # Build SQL query
        query = f"SELECT id, text, score, percentile FROM txtai WHERE similar({clause}) AND percentile >= {low} AND percentile <= {high} limit 10"
        logger.info(query)

        # Generate context
        context = self.application.search(query)

        # Run RAG pipeline
        response = rag(text, [x["text"] for x in context], maxlength=2048)

        # Format and return response
        reference = response["reference"]
        response["reference"] = context[reference]["id"] if reference is not None else reference
        return response

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

    def render(self, response):
        """
        Renders a response to text.

        Args:
            response: pipeline response
        """

        # Get answer and reference
        answer = response["answer"]
        reference = response["reference"]

        # Resolve full reference URL path
        path = urllib.parse.quote(reference.replace(" ", "_"))
        reference = f"https://en.wikipedia.org/wiki/{path}"

        # Render response
        return f"{answer}\n\nReference: {reference}"
