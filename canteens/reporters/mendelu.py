import datetime
import re
from pathlib import Path

import bs4 as bs4
import requests

from ..types import Meal, Canteen, University
from ..decisions import IS_NOT_MAIN_MEAL
from .base import BaseReporter


class ReporterMENDELU(BaseReporter):
    CANTEENS_API_URL = "https://skm.mendelu.cz/stravovani/28603-jidelni-listek"

    IS_NOT_MAIN_MEAL = re

    async def fetch(self):
        response = requests.get(self.CANTEENS_API_URL)
        response.raise_for_status()

        content = response.text

        # with open(Path(__file__).parent / 'mendelu.html', 'w') as f:
        #     f.write(content)

        dom = bs4.BeautifulSoup(content, 'html.parser')
        local_today_date = '{d.day}. {d.month}. {d.year}'.format(d=datetime.datetime.now())

        all_meals = set()
        all_canteens = set()

        for canteen_tab_el in dom.select('#tabs [id^=vydejna-]'):
            menu_el = None
            for date_title_el in canteen_tab_el.select('h3'):
                if local_today_date in date_title_el.text:
                    menu_el = date_title_el.find_next_sibling()
                    break

            if not menu_el:
                continue

            meals = set()

            seen_main_meal_title = False

            for meal_row_el in menu_el.select('tr'):
                if meal_row_el.find(text='Hlavní jídlo'):
                    seen_main_meal_title = True
                    continue

                if not seen_main_meal_title:
                    continue

                if meals and meal_row_el.select_one('.j-kategorie'):
                    # already bellow main meals
                    break

                name = meal_row_el.select_one('.j-slozeni').text
                ingredients = frozenset(map(lambda el: el.attrs['title'],
                                            meal_row_el.select('span:not(.j-slozeni)')))

                meal = Meal(name, ingredients)
                meals.add(meal)
                all_meals.add(meal)

            for permanent_offer_el in canteen_tab_el.select('.notice-board li'):
                name = permanent_offer_el.select_one('.j-slozeni').text
                ingredients = frozenset(map(lambda el: el.attrs['title'],
                                            permanent_offer_el.select('span:not(.j-slozeni)')))

                if IS_NOT_MAIN_MEAL.search(name):
                    continue

                meal = Meal(name, ingredients)
                meals.add(meal)
                all_meals.add(meal)

            if meals:
                # add onl cateens with som meals
                canteen_name = dom.select_one(f'a[href="#{canteen_tab_el.attrs.get("id")}"]').text
                all_canteens.add(Canteen(University.MENDELU, canteen_name, tuple(meals)))

        return all_canteens, all_meals
