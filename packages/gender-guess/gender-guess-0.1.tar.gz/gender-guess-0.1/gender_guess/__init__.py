# gender-guess  -- guessing the gender by firstname
# Copyright (C) 2014 - Alexander Weigl
#
# This file is part of gender_guess-gues.
#
# gender_guess-guessis free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# gender_guess-guess is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar. If not, see <http://www.gnu.org/licenses/>.


__author__ = "Alexander Weigl"
__date__ = "2014-04-18"
__version__ = "0.1beta"

import gender_guess._gender as g
import os.path

g.cvar.first_file_name = os.path.join(
    os.path.dirname(__file__), "nam_dict.txt")


class Country(object):
    ANY_COUNTRY = g.GC_ANY_COUNTRY
    BRITAIN = g.GC_BRITAIN
    IRELAND = g.GC_IRELAND
    USA = g.GC_USA
    SPAIN = g.GC_SPAIN
    PORTUGAL = g.GC_PORTUGAL
    ITALY = g.GC_ITALY
    MALTA = g.GC_MALTA
    FRANCE = g.GC_FRANCE
    BELGIUM = g.GC_BELGIUM
    LUXEMBOURG = g.GC_LUXEMBOURG
    NETHERLANDS = g.GC_NETHERLANDS
    GERMANY = g.GC_GERMANY
    EAST_FRISIA = g.GC_EAST_FRISIA
    AUSTRIA = g.GC_AUSTRIA
    SWISS = g.GC_SWISS
    ICELAND = g.GC_ICELAND
    DENMARK = g.GC_DENMARK
    NORWAY = g.GC_NORWAY
    SWEDEN = g.GC_SWEDEN
    FINLAND = g.GC_FINLAND
    ESTONIA = g.GC_ESTONIA
    LATVIA = g.GC_LATVIA
    LITHUANIA = g.GC_LITHUANIA
    POLAND = g.GC_POLAND
    CZECH_REP = g.GC_CZECH_REP
    SLOVAKIA = g.GC_SLOVAKIA
    HUNGARY = g.GC_HUNGARY
    ROMANIA = g.GC_ROMANIA
    BULGARIA = g.GC_BULGARIA
    BOSNIA = g.GC_BOSNIA
    CROATIA = g.GC_CROATIA
    KOSOVO = g.GC_KOSOVO
    MACEDONIA = g.GC_MACEDONIA
    MONTENEGRO = g.GC_MONTENEGRO
    SERBIA = g.GC_SERBIA
    SLOVENIA = g.GC_SLOVENIA
    ALBANIA = g.GC_ALBANIA
    GREECE = g.GC_GREECE
    RUSSIA = g.GC_RUSSIA
    BELARUS = g.GC_BELARUS
    MOLDOVA = g.GC_MOLDOVA
    UKRAINE = g.GC_UKRAINE
    ARMENIA = g.GC_ARMENIA
    AZERBAIJAN = g.GC_AZERBAIJAN
    GEORGIA = g.GC_GEORGIA
    KAZAKH_UZBEK = g.GC_KAZAKH_UZBEK
    TURKEY = g.GC_TURKEY
    ARABIA = g.GC_ARABIA
    ISRAEL = g.GC_ISRAEL
    CHINA = g.GC_CHINA
    INDIA = g.GC_INDIA
    JAPAN = g.GC_JAPAN
    KOREA = g.GC_KOREA
    VIETNAM = g.GC_VIETNAM


class Result(object):
    IS_FEMALE = 'F'
    IS_MOSTLY_FEMALE = 'f'
    IS_MALE = 'M'
    IS_MOSTLY_MALE = 'm'
    IS_UNISEX_NAME = '?'
    IS_A_COUPLE = 'C'

    EQUIVALENT_NAMES = '='
    NOT_EQUAL_NAMES = '!'
    NAME_NOT_FOUND = ' '
    ERROR_IN_NAME = 'E'
    INTERNAL_ERROR_GENDER = 'I'


class CompareMode(object):
    COMPARE_EXPANDED_UMLAUTS = 0
    TRACE_ALL_COUNTRIES = 0
    TRACE_FULL_COUNTRY_NAME = 0

    ALLOW_COMPRESSED_UMLAUTS = 1
    ALLOW_COUPLE = 2

    TRACE_ONE_COUNTRY_ONLY = 4
    TRACE_SHORT_COUNTRY_NAME = 8

class GenderAttributeException(Exception):
    pass

def _get_values(clazz):
    return {getattr(clazz, attrib) for attrib in dir(clazz)}

def _country_valid(country):
    return country in _get_values(Country)

def _compare_mode_valid(cmp_mode):
    return cmp_mode in _get_values(CompareMode)

def guess_gender(first_name, compare_mode  = CompareMode.COMPARE_EXPANDED_UMLAUTS, country = Country.ANY_COUNTRY):
	if type(first_name) is unicode:
	    return chr(g.get_gender_unicode(first_name, compare_mode, country))
	else:
	    return chr(g.get_gender(first_name, compare_mode, country))
