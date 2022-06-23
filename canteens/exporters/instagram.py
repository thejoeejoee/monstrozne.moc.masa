from pathlib import Path

from instagrapi import Client

from canteens.exporters.base import BaseExporter, OUTPUT_FILE_PATH
from canteens.types import Canteen, Meal


class InstagramExporter(BaseExporter):
    def __init__(self, ig_username, ig_password, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._auth = (ig_username, ig_password)

        self._canteens = None

    def generate(self, canteens: set[Canteen], meals: set[Meal], stats = None):
        self.export_image(all_meals=meals)
        self._canteens = canteens

    def export(self):
        ig_bot = Client()
        ig_bot.login(*self._auth)

        media = ig_bot.photo_upload(
            OUTPUT_FILE_PATH,
            caption=f'Dnešní report ⚠ {self.get_now_formatted()}',
        )

        for c in self._canteens:
            ig_bot.media_comment(
                media_id=media.id,
                text=f"{c.name}\n\n{c.report}",
            )

        # https://adw0rd.github.io/instagrapi/usage-guide/story.html