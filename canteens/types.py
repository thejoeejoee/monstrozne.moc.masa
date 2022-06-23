from __future__ import annotations

import dataclasses
from _operator import attrgetter
from enum import Enum

from .decisions import IS_PIZZA, IS_MEAT, IS_NOT_MAIN_MEAL


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


class University(Enum):
    VUT = '🟥'
    MUNI = '🟦'
    MENDELU = '🟩'

@dataclasses.dataclass(frozen=True)
class Canteen:
    university: University
    name: str
    meals: tuple[Meal]

    @property
    def university_header(self):
        return f'{self.university.name} {self.university.value * 3}'

    @property
    def title(self):
        return f'{self.university_header} {self.name}'

    @property
    def report(self):
        meals_wo_pizza = tuple(filter(lambda m: not m.is_pizza, self.meals))
        vege_rate_wo_pizza = \
            len(tuple(filter(lambda m: m.vege_status_mark == '💚', meals_wo_pizza))) / len(meals_wo_pizza) \
            if meals_wo_pizza else 0

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
