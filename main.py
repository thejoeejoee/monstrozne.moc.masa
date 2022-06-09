#!/bin/env python3
from __future__ import annotations

import dataclasses
import logging
import re
import time
from operator import attrgetter
from pathlib import Path
from pprint import pprint

import click
import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

IS_MEAT = re.compile(
    r'kuře|'
    r'slan|'
    r'klobá|'
    r'hově|'
    r'říz|'
    r'kachn|'
    r'steak|'
    r'šunk|'
    r'vepř',
    re.IGNORECASE | re.VERBOSE
)

IS_PIZZA = re.compile(
    r'pizza',
    re.IGNORECASE | re.VERBOSE
)


def find_meat_part(meal: dict) -> str | None:
    for part in meal.get('slozeni'):
        if IS_MEAT.search(part):
            return part

    return None


@dataclasses.dataclass(frozen=True)
class Meal:
    name: str
    ingredients: frozenset[str]

    meal_type_mark: str = ''
    vege_status_mark: str = ''

    @property
    def is_pizza(self):
        return IS_PIZZA.search(self.name) is not None

    @property
    def meat_part(self):
        for part in self.ingredients:
            if IS_MEAT.search(part):
                return part
        return None

    def __post_init__(self):
        is_pizza = self.is_pizza
        meat_part = self.meat_part

        object.__setattr__(self, 'meal_type_mark', '🍕' if is_pizza else '🥩' if meat_part else '🌱')
        object.__setattr__(self, 'vege_status_mark', '🛑' if meat_part else '💚')

    def __str__(self):
        return f'{self.meal_type_mark} {self.name} ' \
               f'{self.vege_status_mark}' \
               f'{(" " + self.meat_part) if self.meat_part else ""}'


@click.command()
@click.option('--vut-username')
@click.option('--vut-password')
@click.option('--api-url', default='https://api.vut.cz/api/kamb/jidelnicek/v1')
def main(vut_username, vut_password, api_url):
    response = requests.get(
        api_url,
        auth=(vut_username, vut_password)
    )
    response.raise_for_status()

    all_meals = set()
    for canteen in response.json().get('data') or []:
        canteen_name = canteen.get('nazev')
        menu = canteen.get('menu') or []
        if not canteen_name or not menu or (len(menu) == 1 and not menu[0]):
            continue
        print(canteen_name)
        meals = []
        for meal_data in menu:
            if 'Hl. jídlo' in meal_data.get('typ', ''):
                name = meal_data.get('popis')
                ingredients = meal_data.get('slozeni')

                meal = Meal(name, frozenset(ingredients))
                print('\t', meal)
                meals.append(meal)
                all_meals.add(meal)

        meals_wo_pizza = tuple(filter(lambda m: not m.is_pizza, meals))
        vege_rate_wo_pizza = \
            len(tuple(filter(lambda m: m.vege_status_mark == '💚', meals_wo_pizza))) / len(meals_wo_pizza)
        vege_rate_w_pizza = \
            len(tuple(filter(lambda m: m.vege_status_mark == '💚', meals))) / len(meals)

        if len(meals_wo_pizza) != len(meals):
            # pizzas
            print(
                f'\t= Vege dishes w/o pizzas: {vege_rate_wo_pizza * 100:.0f} %\n',
                f'\t= Vege dishes w pizzas: {vege_rate_w_pizza * 100:.0f} %\n',
                f"\t= {''.join(map(attrgetter('meal_type_mark'), meals))}",
            )
        else:
            # no pizzas:
            print(
                f'\t= Vege dishes: {vege_rate_wo_pizza * 100:.0f} %\n',
                f"\t= {''.join(map(attrgetter('meal_type_mark'), meals))}",
            )

    print('\n === OVERVIEW ===')
    rate = len(tuple(filter(lambda m: m.vege_status_mark == '💚', all_meals))) / len(all_meals)
    print(f'Vege dishes from canteens offer today: {rate * 100:.0f} %')
    print(''.join(map(attrgetter('vege_status_mark'), all_meals)))


if __name__ == '__main__':
    main(auto_envvar_prefix='_')
