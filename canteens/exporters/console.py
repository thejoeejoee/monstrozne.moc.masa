import sys
from io import StringIO
from operator import attrgetter

from canteens.exporters.base import BaseExporter
from canteens.types import Meal, Canteen


class ConsoleExporter(BaseExporter):
    def __init__(self, target: StringIO = sys.stdout, verbose=True, **kwargs):
        self._report_to = StringIO()
        self._target = target
        self._verbose = verbose
        super().__init__()

    def generate_report(self, canteens: set[Canteen], meals: set[Meal], stats=''):
        canteens = tuple(canteens)
        if not canteens:
            return

        if self._verbose:
            for c in canteens:
                print(f"{c.title}\n{c.report}", file=self._report_to)

        print(canteens[0].university_header, file=self._report_to, )
        meals_count = len(meals)
        print(f'Masa z dnešní nabídky: '
              f'{self.get_meal_ratio_formated(meals=meals)} '
              f'({meals_count - self.get_vege_meals_count(meals=meals)}/{meals_count})', file=self._report_to, )
        print(''.join(map(attrgetter('vege_status_mark'), meals)), file=self._report_to, )
        print('', file=self._report_to, )

    def export(self):
        self._target.write(self._report_to.getvalue())
