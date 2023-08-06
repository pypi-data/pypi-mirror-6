'''
A wrapper for the FCC Census Block Conversions API
http://www.fcc.gov/developers/census-block-conversions-api
'''
import requests
import json
import argparse
import sys
from .core import retry_on_none, retry_on_exception

import logging
logger = logging.getLogger('fcc.census_block_conversions')


@retry_on_exception
def census_block(latitude, longitude, year=None, format=None, showall=None):
    '''Get the FCC API response in the specified text format.'''
    base_url = 'http://data.fcc.gov/api/block/{year}{lat}{lng}{show}{fmt}'
    parameters = {
        'year': str(year) + '/find?' if year else 'find?',
        'lat': 'latitude=' + str(latitude),
        'lng': '&longitude=' + str(longitude),
        'show': '&showall=true' if showall else '',
        'fmt': '&format=' + format.lower() if format else ''
    }
    data = requests.get(base_url.format(**parameters)).text
    logging.debug('RESPONSE: {0}'.format(data))
    return data


def census_block_dict(latitude, longitude, year=None, showall=None):
    '''Get the FCC API response as a Python dictionary.'''
    try:
        return json.loads(census_block(latitude, longitude, year, 'json', showall))
    except ValueError as e:
        if str(e) == 'No JSON object could be decoded':
            logging.warning('{0}: {1}'.format(e, (latitude,longitude,year,showall)))
            return None
        raise e


def census_block_fips(latitude, longitude, year=None):
    '''
    Get only the census block FIPS code.
    Only return the first if the location corresponds to more than one code.
    '''
    try:
        return census_block_dict(latitude, longitude, year)['Block']['FIPS']
    except TypeError as e:
        if str(e) == "'NoneType' object is not subscriptable":
            logging.warning('{0}: {1}'.format(e, (latitude, longitude, year)))
            return None
        raise e


def parse_command_line_args():
    '''Parse the command line arguments'''
    msg = '''Read geographic location as latitude-longitude pairs.
        Write location as FIPS codes
        (http://www.census.gov/geo/reference/ansi.html).'''
    parser = argparse.ArgumentParser(description = msg)
    parser.add_argument('latitude', nargs='?')
    parser.add_argument('longitude', nargs='?')
    file_usage = 'One "latitude,longitude" pair per line, comma-separated.'
    parser.add_argument('-i', '--input', type=argparse.FileType('r'),
                        nargs='?', default=sys.stdin, help=file_usage)
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        nargs='?', default=sys.stdout)
    parser.add_argument('-d', '--delimiter', type=str, nargs='?', default=',')
    parser.add_argument('-v', '--verbose', action='store_true')
    return parser.parse_args()


def main():
    args = parse_command_line_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if args.latitude and args.longitude:
        fips = census_block_fips(args.latitude, args.longitude)
        args.output.write('{0}\n'.format(fips))
    else:
        delim = bytes(args.delimiter, 'utf-8').decode('unicode_escape')
        for line in args.input:
            fips = census_block_fips(*line.strip().split(delim))
            args.output.write('{0}\n'.format(fips))


if __name__ == '__main__':
    '''
    This module should not be run at the command line directly.
    use `$ python cli.py ...` or `$ census_block_conversions ...` instead.
    '''
    pass
