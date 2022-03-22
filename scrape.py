#!/usr/bin/env python3
from pubchem_scrapper import main


if __name__ == "__main__":
    arg_parser = main.build_arg_parser()
    try:
        namespace = arg_parser.parse_args()
    except SystemExit as err:
        if err.code != 0:
            arg_parser.parse_args("--help".split())
            exit(err.code)
        else:
            exit(0)
    else:
        args = vars(namespace)

    import pprint

    pprint.pprint(args)
