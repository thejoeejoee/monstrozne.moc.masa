#!/bin/env python3
from __future__ import annotations

import dataclasses
import datetime
import logging
import re
import time
from datetime import datetime
from io import StringIO
from operator import attrgetter
from pathlib import Path
from pprint import pprint
from colour import Color
from instagrapi import Client
import instabot
import click
import requests
from PIL import Image, ImageFont, ImageDraw
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

IS_MEAT = re.compile(
    r'kuře|'
    r'slan|'
    r'klobá|'
    r'salám|'
    r'gothaj|'
    r'guláš|'  # questionable
    r'hově|'
    r'říz|'
    r'kachn|'
    r'steak|'
    r'šunk|'
    r'ryb[aí]|'
    r'losos|'
    r'masem|' # uzeným masem
    r'vepř',
    re.IGNORECASE | re.VERBOSE
)

IS_PIZZA = re.compile(
    r'pizza',
    re.IGNORECASE | re.VERBOSE
)

IS_NOT_MAIN_MEAL = re.compile(
    r'bageta',
    re.IGNORECASE | re.VERBOSE
)


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

        # sometimes ingredients are empty, so we need to check the name itself
        if IS_MEAT.search(self.name):
            return self.name
        return None

    def __post_init__(self):
        is_pizza = self.is_pizza
        meat_part = self.meat_part

        object.__setattr__(self, 'meal_type_mark', '🍕' if is_pizza else '🥩' if meat_part else '🌱')
        object.__setattr__(self, 'vege_status_mark', '🛑' if meat_part else '💚')

    def __str__(self):
        return f'{self.meal_type_mark} {self.name} ' \
               f'{self.vege_status_mark}' \
               # f'{(" " + self.meat_part) if self.meat_part else ""}'



@dataclasses.dataclass(frozen=True)
class Canteen:
    name: str
    meals: list[Meal]


    @property
    def report(self):
        meals_wo_pizza = tuple(filter(lambda m: not m.is_pizza, self.meals))
        vege_rate_wo_pizza = \
            len(tuple(filter(lambda m: m.vege_status_mark == '💚', meals_wo_pizza))) / len(meals_wo_pizza)
        vege_rate_w_pizza = \
            len(tuple(filter(lambda m: m.vege_status_mark == '💚', self.meals))) / len(self.meals)

        meals = '\n'.join(str(m) for m in self.meals)

        if len(meals_wo_pizza) != len(self.meals):
            # pizzas
            return f'{meals}\n' \
                f'= Vege jídla kromě pizz: {vege_rate_wo_pizza * 100:.0f} %\n' \
                f'= Vege jídla včetně pizz: {vege_rate_w_pizza * 100:.0f} %\n' \
                f"= {''.join(map(attrgetter('meal_type_mark'), self.meals))}\n"

        else:
            return f'{meals}\n' \
                f'= Vege jídla: {vege_rate_wo_pizza * 100:.0f} %\n' \
                f"= {''.join(map(attrgetter('meal_type_mark'), self.meals))}\n"


@click.command()
@click.option('--vut-username')
@click.option('--vut-password')
@click.option('--ig-username')
@click.option('--ig-password')
@click.option('--api-url', default='https://api.vut.cz/api/kamb/jidelnicek/v1')
def main(vut_username, vut_password, api_url, ig_username, ig_password):
    response = requests.get(
        api_url,
        auth=(vut_username, vut_password)
    )
    response.raise_for_status()
    now_formatted = datetime.now().strftime('%H:%M %d.%m.%Y')

    reporter = StringIO()
    all_meals = set()
    canteens = []
    print(f'⚠ {now_formatted} ⚠️ \n️', file=reporter)
    for canteen in response.json().get('data') or []:
        canteen_name = canteen.get('nazev')
        menu = canteen.get('menu') or []
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

        canteen = Canteen(canteen_name, meals)
        canteens.append(canteen)

    rate = len(tuple(filter(lambda m: m.vege_status_mark == '💚', all_meals))) / len(all_meals)
    rate_formatted = f'{(1. - rate) * 100:.0f} %'
    print(f'Masa z dnešní nabídky: {rate_formatted}', file=reporter, )
    print(''.join(map(attrgetter('vege_status_mark'), all_meals)), file=reporter, )

    red = Color("red")
    colors = list(red.range_to(Color("green"), 10))

    main_font = ImageFont.truetype("font.ttf", 512)
    output = Image.open('./template.png')
    width, height = output.size
    draw = ImageDraw.ImageDraw(output)

    luminance_offset = abs(rate - 0.5) / 7

    # rate is 0..1
    # but 0.7 is fine for us --> complete green
    nice_rate = 0.5
    if rate > nice_rate:
        rate = 1

    text_color = colors[min(9, int(rate * 10))]
    text_color.set_luminance(text_color.get_luminance() - luminance_offset)
    draw.text(
        (width / 2, (height / 2) - 48),
        rate_formatted.replace(' ', ''),
        anchor="mm",
        fill=text_color.hex,
        font=main_font
    )

    side_font = ImageFont.truetype("font.ttf", 72  + 36)
    draw.text(
        (width / 2, height - 96),
        now_formatted,
        anchor="mm",
        fill='#444',
        font=side_font
    )

    output.convert('RGB').save('output.jpg', "JPEG")

    print(reporter.getvalue())

    ig_bot = Client()
    ig_bot.login(ig_username, ig_password)

    media = ig_bot.photo_upload(
        Path('output.jpg'),
        caption=f'Dnešní report ⚠ {now_formatted}',
    )

    for c in canteens:
        ig_bot.media_comment(
            media_id=media.id,
            text=f"{c.name}\n\n{c.report}",
        )

    # https://adw0rd.github.io/instagrapi/usage-guide/story.html


if __name__ == '__main__':
    main(auto_envvar_prefix='_')
