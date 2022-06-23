import requests

from ..types import Meal, Canteen, University
from ..decisions import IS_NOT_MAIN_MEAL
from .base import BaseReporter


class ReporterVUT(BaseReporter):
    API_URL = "https://api.vut.cz/api/kamb/jidelnicek/v1"

    def __init__(self, vut_username, vut_password, vut_api_url, *args, **kwargs):
        self._auth = (vut_username, vut_password)
        self._api_url = vut_api_url or self.API_URL

    async def fetch(self):
        response = requests.get(
            self._api_url,
            auth=self._auth,
        )
        response.raise_for_status()
        all_meals = set()
        all_canteens = set()

        for canteen in response.json().get('data') or []:
            canteen_name = canteen.get('nazev')
            menu = canteen.get('menu') or []

            # WTF VUT API :-D
            #  "data": [
            #     {
            #       "casR": "21. 6. 2022 10:58:45",
            #       "casA": "21. 6. 2022 10:57:58"
            #     },
            #     ... other canteens

            if not canteen_name or not menu or (len(menu) == 1 and not menu[0]):
                continue

            meals = []
            for meal_data in menu:
                if 'Hl. jídlo' not in meal_data.get('typ', ''):
                    continue

                name = meal_data.get('popis')

                if IS_NOT_MAIN_MEAL.search(name):
                    continue

                ingredients = meal_data.get('slozeni')

                meal = Meal(name, frozenset(ingredients))
                meals.append(meal)
                all_meals.add(meal)

            canteen = Canteen(University.VUT, canteen_name, tuple(meals))
            all_canteens.add(canteen)

        return all_canteens, all_meals
