"""
Index module
"""

import argparse
import logging
import re

from datasets import load_dataset

from ..base import Index as IndexBase
from ..base import Reader as ReaderBase
from ..base import COMPLETE, BATCH, ENCODEBATCH


class Reader(ReaderBase):
    """
    Loads the arXiv dataset and adds entries to the outputs queue.
    """

    def __call__(self, outputs, args):
        """
        Adds arXiv articles to outputs.

        Args:
            outputs: outputs queue
            args: command line arguments
        """

        # Load the raw dataset
        arxiv = load_dataset("arxiv_dataset", data_dir=args.data, ignore_verifications=True, split="train")

        # Put estimated data size
        outputs.put(len(arxiv) * 2)

        # Batch of rows
        batch = []

        for row in arxiv:
            # Article title
            title = self.clean(row.pop("title"))

            # Article abstract
            abstract = self.clean(row.pop("abstract"))

            # Create text field
            text = f"{title}\n{abstract}"

            # Index article text
            batch = self.add(batch, (row["id"], text), outputs)

            # Index article metadata
            batch = self.add(batch, row, outputs)

        # Final batch
        if batch:
            outputs.put(batch)

        # Complete flag
        outputs.put(COMPLETE)

    def clean(self, text):
        """
        Formats a text field.

        Args:
            text: input text

        Returns:
            formatted text
        """

        text = text.replace("\n", " ").strip()
        return re.sub(r"\s{2,}", " ", text)


class Index(IndexBase):
    """
    Builds an arXiv embeddings index.
    """

    def __init__(self):
        """
        Set the embeddings configuration.
        """

        # Call parent constructor
        super().__init__()

        # Create configuration
        self.config = {
            "format": "json",
            "path": "thenlper/gte-base",
            "batch": BATCH,
            "encodebatch": ENCODEBATCH,
            "faiss": {"quantize": True, "sample": 0.05},
            "content": True,
        }

        # Create reader instance
        self.reader = Reader()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s")
    logging.getLogger().setLevel(logging.INFO)

    # Command line parser
    parser = argparse.ArgumentParser(description="arXiv Index")
    parser.add_argument("-d", "--data", help="input data directory", metavar="DATA", required=True)
    parser.add_argument("-o", "--output", help="path to output directory", metavar="OUTPUT", required=True)

    # Build index
    index = Index()
    index(parser.parse_args())
