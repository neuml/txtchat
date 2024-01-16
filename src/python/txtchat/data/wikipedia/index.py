"""
Index module
"""

import argparse
import logging
import re
import sqlite3

from nltk import sent_tokenize
from datasets import load_dataset

from ..base import Index as IndexBase
from ..base import Reader as ReaderBase
from ..base import COMPLETE, BATCH, ENCODEBATCH


class Reader(ReaderBase):
    """
    Loads the Wikipedia dataset along with the page view database and adds valid entries to the outputs queue.
    """

    def __call__(self, outputs, args):
        """
        Adds valid Wikipedia articles to outputs.

        Args:
            outputs: outputs queue
            args: command line args
        """

        # Load the raw dataset
        wiki = load_dataset(args.dataset, split="train")

        # Get percentile rankings
        rank = self.rankings(args.pageviews)

        # Put estimated data size
        outputs.put(len(wiki) * 2)

        # Titles and abstract prefixes to skip
        skiptitles = ["List of ", "Timeline of ", "Timelines "]
        skipabstracts = ["Events ", "The following events "]

        # Batch of rows
        batch = []

        for row in wiki:
            # Article title
            title = row["title"]

            # First text section is considered abstract
            abstract = row["text"].split("\n\n")[0]

            # Cleanup empty parens
            abstract = re.sub(r" \(\s*\)", "", abstract)

            # Accept article using following rules
            # - title does not contain 'disambiguation' and does not start with skip title prefixes
            # - abstract is not empty and does not start with skip abstract prefixes and does not end with ':'
            # - lede does not contain 'can refer to' or 'may refer to'
            if (
                "disambiguation" not in title
                and not any(title.startswith(p) for p in skiptitles)
                and abstract.strip()
                and not any(abstract.startswith(p) for p in skipabstracts)
                and not abstract.strip().endswith(":")
            ):
                # Split into sentences
                lede = sent_tokenize(abstract)[0]

                # Skip if lede is a list of references
                if lede.strip() and "can refer to" not in lede and "may refer to" not in lede:
                    score = self.percentile(rank, title)

                    # Index article text
                    batch = self.add(batch, (title, abstract), outputs)

                    # Index additional metadata
                    batch = self.add(batch, (title, {"percentile": score}), outputs)

        # Final batch
        if batch:
            outputs.put(batch)

        # Complete flag
        outputs.put(COMPLETE)

    def rankings(self, path):
        """
        Reads a page views database at path and runs a query to rank each article by page
        view percentile.

        Args:
            path: path to database file

        Returns:
            dictionary of title to percentile rank for each article
        """

        # Read page views database
        connection = sqlite3.connect(path)
        cursor = connection.cursor()

        # Get ranks for each page
        cursor.execute("SELECT title, percent_rank() OVER (ORDER BY views) rank FROM pages")

        rank = {}
        for title, score in cursor:
            rank[title] = score

        return rank

    def percentile(self, rank, title):
        """
        Looks up the percentile for a title.

        Args:
            rank: ranking dictionary
            title: title key to lookup

        Returns:
            percentile rank for title, 0 if not found
        """

        return rank.get(title.lower().replace(" ", "_"), 0)


class Index(IndexBase):
    """
    Builds a Wikipedia embeddings index.
    """

    def __init__(self):
        """
        Sets the embeddings configuration.
        """

        # Call parent constructor
        super().__init__()

        # Create configuration
        self.config = {
            "format": "json",
            "path": "intfloat/e5-base",
            "instructions": {"query": "query: ", "data": "passage: "},
            "batch": BATCH,
            "encodebatch": ENCODEBATCH,
            "faiss": {"quantize": True, "sample": 0.05},
            "content": True,
        }

        # Create Reader instance
        self.reader = Reader()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s")
    logging.getLogger().setLevel(logging.INFO)

    # Command line parser
    parser = argparse.ArgumentParser(description="Wikipedia Index")
    parser.add_argument("-d", "--dataset", help="input dataset", metavar="DATASET", required=True)
    parser.add_argument("-o", "--output", help="path to output directory", metavar="OUTPUT", required=True)
    parser.add_argument("-v", "--pageviews", help="path to pageviews database", metavar="PAGEVIEWS", required=True)

    # Build index
    index = Index()
    index(parser.parse_args())
