import sys

from ssssg.config import options
from ssssg.main import SSSG


if __name__ == '__main__':
    options.parse_command_line(sys.argv)

    ssssg = SSSG(site_path=options.site_path,
        source_path=options.source_path, template_path=options.template_path)
    ssssg.create_site()

    if options.index_directories:
        ssssg.index_directories()

    ssssg.save()
