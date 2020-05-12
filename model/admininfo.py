# -*- coding: utf-8 -*-
import logging
from difflib import get_close_matches

from hdx.utilities.text import multiple_replace
from unidecode import unidecode
from hdx.location.country import Country

logger = logging.getLogger(__name__)


class AdminInfo(object):
    pcodes = list()
    name_to_pcode = dict()
    pcode_to_name = dict()
    pcode_to_iso3 = dict()

    def __init__(self, configuration):
        admin_info = configuration['admin_info']
        self.adm1_name_replacements = configuration['adm1_name_replacements']
        countryiso3s = set()
        for row in admin_info:
            countryiso3 = row['alpha_3']
            countryiso3s.add(countryiso3)
            pcode = row['ADM1_PCODE']
            self.pcodes.append(pcode)
            adm1_name = row['ADM1_REF']
            self.pcode_to_name[pcode] = adm1_name
            name_to_pcode = self.name_to_pcode.get(countryiso3, dict())
            name_to_pcode[unidecode(adm1_name).lower()] = pcode
            self.name_to_pcode[countryiso3] = name_to_pcode
            self.pcode_to_iso3[pcode] = countryiso3
        self.countryiso3s = sorted(list(countryiso3s))

    def get_pcode(self, countryiso3, adm1_name):
        name_to_pcode = self.name_to_pcode.get(countryiso3)
        if not name_to_pcode:
            logger.error('Could not find %s in map names!' % countryiso3)
            return False
        adm1_name_lookup = unidecode(adm1_name)
        adm1_name_lookup2 = multiple_replace(adm1_name_lookup, self.adm1_name_replacements)
        adm1_name_lookup = adm1_name_lookup.lower()
        adm1_name_lookup2 = adm1_name_lookup2.lower()
        pcode = name_to_pcode.get(adm1_name_lookup, name_to_pcode.get(adm1_name_lookup2))
        if not pcode:
            for map_name in name_to_pcode:
                if adm1_name_lookup in map_name:
                    pcode = name_to_pcode[map_name]
                    logger.info('%s: Matching (substring) %s to %s on map' % (countryiso3, adm1_name, self.pcode_to_name[pcode]))
                    break
            for map_name in name_to_pcode:
                if adm1_name_lookup2 in map_name:
                    pcode = name_to_pcode[map_name]
                    logger.info(
                        '%s: Matching (substring) %s to %s on map' % (countryiso3, adm1_name, self.pcode_to_name[pcode]))
                    break
        if not pcode:
            map_names = list(name_to_pcode.keys())
            lower_mapnames = [x.lower() for x in map_names]
            matches = get_close_matches(adm1_name_lookup, lower_mapnames, 1, 0.8)
            if not matches:
                matches = get_close_matches(adm1_name_lookup2, lower_mapnames, 1, 0.8)
                if not matches:
                    logger.error('%s: Could not find %s in map names!' % (countryiso3, adm1_name))
                    return None
            index = lower_mapnames.index(matches[0])
            map_name = map_names[index]
            pcode = name_to_pcode[map_name]
            logger.info('%s: Matching (fuzzy) %s to %s on map' % (countryiso3, adm1_name, self.pcode_to_name[pcode]))
        return pcode