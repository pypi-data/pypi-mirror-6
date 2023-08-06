# -*- coding: utf-8 -*-
"""Custom Batch Provider for listing results."""

# zope imports
from Products.CMFPlone.PloneBatch import Batch
try:
    from Products.CMFPlone.PloneBatch import LazyNextBatch, LazyPrevBatch
    USE_OLD_BATCHING = True
except ImportError:
    USE_OLD_BATCHING = False


if USE_OLD_BATCHING:
    class LazyListingPrevBatch(LazyPrevBatch):
        """Previous listing result batch."""

        def __of__(self, parent):
            return ListingBatch(
                parent._sequence,
                parent._size,
                parent.first - parent._size + parent.overlap,
                0,
                parent.orphan,
                parent.overlap,
                batch_data=parent.batch_data,
            )

    class LazyListingNextBatch(LazyNextBatch):
        """Next listing result batch."""

        def __of__(self, parent):
            if parent.end >= (parent.last + parent.size):
                return None
            return ListingBatch(
                parent._sequence,
                parent._size,
                parent.end - parent.overlap,
                0,
                parent.orphan,
                parent.overlap,
                batch_data=parent.batch_data,
            )

    class ListingBatch(Batch):
        """Listing result batch."""
        __allow_access_to_unprotected_subobjects__ = 1

        previous = LazyListingPrevBatch()
        next = LazyListingNextBatch()

        def __init__(self, sequence, size, start=0, end=0, orphan=0, overlap=0,
                     pagerange=7, quantumleap=0, b_start_str='b_start',
                     batch_data=None):
            self.batch_data = batch_data
            if self.batch_data is not None:
                length = 0
                if sequence is not None:
                    length = len(sequence)
                self.sequence_length = self.batch_data.get('results', length)

            if sequence is None:
                sequence = []

            super(ListingBatch, self).__init__(
                sequence, size, start, end, orphan, overlap, pagerange,
                quantumleap, b_start_str,
            )

        def __getitem__(self, index):
            if index >= self.length:
                raise IndexError(index)
            return self._sequence[index]

else:
    class ListingBatch(Batch):
        """Listing result batch."""

        def __init__(self, sequence, size, start=0, end=0, orphan=0, overlap=0,
                     pagerange=7, quantumleap=0, b_start_str='b_start',
                     batch_data=None):
            self.batch_data = batch_data

            if sequence is None:
                sequence = []

            super(ListingBatch, self).__init__(
                sequence, size, start, end, orphan, overlap, pagerange,
                quantumleap, b_start_str,
            )

        @property
        def sequence_length(self):
            """Effective length of sequence."""
            if self.batch_data is not None:
                length = getattr(self, 'pagesize', 0)
                return self.batch_data.get('results', length)
            return super(ListingBatch, self).sequence_length

        def __getitem__(self, index):
            if index >= self.length:
                raise IndexError(index)
            return self._sequence[index]

        @property
        def next(self):
            """Next batch page."""
            if USE_OLD_BATCHING:
                return LazyListingNextBatch()

            if self.end >= (self.last + self.pagesize):
                return None
            return ListingBatch(
                self._sequence, self._size, self.end - self.overlap, 0,
                self.orphan, self.overlap, batch_data=self.batch_data,
            )

        @property
        def previous(self):
            """Previous batch page."""
            if USE_OLD_BATCHING:
                return LazyListingPrevBatch()

            if not self.first:
                return None
            return ListingBatch(
                self._sequence, self._size,
                self.first - self._size + self.overlap, 0, self.orphan,
                self.overlap, batch_data=self.batch_data,
            )
