import sys

from ssssg.config import options
from ssssg.commands import run_ssssg, build_index


def help_text():
    return """usage: 
    To index the site:
        python ssssg.py index /path/to/site

    To run the site:
        python ssssg.py run site"""


if __name__ == "__main__":
    args = sys.argv[1:]

    options.parse_command_line(sys.argv[2:])

    if len(args) < 2:
        print(help_text())
    elif args[0] == 'run':
        run_ssssg(args[1])
    elif args[0] == 'index':
        build_index(args[1])
    else:
        print(help_text())
