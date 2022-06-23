#!/bin/env python3
from __future__ import annotations

import logging

import click
from dotenv import load_dotenv

from canteens.exporters.console import ConsoleExporter
from canteens.exporters.instagram import InstagramExporter
from canteens.reporters.muni import ReporterMUNI
from canteens.reporters.vut import ReporterVUT
from canteens.utils import native_coroutine

logging.basicConfig(level=logging.INFO)

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
    vut_canteens, vut_meals = await vut.fetch()

    muni = ReporterMUNI(**ctx.params)
    muni_canteens, muni_meals = await muni.fetch()

    console = ConsoleExporter(**ctx.params, verbose=False)
    print(f'⚠ {console.get_now_formatted()} ⚠️ \n️', file=console._report_to)

    console.generate_report(canteens=vut_canteens, meals=vut_meals)
    console.generate_report(canteens=muni_canteens, meals=muni_meals)
    console.export()

    instagram = InstagramExporter(**ctx.params)
    instagram.generate_report(canteens=vut_canteens, meals=vut_meals)

    # instagram.export()


if __name__ == '__main__':
    main(auto_envvar_prefix='_')
