"""
Question module
"""


class Question:
    """
    Creates a question prompt.
    """

    def __call__(self, question):
        """
        Create a question prompt.

        Args:
            question: question to add to prompt

        Returns:
            question prompt
        """

        # pylint: disable=C0301
        return f"""Answer the following question using only the context below. Give a detailed answer. Say 'I don't have data on that' when the question can't be answered.
Question: {question} 
Context: """
