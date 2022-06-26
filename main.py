#!/bin/env python3
from __future__ import annotations

import logging
from io import StringIO

import click
from dotenv import load_dotenv

from canteens.exporters.console import ConsoleExporter
from canteens.exporters.instagram import InstagramExporter
from canteens.reporters.mendelu import ReporterMENDELU
from canteens.reporters.muni import ReporterMUNI
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
    vut_canteens, vut_meals = await vut.fetch()

    muni = ReporterMUNI(**ctx.params)
    muni_canteens, muni_meals = await muni.fetch()

    mendelu = ReporterMENDELU(**ctx.params)
    mendelu_canteens, mendelu_meals = await mendelu.fetch()

    console_verbose = ConsoleExporter(**ctx.params, verbose=True)
    brief = StringIO()
    console_brief = ConsoleExporter(**ctx.params, target=brief, verbose=False)

    print(f'⚠ {console_verbose.get_now_formatted()} ⚠️ \n️', file=console_verbose._report_to)

    console_verbose.generate_report(canteens=vut_canteens, meals=vut_meals)
    console_brief.generate_report(canteens=vut_canteens, meals=vut_meals)
    console_verbose.generate_report(canteens=muni_canteens, meals=muni_meals)
    console_brief.generate_report(canteens=muni_canteens, meals=muni_meals)
    console_verbose.generate_report(canteens=mendelu_canteens, meals=mendelu_meals)
    console_brief.generate_report(canteens=mendelu_canteens, meals=mendelu_meals)
    console_verbose.export()
    console_brief.export()

    instagram = InstagramExporter(**ctx.params)
    instagram.generate_report(
        canteens=vut_canteens | muni_canteens | mendelu_canteens,
        meals=vut_meals # overall percentage only from VUT meals
    )

    instagram.export(ext_report=brief.getvalue())


if __name__ == '__main__':
    main(auto_envvar_prefix='_')
