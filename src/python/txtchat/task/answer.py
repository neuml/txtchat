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
        return "{answer}\n\nReference: {reference}"

    def defaultrules(self):
        return {
            "answer": Answer.NOANSWER
        }
