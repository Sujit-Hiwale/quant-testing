from abc import ABC, abstractmethod

from src.core.models import Bar, Order


class Strategy(ABC):

    @abstractmethod
    def on_bar(self, bar: Bar) -> Order | None:
        """
        Process a market bar and optionally
        generate an order.

        Orders generated from this bar are
        executed on a future bar.
        """
        raise NotImplementedError
