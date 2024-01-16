"""
Index module
"""

from multiprocessing import Process, Queue

from tqdm import tqdm

from txtai.embeddings import Embeddings

# Process and index parameters
COMPLETE, BATCH, ENCODEBATCH = 1, 8192, 128


class Reader:
    """
    Loads a dataset and adds valid entries to the outputs queue.
    """

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
    Builds an embeddings index.
    """

    def __init__(self):
        """
        Creates a new Index instance.
        """

        self.config = None
        self.reader = None

    def __call__(self, args):
        """
        Main process for streaming content and building an embeddings index. Another process is spawned that
        streams articles to load into the embeddings index.

        Args:
            args: command line arguments
        """

        # Encoding parameters
        queue = Queue(5)

        # Dataset reader process
        process = Process(target=self.reader, args=(queue, args))
        process.start()

        # Total size
        total = queue.get()

        # Embedding index parameters
        embeddings = Embeddings(self.config)

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
