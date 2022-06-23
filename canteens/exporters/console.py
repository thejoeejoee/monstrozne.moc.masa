import sys
from io import StringIO
from operator import attrgetter

from canteens.exporters.base import BaseExporter
from canteens.types import Meal, Canteen


class ConsoleExporter(BaseExporter):
    def __init__(self, target: StringIO=sys.stdout, **kwargs):
        self._report_to = StringIO()
        self._target = target
        super().__init__()

    def generate(self, canteens: set[Canteen], meals: set[Meal], stats=''):
        print(f'⚠ {self.get_now_formatted()} ⚠️ \n️', file=self._report_to)
        print(f'Masa z dnešní nabídky: {self.get_meal_ratio_formated(meals=meals)}', file=self._report_to, )
        print(''.join(map(attrgetter('vege_status_mark'), meals)), file=self._report_to, )

    def export(self):
        self._target.write(self._report_to.getvalue())
