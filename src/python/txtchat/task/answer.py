"""
Answer module
"""

from txtai.workflow import TemplateTask


class Answer(TemplateTask):
    """
    Template task with defaults for answer tasks.
    """

    NOANSWER = "I don't have data on that"

    def defaulttemplate(self):
        """
        Default template. Used when template parameter is empty.

        Returns:
            default template
        """

        return "{answer}\n\nReference: {reference}"

    def defaultrules(self):
        """
        Default rules. Used when rules parameter is empty.

        Returns:
            default rules
        """

        return {"answer": Answer.NOANSWER}
