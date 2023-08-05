#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import site

PYTHON_PATH = sys.executable
PYTHON_EXTRAS_PATH = site._init_pathinfo()


CONFIG_TEMPLATE = """{
    'Python': {
        'python': '%s',
        'pythonExtraPaths': %s
    }
}
"""


class SublimeCodeIntelConfig(object):
    """SublimeCodeIntelConfig"""
    config_path = '.codeintel'
    config_file = '.codeintel/config'
    config_text = ''

    def __init__(self):
        super(SublimeCodeIntelConfig, self).__init__()

    def format_config(self):
        self.config_text = CONFIG_TEMPLATE % (PYTHON_PATH,
                                              str(list(PYTHON_EXTRAS_PATH)))

    def create_file(self):
        self.format_config()
        if not os.path.isdir(self.config_path):
            os.mkdir(self.config_path)
        with open(self.config_file, 'w') as config:
            config.write(self.config_text)
        return os.path.isfile(self.config_file)


def main():
    SublimeCodeIntelConfig().create_file()

if __name__ == '__main__':
    main()
