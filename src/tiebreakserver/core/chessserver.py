#! C:/Program Files/Python313/python.exe
"""
chessserver.py
==============

A brief description of what this module does.

:author: Otto Milvang <sjakk@milvang.no>
:copyright: (c) 2023 Otto Milvang
:license: MIT License
"""
import sys

from commonmain import commonmain
from tiebreak import tiebreak

"""
==============================
Request:
{
    "filetype": "convert request" | "tiebreak request" ,
    "version": "1.0",
    "origin": "<Free text>",
    "published": "<date on format 2018-08-14 05:07:44>",
    "command": {
        "service" : "convert" | tiebreak,
        "filename" : "<original file name>",
        "filetype": "TRF" | "TS" | < other known format >,
        "content": ["<lines with base 64 encoded file>"],
        "tournamentno": <0 or tournamentno to convert>,
        "number_of_rounds": <int>,
        // parameters for tiebreaks
            "tiebreaks" : [string list],
            "tournamenttype" : "" | "d" | "p" | "s"
        }

    }
}

Response:
{
    "filetype": "convert response" | "tiebreak response",
    "version": "1.0",
    "origin": "chessserver ver. 1.04",
    "published": "2024-10-01 14:32:16",
    "status": {
        "code": 0,
        "error": []
    },
    "convertResult": {
        <Json chess file>
    }
    "tiebreakResult": {
        "check": false,
        "tiebreaks": [ … ],
        "competitors": [ {
            "cid": <cid>,
            "rank": <rank>,
            "tiebreakScore": [ … ],
            "boardPoints": { … },
            "tiebreakDetails": [{ … }, … ]
    }
}


"""


class chessserver(commonmain):

    def __init__(self):
        super().__init__()
        self.origin = "chessserver ver. 1.00"
        self.tournamentno = 0

    def read_command_line(self):
        self.read_common_server(True)

    def write_text_file(self, f, result, delimiter):
        pass

    def do_checker(self):
        params = self.params
        self.core = None
        match (params["service"]):
            case "convert":
                self.core = None
            case "tiebreak":
                # result = None
                if params["check"]:
                    self.filetype = "tiebreak"
                chessfile = self.chessfile
                if chessfile.get_status() == 0:
                    if self.tournamentno > 0:
                        tb = tiebreak(chessfile, self.tournamentno, params["number_of_rounds"], params)
                        tb.compute_tiebreaks(chessfile, self.tournamentno, params)
                    else:
                        tb = tiebreak(chessfile, self.tournamentno, params["number_of_rounds"], params)
                self.core = tb
            case _:
                self.core = None


# run program
jch = chessserver()
code = jch.common_main()
sys.exit(code)
