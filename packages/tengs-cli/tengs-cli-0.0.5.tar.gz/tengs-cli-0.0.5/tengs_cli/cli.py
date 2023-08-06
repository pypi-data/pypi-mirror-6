from tengs_cli import actions

import argparse

def main():
    description = 'tengs - A command line tool to interact with http://tengs.herokuapp.com/'
    parser = argparse.ArgumentParser(description=description)

    parsers = parser.add_subparsers()

    login_parser = parsers.add_parser("login")
    login_parser.add_argument('github_name', type=str)
    login_parser.add_argument('api_key', type=str)
    login_parser.set_defaults(func=actions.login)

    fetch_parser = parsers.add_parser("fetch")
    fetch_parser.set_defaults(func=actions.fetch)

    submit_parser = parsers.add_parser("submit")
    submit_parser.set_defaults(func=actions.submit)


    args = parser.parse_args()
    args.func(args)
