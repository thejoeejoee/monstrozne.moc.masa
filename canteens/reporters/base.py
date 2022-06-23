from abc import ABCMeta
from typing import Tuple, Set

from canteens.types import Canteen, Meal


class BaseReporter(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        ...

    async def fetch(self) -> Tuple[Set[Canteen], Set[Meal]]:
        """
        Returns all canteens (w some meals) and all meals provided by one university.
        """
        ...
