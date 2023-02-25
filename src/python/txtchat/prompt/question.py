"""
Question module
"""

from .base import Prompt


class Question(Prompt):
    """
    Creates a question prompt.
    """

    def generate(self, text):
        # Generates a prompt
        prompt = "Answer the following question using only the context below. Give a detailed answer. "
        prompt += "Say 'I don't have data on that' when the question can't be answered.\n"
        prompt += f"Question: {text}\n"
        prompt += "Context: "

        return prompt
