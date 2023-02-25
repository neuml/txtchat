"""
Prompt module
"""


class Prompt:
    """
    Base class for prompts.
    """

    def __call__(self, text):
        """
        Transform input text into a {query, question} dictionary that can be processed by a txtai extractor pipeline.

        Args:
            text: text|list

        Returns:
            list of {query, question}
        """

        # Convert results to a list if necessary
        inputs = text if isinstance(text, list) else [text]

        # Build prompts
        outputs = [{"query": x, "question": self.generate(x)} for x in inputs]

        # Return same type as original input
        return outputs if isinstance(text, list) else outputs[0]

    def generate(self, text):
        """
        Defines the template for this prompt. This template requires a {text} parameter

        Args:
            text: text to substitute
        """

        raise NotImplementedError
