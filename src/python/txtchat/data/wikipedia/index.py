"""
Index module
"""

import argparse
import logging
import re
import sqlite3

from multiprocessing import Process, Queue

from nltk import sent_tokenize
from tqdm import tqdm

from txtai.embeddings import Embeddings

from datasets import load_dataset

# Process and index parameters
COMPLETE, BATCH, ENCODEBATCH = 1, 8192, 128


class Reader:
    """
    Loads the Wikipedia dataset along with the page view database and adds valid entries to the outputs queue.
    """

    def __call__(self, outputs, dataset, pageviews):
        """
        Adds valid Wikipedia articles to outputs.

        Args:
            outputs: outputs queue
            dataset: path to dataset
            pageviews: path to page views database
        """

        wiki = load_dataset(dataset, split="train")

        # Get percentile rankings
        rank = self.rankings(pageviews)

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
                    batch = self.add(batch, (title, abstract, None), outputs)

                    # Index additional metadata
                    batch = self.add(batch, (title, {"percentile": score}, None), outputs)

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

    def add(self, batch, row, outputs):
        """
        Adds an output row to batch. If BATCH size has been met, a new batch is put in outputs.

        Args:
            batch: current batch
            row: row to add
            outputs: output queue

        Returns:
            current batch, which will change when BATCH size has been reached
        """

        batch.append(row)

        if len(batch) % BATCH == 0:
            outputs.put(batch)
            batch = []

        return batch


class Index:
    """
    Builds a Wikipedia embeddings index.
    """

    def __call__(self, args):
        """
        Main process for streaming content and building an embeddings index. Another process is spawned that
        streams Wikipedia articles to load into the embeddings index.

        Args:
            args: command line arguments
        """

        # Encoding parameters
        queue = Queue(5)

        # Dataset reader process
        process = Process(target=Reader(), args=(queue, args.dataset, args.pageviews))
        process.start()

        # Total size
        total = queue.get()

        # Embedding index parameters
        embeddings = Embeddings(
            {
                "format": "json",
                "path": "intfloat/e5-base",
                "instructions": {"query": "query: ", "data": "passage: "},
                "batch": BATCH,
                "encodebatch": ENCODEBATCH,
                "faiss": {"quantize": True, "sample": 0.05},
                "content": True,
            }
        )

        # Index stream
        embeddings.index(tqdm(self.stream(queue), total=total))

        # Wait for process to finish
        process.join()

        # Save index
        embeddings.save(args.output)

    def stream(self, queue):
        """
        Yields articles for indexing from the queue.

        Args:
            queue: queue to read from
        """

        result = queue.get()
        while result != COMPLETE:
            yield from result
            result = queue.get()


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
