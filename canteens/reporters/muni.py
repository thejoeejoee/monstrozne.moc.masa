import datetime
import re

import requests

from ..types import Meal, Canteen, University
from ..decisions import IS_NOT_MAIN_MEAL
from .base import BaseReporter


class ReporterMUNI(BaseReporter):
    CANTEENS_API_URL = "https://kredit.skm.muni.cz/WebKredit/Api/Ordering/Ordering?CanteenId=30" \
                       "&DateFrom={date}&DateTo={date}"
    MENU_API_URL = "https://kredit.skm.muni.cz/WebKredit/Api/Ordering/Menu?Dates={date}&CanteenId={canteen}"

    IS_RELEVANT_GROUP = re.compile(
        r'Obědy|'
        r'Týdenní|'
        r'Pizza',
        re.IGNORECASE | re.VERBOSE
    )

    @classmethod
    def meals_from_relevant_groups(cls, groups: list[dict]):
        for g in groups:
            if not cls.IS_RELEVANT_GROUP.search(g.get('mealKindName') or ''):
                continue

            yield from g.get('rows')

    async def fetch(self):
        request_date = datetime.date.today().strftime('%Y-%m-%dT22:00:00.000Z')

        all_meals = set()
        all_canteens = set()

        canteens_req = requests.get(self.CANTEENS_API_URL.format(date=request_date))

        for canteen_data in canteens_req.json().get('canteens'):
            c_id = canteen_data.get('id')

            response = requests.get(
                self.MENU_API_URL.format(date=request_date, canteen=c_id),
            )
            response.raise_for_status()
            data = response.json()

            groups = data.get('groups')
            if not groups:
                continue

            meals = []
            for meal_data in self.meals_from_relevant_groups(groups=groups):
                meal_data = meal_data.get('item')
                name = meal_data.get('mealName')

                ingredients = map(str.strip, (meal_data.get('allergens') or '').split(','))

                meal = Meal(name, frozenset(ingredients))
                meals.append(meal)
                all_meals.add(meal)

            if not meals:
                # extracted no main meals
                continue

            canteen = Canteen(University.MUNI, canteen_data.get('name'), tuple(meals))
            all_canteens.add(canteen)

        return all_canteens, all_meals
