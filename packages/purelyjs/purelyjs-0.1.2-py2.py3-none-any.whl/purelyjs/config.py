try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

import re


def parse_config(filepath):
    cfg = ConfigParser()
    cfg.read(filepath)

    section_name = 'purelyjs'

    if not cfg.has_section(section_name):
        raise ValueError("No section %s found" % section_name)

    interpreters = []
    libs = []
    tests = []

    # TODO: add warning for unrecognized keys?
    for key, value in cfg.items(section_name):
        if key == 'interpreters':
            interpreters = re.split('\s+', value)
        if key == 'libs':
            libs = re.split('\s+', value)
        elif key == 'tests':
            tests = re.split('\s+', value)

    interpreters = [e for e in interpreters if e]
    libs = [lib for lib in libs if lib]
    tests = [test for test in tests if test]

    return interpreters, libs, tests
