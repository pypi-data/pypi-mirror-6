from tengs_cli import actions
from functools import partial
from tengs_cli import *

import argparse

def main():
    description = 'tengs - A command line tool to interact with http://tengs.herokuapp.com/'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-v', '--verbose', action='store_true')

    parsers = parser.add_subparsers()

    login_parser = parsers.add_parser("login")
    login_parser.add_argument('github_name', type=str)
    login_parser.add_argument('api_key', type=str, help="see on http://tengs.ru/account")
    login_parser.set_defaults(func=actions.login)

    fetch_parser = parsers.add_parser("fetch")
    fetch_parser.set_defaults(func=actions.fetch)

    submit_parser = parsers.add_parser("submit", description="it only works from teng exercise directory.")
    submit_parser.set_defaults(func=actions.submit)

    args = parser.parse_args()

    current_level = "info"
    if args.verbose:
        current_level = "debug"

    args.func(args, partial(logger, current_level))
