""" Convert swagger api file to YAML/JSON testcase for HttpRunner.
Usage:
    # convert to JSON format testcase
    >>> swagger2case demo.json
    # convert to YAML format testcase
    >>> hswagger2case demo.json -2y
"""
import argparse
import sys
from swagger2case.__about__ import __version__
from loguru import logger
from swagger2case.core import SwaggerParser

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-V', '--version', dest='version', action='store_true',
        help="show version"
    )
    parser.add_argument(
        '--log-level', default='INFO',
        help="Specify logging level, default is INFO."
    )
    parser.add_argument('swagger_api_file', nargs='?',
        help="Specify swagger api file"
    )
    parser.add_argument(
        '-2y', '--to-yml', '--to-yaml',
        dest='to_yaml', action='store_true',
        help="Convert to YAML format, if not specified, convert to JSON format by default."
    )
    # parser.add_argument(
    #     '-fmt', '--format',
    #     dest='fmt_version', default='v1',
    #     help="Specify YAML/JSON testcase format version, v2 corresponds to HttpRunner 2.2.0+."
    # )
    parser.add_argument(
        '--filter', help="Specify filter keyword, only url include filter string will be converted."
    )
    parser.add_argument(
        '--exclude',
        help="Specify exclude keyword, url that includes exclude string will be ignored, \
        multiple keywords can be joined with '|'"
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        exit(0)

    if args.version:
        print(f"{__version__}")
        exit(0)

    swagger_api_file = args.swagger_api_file
    if not swagger_api_file or not swagger_api_file.endswith(".json"):
        logger.error("swagger api file not specified")
        exit(1)

    output_file_type = "YML" if args.to_yaml else "JSON"
    SwaggerParser(
        swagger_api_file, args.filter, args.exclude
    ).gen_testcase(output_file_type)

