'''
A wrapper for the FCC Census Block Conversions API
http://www.fcc.gov/developers/census-block-conversions-api
'''
import requests
import json

import argparse
import sys


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
    return requests.get(base_url.format(**parameters)).text


def census_block_dict(latitude, longitude, year=None, showall=None):
    '''Get the FCC API response as a Python dictionary.'''
    return json.loads(census_block(latitude, longitude, year, 'json', showall))


def census_block_fips(latitude, longitude, year=None):
    '''
    Get only the census block FIPS code.
    Only return the first if the location corresponds to more than one code.
    '''
    return census_block_dict(latitude, longitude, year)['Block']['FIPS']


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
    return parser.parse_args()


def main():
    args = parse_command_line_args()
    def writeline(entry):
        args.output.write('{0}\n'.format(entry))

    if args.latitude and args.longitude:
        writeline(census_block_fips(args.latitude, args.longitude))
    else:
        for line in args.input:
            writeline(census_block_fips(*line.strip().split(',')))


if __name__ == '__main__':
    '''This module should not be run at the command line directly.'''
    pass
