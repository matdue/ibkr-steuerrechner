import io
from typing import Iterator


class IterableTextIO(io.TextIOBase):
    """
    Makes an iterable of strings to be used as a file-like object.

    Usage:
    with IterableTextIO(some_iterable_of_string) as s:
        df = pd.read_csv(s)

    This class has been influenced by https://stackoverflow.com/a/20260030
    """
    def __init__(self, iterable: Iterator[str]):
        """
        Creates a new instance which allow reading an iterable of strings like a file.

        :param iterable: Iterable of strings
        """
        self.iterable = iterable
        self.leftover = None

    def read(self, size: int = -1) -> str:
        try:
            chunk = self.leftover or next(self.iterable)
            output, self.leftover = chunk[:size], chunk[size:]
            return output
        except StopIteration:
            return ""    # indicate EOF
