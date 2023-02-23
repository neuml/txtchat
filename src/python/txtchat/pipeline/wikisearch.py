"""
Wikisearch module
"""

import logging
import urllib.parse

from txtai.pipeline import Pipeline

from ..prompt import Question

# Logging configuration
logger = logging.getLogger(__name__)


class Wikisearch(Pipeline):
    """
    Pipeline for conversational search with Wikipedia. This pipeline queries a Wikipedia embeddings index and passes the results
    as context to a large language model (LLM) prompt. Results from the prompt inference are then returned.
    """

    NOANSWER = "I don't have data on that"

    def __init__(self, application):
        """
        Creates a new Wikisearch instance.

        Args:
            application: application instance
        """

        # Application instance
        self.application = application

        # Initialize prompt
        self.prompt = Question()

    def __call__(self, texts):
        """
        Executes a conversational search action for each element in texts.

        Args:
            texts: input texts

        Returns:
            responses
        """

        responses = []
        for text in texts:
            # First try top 1%
            response = self.query(text, 0.99, 1.0)

            # Do full query if no answer
            if response == Wikisearch.NOANSWER:
                response = self.query(text, 0.00, 0.99)

            responses.append(response)

        return responses

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

        query = f"SELECT id, text, score, percentile FROM txtai WHERE similar({clause}) AND percentile >= {low} AND percentile <= {high} limit 3"
        logger.info(query)

        # Run embeddings search
        results, answer = self.application.search(query), Wikisearch.NOANSWER
        if results:
            # Prompt context
            texts = [x["text"] for x in results]

            for x in results:
                logger.info("%s\n", x)

            # Run the LLM prompt
            answer = self.application.extract([{"name": "query", "query": text, "question": self.prompt(text)}], texts)[0]["answer"]

            # Find the best matching reference from the results
            if answer != Wikisearch.NOANSWER:
                index = self.application.similarity(f"{text} {answer}", texts)[0]["id"]
                uid = results[index]["id"]
                path = urllib.parse.quote(uid.replace(" ", "_"))
                answer += f"\n\nReference: https://en.wikipedia.org/wiki/{path}"

        return answer

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
