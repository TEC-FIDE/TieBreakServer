"""
convert.py
==========

A brief description of what this module does.

:author: Otto Milvang <sjakk@milvang.no>
:copyright: (c) 2023 Otto Milvang
:license: MIT License
"""

import sys

from commonmain import commonmain


class convert2jch(commonmain):

    def __init__(self):
        super().__init__()
        self.origin = "convert ver. 1.00"
        self.tournamentno = 0

    # read_command_line
    #   options:
    #   -i = input-file
    #   -o = output-file
    #   -f = file-format
    #   -e = tournament-number
    #   -n = number-of-rounds
    #   -g = game-score
    #   -m = match-score
    #   -v = verbose and debug

    def read_command_line(self):
        self.read_common_command_line(True)

    def write_text_file(self, f, result, delimiter):
        pass

    def do_checker(self):
        self.core = None


# run program
jch = convert2jch()
code = jch.common_main()
sys.exit(code)
