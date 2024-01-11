"""
Views module
"""

import argparse
import bz2
import glob
import logging
import os
import sqlite3

from multiprocessing import Process, Queue

import pandas as pd

COMPLETE = 1

# Logging configuration
logger = logging.getLogger(__name__)


class Reader:
    """
    Multiple processes are instantiated with this class as the entry point. Each process reads file paths from
    a shared queue and writes back aggregated page view data.
    """

    def __call__(self, inputs, outputs, prefix):
        """
        Reads files from inputs and writes aggregated page views to outputs.

        Args:
            inputs: input queue
            outputs: output queue
            prefix: prefix filter used to accept entries
        """

        # Aggregated page views
        pages = {}

        try:
            # Process until inputs queue is exhausted
            while not inputs.empty():
                self.process(inputs.get(), pages, prefix)

        finally:
            # Write aggregated page stats
            outputs.put(pages)

            # Write message that process is complete
            outputs.put(COMPLETE)

    def process(self, path, pages, prefix):
        """
        Processes a single file at path. Writes page views to pages parameter.

        Args:
            path: input file path
            pages: page view dictionary
            prefix: prefix filter used to accept entries
        """

        logger.info("Processing: %s", path)
        with bz2.open(path, "rt", encoding="utf-8") as infile:
            for line in infile:
                if not prefix or line.startswith(f"{prefix} "):
                    columns = line.split()
                    title, views = columns[1].lower(), columns[-2]

                    # Check if title matches filters
                    if self.accept(title):
                        pages[title] = pages.get(title, 0) + int(views)

    def accept(self, title):
        """
        Determines if entry should be accepted based on title.

        Args:
            title: input title

        Returns:
            True if entry should be accepted, False otherwise
        """

        prefix = ["Category:", "Draft:", "File:", "Help:", "Main_Page", "Portal:", "Special:", "Talk:", "Template:", "Wikipedia:"]
        names = ["Main_Page", "-"]

        return not any(x for x in prefix if title.startswith(x)) and title not in names


class Views:
    """
    Builds a page views database.
    """

    def __call__(self, args):
        """
        Main process for aggregating page view data. This lists a directory containing hourly page view files
        and puts each file into a queue shared by multiple processes.

        The reader processes parse the file contents and return page view data. This process then aggregates
        the page views by title and saves the results to a SQLite database.

        Args:
            args: command line arguments
        """

        # Create queues, limit size of output queue
        inputs, outputs = Queue(), Queue()

        # Scan input directory and add files to inputs queue
        total = self.scan(os.path.join(args.views, "data/pageviews*bz2"), inputs)

        # Start worker processes
        processes = []
        for _ in range(min(total, os.cpu_count())):
            process = Process(target=Reader(), args=(inputs, outputs, args.prefix))
            process.start()
            processes.append(process)

        # Main processing loop
        pages = self.process(processes, outputs)

        # Wait for processes to terminate
        for process in processes:
            process.join()

        df = pd.DataFrame(pages.items(), columns=["title", "views"])

        # Path to database file
        path = os.path.join(args.views, "pageviews.sqlite")

        # Remove existing file, if necessary
        if os.path.exists(path):
            os.remove(path)

        connection = sqlite3.connect(path)
        df.to_sql("pages", connection, index=False)

    def scan(self, path, inputs):
        """
        Reads all matching files at path and loads them into the inputs queue.

        Args:
            path: input path pattern
            inputs: add each matching file to this queue

        Returns:
            total number of files
        """

        total = 0
        for f in sorted(glob.glob(path)):
            inputs.put(f)
            total += 1

        return total

    def process(self, processes, outputs):
        """
        Reads aggregated page view data from the outputs queue and further aggregates that data into a single pages dictionary.

        Args:
            processes: handle to list of input processes
            outputs: outputs queue to read data from

        Returns:
            final fully-aggregated page view data
        """

        # Read output from worker processes
        pages, empty, complete = {}, False, 0
        while not empty:
            # Get next result
            result = outputs.get()

            # Mark process as complete if all workers are complete and output queue is empty
            if result == COMPLETE:
                complete += 1
                empty = len(processes) == complete and outputs.empty()

            # Merge page results
            elif result:
                for title, views in result.items():
                    if title not in pages:
                        pages[title] = 0

                    pages[title] += int(views)

        return pages


# Call main method
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s")
    logging.getLogger().setLevel(logging.INFO)

    # Command line parser
    parser = argparse.ArgumentParser(description="Wikipedia Page Views")
    parser.add_argument("-p", "--prefix", help="prefix filter used to accept entries", metavar="PREFIX", default="en.wikipedia")
    parser.add_argument("-v", "--views", help="pageviews root directory", metavar="PAGEVIEWS", required=True)

    # Create page views database
    database = Views()

    # Build aggregated page view database
    database(parser.parse_args())
