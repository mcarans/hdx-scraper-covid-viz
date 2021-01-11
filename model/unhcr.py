# -*- coding: utf-8 -*-
import inspect
import logging

from os.path import join

from dateutil.relativedelta import relativedelta
from hdx.utilities.dateparse import parse_date

logger = logging.getLogger(__name__)


def get_unhcr(configuration, today, today_str, countryiso3s, downloader, scrapers=None):
    name = inspect.currentframe().f_code.co_name
    if scrapers and not any(scraper in name for scraper in scrapers):
        return list(), list(), list()
    iso3tocode = downloader.download_tabular_key_value(join('config', 'UNHCR_geocode.csv'))
    unhcr_configuration = configuration['unhcr']
    base_url = unhcr_configuration['url']
    population_collections = unhcr_configuration['population_collections']
    exclude = unhcr_configuration['exclude']
    valuedicts = [dict(), dict()]
    for countryiso3 in countryiso3s:
        if countryiso3 in exclude:
            continue
        code = iso3tocode.get(countryiso3)
        if not code:
            continue
        for population_collection in population_collections:
            r = downloader.download(base_url % (population_collection,  code))
            data = r.json()['data'][0]
            individuals = data['individuals']
            if individuals is None:
                continue
            date = data['date']
            if parse_date(date) < today - relativedelta(years=2):
                continue
            existing_individuals = valuedicts[0].get(countryiso3)
            if existing_individuals is None:
                valuedicts[0][countryiso3] = int(individuals)
                valuedicts[1][countryiso3] = date
            else:
                valuedicts[0][countryiso3] += int(individuals)
    logger.info('Processed UNHCR')
    hxltags = ['#affected+refugees', '#affected+date+refugees']
    return [['TotalRefugees', 'TotalRefugeesDate'], hxltags], valuedicts, [(hxltag, today_str, 'UNHCR', unhcr_configuration['source_url']) for hxltag in hxltags]
