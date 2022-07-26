from abc import ABCMeta
from zoneinfo import ZoneInfo
from datetime import datetime
from pathlib import Path

from PIL import ImageFont, Image, ImageDraw
from colour import Color

from canteens.types import Canteen, Meal

BASE_DIR = Path(__file__).parent

FONT_PATH = (BASE_DIR / "font.ttf").as_posix()

OUTPUT_FILE_PATH = BASE_DIR.parent.parent / 'output.jpg'


class BaseExporter(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        ...

    def generate_report(self, canteens: set[Canteen], meals: set[Meal], stats):
        """Prepares data for posting."""
        ...

    def export(self):
        """Exports data to target channel."""
        ...

    @classmethod
    def get_vege_meals_count(cls, meals: set[Meal]):
        return len(tuple(filter(lambda m: m.vege_status_mark == '💚', meals)))

    @classmethod
    def get_vege_ratio(cls, meals: set[Meal]) -> float:
        return cls.get_vege_meals_count(meals) / len(meals)

    @classmethod
    def get_meal_ratio_formated(self, vege_ratio: float = None, meals: set[Meal] = None):
        ratio = vege_ratio or self.get_vege_ratio(meals)

        return f'{(1. - ratio) * 100:.0f} %'

    @classmethod
    def get_now_formatted(cls):
        return datetime.now().replace(tzinfo=ZoneInfo('Europe/Prague')).strftime('%H:%M %d.%m.%Y')

    @classmethod
    def export_image(cls, all_meals: set[Meal], output_path: Path = OUTPUT_FILE_PATH):
        rate = cls.get_vege_ratio(meals=all_meals)

        red = Color("red")
        colors = list(red.range_to(Color("green"), 10))

        main_font = ImageFont.truetype(FONT_PATH, 512)
        output = Image.open(BASE_DIR / './template.png')
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
            cls.get_meal_ratio_formated(meals=all_meals).replace(' ', ''),
            anchor="mm",
            fill=text_color.hex,
            font=main_font
        )

        side_font = ImageFont.truetype(FONT_PATH, 72 + 36)
        draw.text(
            (width / 2, height - 96),
            cls.get_now_formatted(),
            anchor="mm",
            fill='#444',
            font=side_font
        )

        output.convert('RGB').save(output_path, "JPEG")
