import sys

from ssssg.commands import run_ssssg, build_index


if __name__ == "__main__":
    args = sys.argv[1:]

    if args[0] == 'run':
        run_ssssg(args[1])
    elif args[0] == 'index':
        build_index(args[1])
