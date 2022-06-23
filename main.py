#!/bin/env python3
from __future__ import annotations

import datetime
import logging
from datetime import datetime
from io import StringIO
from operator import attrgetter
from pathlib import Path
from colour import Color
from instagrapi import Client
import click
from PIL import Image, ImageFont, ImageDraw
from dotenv import load_dotenv

from canteens.exporters.console import ConsoleExporter
from canteens.exporters.instagram import InstagramExporter
from canteens.reporters.vut import ReporterVUT

from canteens.utils import native_coroutine

logging.basicConfig(level=logging.DEBUG)

load_dotenv()


@click.command()
@click.option('--vut-username')
@click.option('--vut-password')
@click.option('--ig-username')
@click.option('--ig-password')
@click.option('--vut-api-url')
@click.pass_context
@native_coroutine
async def main(ctx: click.Context, **kwargs):
    vut = ReporterVUT(**ctx.params)
    canteens, all_meals = await vut.fetch()

    console = ConsoleExporter(**ctx.params)
    console.generate(canteens=canteens, meals=all_meals)
    console.export()

    instagram = InstagramExporter(**ctx.params)
    instagram.generate(canteens=canteens, meals=all_meals)

    # instagram.export()


if __name__ == '__main__':
    main(auto_envvar_prefix='_')
