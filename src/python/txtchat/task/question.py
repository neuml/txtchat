"""
Question module
"""

from txtai.workflow import ExtractorTask


class Question(ExtractorTask):
    """
    Extractor task with a default template when it's not provided.
    """

    def defaulttemplate(self):
        """
        Default template. Used when template parameter is empty.

        Returns:
            default template
        """

        # Generate a default template
        template = "Answer the following question using only the context below. Give a detailed answer. "
        template += "Say 'I don't have data on that' when the question can't be answered.\n"
        template += "Question: {text}\n"
        template += "Context: "

        return template
