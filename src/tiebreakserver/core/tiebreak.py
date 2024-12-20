"""
tiebreak.py
===========

A brief description of what this module does.

:author: Otto Milvang <sjakk@milvang.no>
:copyright: (c) 2023 Otto Milvang
:license: MIT License
"""

import math
from decimal import Decimal
from decimal import ROUND_HALF_UP

import rating as rating

"""
Structure

+--- tiebreaks: [  - added in compute-tiebreak
|         {
|             order: priority of tiebreak
|             name: Acronym from regulations
|             point_type: mpoints (match points) game_points (game points) or points
|             modifiers: { low / high / lim / urd / p4f / fmo / rb5 / z4h / vuv }
|         },
|         ...
|
|       ]
+--- is_team: True/False
+--- current_round: Standings after round 'current_round'
+--- rounds: Total number of rounds
+--- rr: RoundRobin (True/False)
+--- score_system: {
|        game: { W:1.0, D:0.5, L:0.0, Z:0.0, P:1.0, A:0.5, U: 0.0 }
|        team: { W:1.0, D:1.0, L:0.0, Z:0.0, P:1.0, A:1.0, U: 0.0 }
|                 }
+--- players/teams:  {
|              1: {
|                    cid: start_no
|                    rating: rating
|                    kfactor: k
|                    rating: rating
|                    rrst: {  - results, games for players, matches for teams
|                        1: {  - round
|                              points - points for game / match
|                              rpoints - for games, points with score system 1.0 / 0.5 / 0.0
|                              color - w / b
|                              played  - boolean
|                              rated - boolean
|                              opponent - id of opponent
|                              opprating - rating of opponent
|                              deltaR - for rating change
|                            }
|                        2: {  - round 2 }
|                           ...
|                           }
|                   tb_val: {  - intermediate results from tb calculations }
|     ---- output for each player / team
|                   score: [ array of tie-breaks values, same order and length as 'tiebreaks'
|                   rank: final rank of player / team
|                 },
|              2: { ... },
|                  ...
|         }
+--- rank_order: [ array of rank_order,  players/teams ]
|

"""


class tiebreak:

    # constructor function
    def __init__(self, chessevent, tournamentno, current_round, params):
        event = chessevent.event
        tournament = chessevent.get_tournament(tournamentno)
        self.tiebreaks = []
        if tournament is None:
            return
        self.is_team = self.is_team = tournament["teamTournament"] if "teamTournament" in tournament else False
        chessevent.update_tournament_random(tournament, self.is_team)
        self.rounds = tournament["numRounds"]
        self.current_round = current_round if current_round >= 0 else self.rounds
        self.get_score = chessevent.get_score
        self.is_vur = chessevent.is_vur
        self.max_board = 0
        self.lastplayedround = 0
        self.primaryscore = None  # use default
        self.acceleration = tournament["acceleration"] if "acceleration" in tournament else None

        self.scoreLists = chessevent.scoreLists
        for score_system in event["scoreLists"]:
            self.scoreLists[score_system["listName"]] = score_system["score_system"]
        if self.is_team:
            self.matchscore = tournament["matchScoreSystem"]
            self.game_score = tournament["gameScoreSystem"]
            [self.cplayers, self.cteam] = chessevent.build_tournament_teamcompetitors(tournament)
            self.allgames = chessevent.build_all_games(tournament, self.cteam, False)
            self.teams = self.prepare_competitors(tournament, "match")
            self.compute_score(self.teams, "mpoints", self.matchscore, self.current_round)
            self.compute_score(self.teams, "game_points", self.game_score, self.current_round)
        else:
            self.matchscore = tournament["gameScoreSystem"]
            self.game_score = tournament["gameScoreSystem"]
            self.players = self.prepare_competitors(tournament, "game")
            self.compute_score(self.players, "points", self.game_score, self.current_round)
        self.cmps = self.teams if self.is_team else self.players
        numcomp = len(self.cmps)
        self.rank_order = list(self.cmps.values())

        # find the tournament type
        tt = tournament["tournamentType"].upper()
        # self.teamsize = round(len(tournament['playerSection']['results'])/ len(tournament['teamSection']['results']
        # )) if self.is_team else 1
        self.teamsize = tournament["teamSize"] if "teamSize" in tournament else 1
        self.rr = params["is_rr"] if params is not None and "is_rr" in params else False
        if self.rr is None:
            if tt.find("SWISS") >= 0:
                self.rr = False
            elif tt.find("RR") >= 0 or tt.find("ROBIN") >= 0 or tt.find("BERGER") >= 0:
                self.rr = True
            elif numcomp == self.rounds + 1 or numcomp == self.rounds:
                self.rr = True
            elif numcomp == (self.rounds + 1) * 2 or numcomp == self.rounds * 2:
                self.rr = True
        self.unrated = int(params["unrated"]) if params is not None and "unrated" in params else 0

    """
    compute_tiebreaks(self, chessfile, tournamentno, params)
    chessfile - Chessfile structure
    tournamentno - which tournament to calculate
    params - Parameters from core
    """

    def compute_tiebreaks(self, chessfile, tournamentno, params):
        # run tiebreak
        # json.dump(chessfile.__dict__, sys.stdout, indent=2)

        if chessfile.get_status() == 0:
            tblist = params["tie_break"]
            for pos in range(0, len(tblist)):
                mytb = self.parse_tiebreak(pos + 1, tblist[pos])
                self.compute_tiebreak(mytb)
        if chessfile.get_status() == 0:
            tm = chessfile.get_tournament(tournamentno)
            tm["rank_order"] = self.tiebreaks
            jsoncmps = tm["competitors"]
            correct = True
            competitors = []
            for cmp in jsoncmps:
                competitor = {}
                competitor["cid"] = start_no = cmp["cid"]
                correct = correct and cmp["rank"] == self.cmps[start_no]["rank"]
                competitor["rank"] = cmp["rank"] = self.cmps[start_no]["rank"]
                if self.is_team:
                    competitor["boardPoints"] = self.cmps[start_no]["tb_val"]["gpoints_" + "bp"]
                competitor["tiebreakDetails"] = self.cmps[start_no]["tiebreakDetails"]
                competitor["tiebreakScore"] = cmp["tiebreakScore"] = self.cmps[start_no]["tiebreakScore"]
                competitors.append(competitor)
            chessfile.result = {"check": correct, "tiebreaks": self.tiebreaks, "competitors": competitors}

    def prepare_competitors(self, tournament, scoretype):
        rounds = self.current_round
        # for rst in competition['results']:
        #    rounds = max(rounds, rst['round'])
        # self.rounds = rounds
        ptype = "mpoints" if self.is_team else "points"
        # score_system = self.score_system['match']
        # Fill competition structure, replaze unplayed games with played=Fales, points=0.0
        cmps = {}
        for competitor in tournament["competitors"]:
            rnd = competitor["random"] if "random" in competitor else 0
            cmp = {
                "cid": competitor["cid"],
                "rsts": {},
                "orgrank": competitor["rank"] if "rank" in competitor else 0,
                "rank": 1,
                "rating": (competitor["rating"] if "rating" in competitor else 0),
                "present": competitor["present"] if "present" in competitor else True,
                "tiebreakScore": [],
                "tiebreakDetails": [],
                "rnd": rnd,
                "tb_val": {},
            }
            # Be sure that missing results are replaced by zero
            zero = self.scoreLists[scoretype]["Z"]
            for rnd in range(1, rounds + 1):
                cmp["rsts"][rnd] = {
                    ptype: zero,
                    "rpoints": zero,
                    "color": "w",
                    "played": False,
                    "vur": True,
                    "rated": False,
                    "opponent": 0,
                    "opprating": 0,
                    "board": 0,
                    "deltaR": 0,
                }
            cmps[competitor["cid"]] = cmp
        for rst in tournament[scoretype + "List"]:
            if rst["round"] <= self.current_round or True:
                self.prepare_result(cmps, rst, self.matchscore)
                if self.is_team:
                    self.prepare_teamgames(cmps, rst, self.game_score)

        # helpers.json_output('c:\\temp\\mc01.txt', cmps)

        return cmps

    def prepare_result(self, cmps, rst, score_system):
        ptype = "mpoints" if self.is_team else "points"
        rnd = rst["round"]
        white = rst["white"]
        wPoints = self.get_score(score_system, rst, "white")
        wrPoints = self.get_score("rating", rst, "white")
        wVur = self.is_vur(rst, "white")
        wrating = 0
        brating = 0
        expscore = None
        if "black" in rst:
            black = rst["black"]
        else:
            black = 0
        if black > 0:
            if "bResult" not in rst:
                rst["bResult"] = self.scoreLists["_reverse"][rst["wResult"]]
            bPoints = self.get_score(score_system, rst, "black")
            brPoints = self.get_score("rating", rst, "black")
            bVur = self.is_vur(rst, "black")
            if rst["played"]:
                if "rating" in cmps[white] and cmps[white]["rating"] > 0:
                    wrating = cmps[white]["rating"]
                if "rating" in cmps[black] and cmps[black]["rating"] > 0:
                    brating = cmps[black]["rating"]
                expscore = rating.ComputeExpectedScore(wrating, brating)
        board = rst["board"] if "board" in rst else 0
        if white > 0:
            cmps[white]["rsts"][rnd] = {
                ptype: wPoints,
                "rpoints": wrPoints,
                "color": "w",
                "played": rst["played"],
                "vur": wVur,
                "rated": rst["rated"] if "rated" in rst else (rst["played"] and black > 0),
                "opponent": black,
                "opprating": brating,
                "board": board,
                "deltaR": (rating.ComputeDeltaR(expscore, wrPoints) if expscore is not None else None),
            }
        if black > 0:
            self.lastplayedround = max(self.lastplayedround, rnd)
            cmps[black]["rsts"][rnd] = {
                ptype: bPoints,
                "rpoints": brPoints,
                "color": "b",
                "played": rst["played"],
                "vur": bVur,
                "rated": rst["rated"] if "rated" in rst else (rst["played"] and white > 0),
                "opponent": white,
                "opprating": wrating,
                "board": board,
                "deltaR": (rating.ComputeDeltaR(Decimal(1.0) - expscore, brPoints) if expscore is not None else None),
            }
        return

    def prepare_teamgames(self, cmps, rst, score_system):
        max_board = 0
        rnd = rst["round"]
        for col in ["white", "black"]:
            if col in rst and rst[col] > 0:
                game_points = 0
                competitor = rst[col]
                games = []
                for game in self.allgames[rnd][competitor]:
                    white = game["white"]
                    black = game["black"] if "black" in game else 0
                    board = game["board"] if "board" in game else 0
                    max_board = max(max_board, board)
                    # print(rnd, white, black)
                    wVur = self.is_vur(game, "white")
                    if self.cteam[white] == competitor and board > 0:
                        points = self.get_score(self.game_score, game, "white")
                        game_points += points
                        games.append(
                            {
                                "points": points,
                                "rpoints": self.get_score("rating", game, "white"),
                                "color": "w",
                                "vur": wVur,
                                "played": game["played"],
                                "rated": game["rated"] if "rated" in rst else (game["played"] and black > 0),
                                "player": white,
                                "opponent": black,
                                "board": board,
                            }
                        )
                    if black > 0 and board > 0 and self.cteam[black] == competitor:
                        points = self.get_score(self.game_score, game, "black")
                        bVur = self.is_vur(game, "black")
                        game_points += points
                        games.append(
                            {
                                "points": points,
                                "rpoints": self.get_score("rating", game, "black"),
                                "color": "b",
                                "vur": bVur,
                                "played": game["played"],
                                "rated": game["rated"] if "rated" in rst else (game["played"] and black > 0),
                                "player": black,
                                "opponent": white,
                                "board": board,
                            }
                        )
                cmps[competitor]["rsts"][rnd]["game_points"] = game_points
                cmps[competitor]["rsts"][rnd]["games"] = games
        self.max_board = max(self.max_board, max_board)
        # print('self.max', self.max_board)

    def addtbval(self, obj, rnd, val):
        if rnd in obj:
            if isinstance(val, str):
                obj[rnd] = obj[rnd] + val
            else:
                obj[rnd] = obj[rnd] + val
        else:
            obj[rnd] = val

    def compute_score(self, cmps, point_type, scoretype, norounds):
        # score_system = self.score_system[scoretype]
        prefix = point_type + "_"
        other = {"w": "b", "b": "w", " ": " "}
        for start_no, cmp in cmps.items():
            tbscore = cmp["tb_val"]
            tbscore[prefix + "sno"] = {"val": start_no}
            tbscore[prefix + "rank"] = {"val": cmp["orgrank"]}
            tbscore[prefix + "rnd"] = {"val": cmp["rnd"]}
            tbscore[prefix + "cnt"] = {"val": 0}  # count the number of elements (why)
            tbscore[prefix + "points"] = {"val": Decimal("0.0")}  # total points
            tbscore[prefix + "win"] = {"val": 0}  # number of wins (played and unplayed)
            tbscore[prefix + "won"] = {"val": 0}  # number of won games over the board
            tbscore[prefix + "bpg"] = {"val": 0}  # number of black games played
            tbscore[prefix + "bwg"] = {"val": 0}  # number of games won with black
            tbscore[prefix + "ge"] = {"val": 0}  # number of games played + PAB
            tbscore[prefix + "rep"] = {"val": 0}  # number of rounds elected to play (same as GE)
            tbscore[prefix + "vur"] = {"val": 0}  # number of vurs (check algorithm)
            tbscore[prefix + "cop"] = {"val": "  "}  # color preference (for pairing)
            tbscore[prefix + "cod"] = {"val": 0}  # color difference (for pairing)
            tbscore[prefix + "csq"] = {"val": ""}  # color sequence (for pairing)
            tbscore[prefix + "num"] = {"val": 0}  # number of games played (for pairing)
            tbscore[prefix + "lp"] = 0  # the last round played
            tbscore[prefix + "lo"] = 0  # last round without vur
            tbscore[prefix + "lp"] = 0  # last round paired
            tbscore[prefix + "pfp"] = 0  # points from played games
            tbscore[prefix + "lg"] = 0  # self.scoreLists[scoretype]['D'] # Result of last game
            tbscore[prefix + "bp"] = {}  # Boardpoints
            # if start_no == 1:
            #    helpers.json_output("c:\\temp\\new_trx_cmp_" + point_type + '.json', cmp['rsts'])
            # cmpr = sorted(cmp, key=lambda p: (p['rank'], p['tb_val'][prefix + name]['val'], p['cid']))
            # for rnd, rst in cmp['rsts'].items():
            # print(rnd, cmp['rsts'])
            #    if rnd <= norounds:
            pcol = " "  # Previous color
            csq = ""
            for rnd in range(1, norounds + 1):
                if rnd in cmp["rsts"]:
                    rst = cmp["rsts"][rnd]
                    # total score
                    points = rst[point_type] if point_type in rst else 0
                    tbscore[prefix + "points"][rnd] = points
                    tbscore[prefix + "points"]["val"] += points

                    # number of games
                    if self.is_team and scoretype == "game":
                        gamelist = rst["games"] if "games" in rst else []
                    else:
                        gamelist = [rst]
                    #                    if start_no == 1:
                    #                        print(point_type, gamelist)
                    for game in gamelist:
                        # print(game)
                        if self.is_team and scoretype == "game":
                            points = game["points"]
                            if game["played"] and game["opponent"] <= 0:  # PAB
                                points = self.scoreLists[self.game_score]["W"]
                            board = game["board"]
                            tbscore[prefix + "bp"][board] = (
                                tbscore[prefix + "bp"][board] + points if board in tbscore[prefix + "bp"] else points
                            )
                            # tbscore[prefix + 'bp']['val'] += tbscore[prefix + 'bp'][board]

                        self.addtbval(tbscore[prefix + "cnt"], rnd, 1)
                        self.addtbval(tbscore[prefix + "cnt"], "val", 1)

                        # result in the last game
                        if rnd == self.rounds and game["opponent"] > 0:
                            tbscore[prefix + "lg"] += points
                            # if start_no == 1:
                            #    print(point_type, points, tbscore[prefix + 'lg'])

                        # points from played games
                        if game["played"]:
                            self.addtbval(tbscore[prefix + "num"], rnd, game["opponent"])
                            if game["opponent"] > 0:
                                self.addtbval(tbscore[prefix + "num"], "val", 1)
                                tbscore[prefix + "pfp"] += points
                                ocol = ncol = game["color"]
                                pf = 1 if ocol == "w" else -1
                                self.addtbval(tbscore[prefix + "cod"], rnd, pf)
                                self.addtbval(tbscore[prefix + "cod"], "val", pf)
                                pf = tbscore[prefix + "cod"]["val"]
                                ncol = (other[ocol] + "bbbbwwww")[pf]
                                ncol += str(abs(pf)) if ocol != pcol else "2"
                                # if ocod > -2 and ocod < 2:
                                #    ncol = 'w' if ocol == 'b' else 'b'
                                #    ncol = ncol.upper() if ncol.upper() == tbscore[prefix + 'cop']['val'].upper()
                                #    else ncol

                                csq += ocol
                                pcol = ocol
                                self.addtbval(tbscore[prefix + "csq"], rnd, ocol)
                                self.addtbval(tbscore[prefix + "csq"], "val", ocol)

                                self.addtbval(tbscore[prefix + "cop"], rnd, ncol)
                                tbscore[prefix + "cop"]["val"] = ncol

                            # last played game (or PAB)
                            if rnd > tbscore[prefix + "lp"]:
                                tbscore[prefix + "lp"] = rnd
                        elif "points" in game and game["points"] == self.scoreLists[scoretype]["W"]:
                            self.addtbval(tbscore[prefix + "num"], rnd, 0)

                        # number of wins
                        win = 1 if points == self.scoreLists[scoretype]["W"] else 0
                        self.addtbval(tbscore[prefix + "win"], rnd, win)
                        self.addtbval(tbscore[prefix + "win"], "val", win)

                        # number of wins played over the board
                        won = (
                            1
                            if points == self.scoreLists[scoretype]["W"] and game["played"] and game["opponent"] > 0
                            else 0
                        )
                        self.addtbval(tbscore[prefix + "won"], rnd, won)
                        self.addtbval(tbscore[prefix + "won"], "val", won)

                        # number of games played with black
                        bpg = 1 if game["color"] == "b" and game["played"] else 0
                        self.addtbval(tbscore[prefix + "bpg"], rnd, bpg)
                        self.addtbval(tbscore[prefix + "bpg"], "val", bpg)

                        # number of wins played with black
                        bwg = (
                            1
                            if game["color"] == "b" and game["played"] and points == self.scoreLists[scoretype]["W"]
                            else 0
                        )
                        self.addtbval(tbscore[prefix + "bwg"], rnd, bwg)
                        self.addtbval(tbscore[prefix + "bwg"], "val", bwg)

                        # number of games elected to play
                        # ge = 1 if game['played'] or (game['opponent'] > 0 and points == self.scoreLists[scoretype][
                        # 'W']) else 0
                        ge = 1 if game["played"] or (points == self.scoreLists[scoretype]["W"]) else 0
                        self.addtbval(tbscore[prefix + "ge"], rnd, ge)
                        self.addtbval(tbscore[prefix + "ge"], "val", ge)
                        self.addtbval(tbscore[prefix + "rep"], rnd, ge)
                        self.addtbval(tbscore[prefix + "rep"], "val", ge)

                        vur = 1 if game["vur"] else 0
                        self.addtbval(tbscore[prefix + "vur"], rnd, vur)
                        self.addtbval(tbscore[prefix + "vur"], "val", vur)

                        # last round with opponent, pab or fpb (16.2.1, 16.2.2, 16.2.3 and 16.2.4)
                        if rnd > tbscore[prefix + "lo"] and (vur == 0):
                            tbscore[prefix + "lo"] = rnd
                        if rnd > tbscore[prefix + "lp"] and (game["opponent"] > 0):
                            tbscore[prefix + "lp"] = rnd

    def compute_recursive_if_tied(self, tb, cmps, rounds, compute_singlerun):
        (points, scoretype, prefix) = self.get_scoreinfo(tb, True)
        name = tb["name"].lower()
        ro = self.rank_order
        for player in ro:
            player["tb_val"][prefix + name] = {}
            player["tb_val"][prefix + name]["val"] = player["rank"]  # rank value initial value = rank
            player["tb_val"]["moreloops"] = True  # As long as True, we have more to check
        loopcount = 0
        moretodo = compute_singlerun(tb, cmps, rounds, ro, loopcount)
        while moretodo:
            moretodo = False
            loopcount += 1
            start = 0
            while start < len(ro):
                currentrank = ro[start]["tb_val"][prefix + name]["val"]
                for stop in range(start + 1, len(ro) + 1):
                    if stop == len(ro) or currentrank != ro[stop]["tb_val"][prefix + name]["val"]:
                        break
                # we have a range start .. stop-1 to check for top board result
                # print("start-stop", start, stop)
                if ro[start]["tb_val"]["moreloops"]:
                    if stop - start == 1:
                        moreloops = False
                        ro[start]["tb_val"]["moreloops"] = moreloops
                    else:
                        subro = ro[start:stop]  # subarray of rank_order
                        moreloops = compute_singlerun(tb, cmps, rounds, subro, loopcount)
                        for player in subro:
                            player["tb_val"]["moreloops"] = moreloops  # 'de' rank value initial value = rank
                        moretodo = moretodo or moreloops
                start = stop
            # json.dump(ro, sys.stdout, indent=2)
            moreloops = compute_singlerun(tb, cmps, rounds, [], loopcount)
            moretodo = moretodo or moreloops
            ro = sorted(ro, key=lambda p: (p["rank"], p["tb_val"][prefix + name]["val"], p["cid"]))
        # print('L=' + str(loopcount))
        # reorder 'tb'
        start = 0
        while start < len(ro):
            currentrank = ro[start]["rank"]
            for stop in range(start, len(ro) + 1):
                if stop == len(ro) or currentrank != ro[stop]["rank"]:
                    break
                # we have a range start .. stop-1 to check for direct encounter
            offset = ro[start]["tb_val"][prefix + name]["val"]
            if ro[start]["tb_val"][prefix + name]["val"] != ro[stop - 1]["tb_val"][prefix + name]["val"]:
                offset -= 1
            for p in range(start, stop):
                ro[p]["tb_val"][prefix + name]["val"] -= offset
            start = stop
        return name

    def compute_basic_direct_encounter(self, tb, cmps, rounds, subro, loopcount, points, scoretype, prefix):
        name = tb["name"].lower()
        (xpoints, xscoretype, prefix) = self.get_scoreinfo(tb, True)
        changes = 0
        rpos = loopcount - tb["modifiers"]["swap"]  # Report pos
        postfix = " " + scoretype[0] if tb["name"] == "EDGE" else ""
        currentrank = subro[0]["tb_val"][prefix + name]["val"]
        metall = True  # Met all opponents on same range
        metmax = len(subro) - 1  # Max number of opponents
        for player in range(0, len(subro)):
            de = subro[player]["tb_val"]
            de["denum"] = 0  # number of opponents
            de["deval"] = 0  # sum score against of opponens
            de["demax"] = 0  # sum score against of opponens, unplayed = win
            de["delist"] = {}  # list of results numgames, score, maxscore
            for rnd, rst in subro[player]["rsts"].items():
                if rnd <= rounds:
                    opponent = rst["opponent"]
                    if opponent > 0:
                        played = True if tb["modifiers"]["p4f"] else rst["played"]
                        if played and cmps[opponent]["tb_val"][prefix + name]["val"] == currentrank:
                            # 6.1.2 compute average score
                            if opponent in de["delist"]:
                                score = de["delist"][opponent]["score"]
                                num = de["delist"][opponent]["cnt"]
                                sumscore = score * num
                                de["deval"] -= score
                                num += 1
                                sumscore += rst[points]
                                score = sumscore / num
                                de["denum"] = 1
                                de["deval"] += score
                                de["delist"][opponent]["cnt"] = 1
                                de["delist"][opponent]["score"] = score
                            else:
                                de["denum"] += 1
                                de["deval"] += rst[points]
                                de["delist"][opponent] = {"cnt": 1, "score": rst[points]}
            # if not tb['modifiers']['p4f'] and de['denum'] < metmax:
            # if (not tb['modifiers']['p4f'] and de['denum'] < metmax) or tb['modifiers']['sws']:
            if (not self.rr and de["denum"] < metmax) or tb["modifiers"]["sws"]:
                metall = False
                de["demax"] = de["deval"] + (metmax - de["denum"]) * self.scoreLists[scoretype]["W"] * (
                    self.teamsize if points == "game_points" else 1
                )
                # print('F', metmax, de['deval'], de['demax'], de['denum'])
            else:
                de["demax"] = de["deval"]
                # print('T', metmax, de['deval'], de['demax'], de['denum'])
        if metall:  # 6.2 All players have met
            # print("T")
            subro = sorted(subro, key=lambda p: (-p["tb_val"]["deval"], p["cid"]))
            crank = rank = subro[0]["tb_val"][prefix + name]["val"]
            val = subro[0]["tb_val"]["deval"]
            sprefix = "\t" if rpos in subro[0]["tb_val"][prefix + name] else ""
            self.addtbval(subro[0]["tb_val"][prefix + name], rpos, sprefix + str(val) + postfix)
            for i in range(1, len(subro)):
                rank += 1
                de = subro[i]["tb_val"]
                if val != de["deval"]:
                    crank = de[prefix + name]["val"] = rank
                    val = de["deval"]
                    changes += 1
                else:
                    de[prefix + name]["val"] = crank
                sprefix = "\t" if rpos in de[prefix + name] else ""
                self.addtbval(de[prefix + name], rpos, sprefix + str(val) + postfix)
        else:  # 6.2 swiss tournament
            # print("F")
            subro = sorted(subro, key=lambda p: (-p["tb_val"]["deval"], -p["tb_val"]["demax"], p["cid"]))
            crank = rank = subro[0]["tb_val"][prefix + name]["val"]
            val = subro[0]["tb_val"]["deval"]
            maxval = subro[0]["tb_val"]["demax"]
            sprefix = "\t" if rpos in subro[0]["tb_val"][prefix + name] else ""
            self.addtbval(subro[0]["tb_val"][prefix + name], rpos, sprefix + str(val) + "/" + str(maxval) + postfix)
            unique = True
            for i in range(1, len(subro)):
                rank += 1
                tbmax = max(subro[i:], key=lambda tb_val: tb_val["tb_val"]["demax"])
                de = subro[i]["tb_val"]
                if unique and val > tbmax["tb_val"]["demax"]:
                    crank = de[prefix + name]["val"] = rank
                    val = de["deval"]
                    maxval = de["demax"]
                    changes += 1
                else:
                    val = de["deval"]
                    maxval = de["demax"]
                    de[prefix + name]["val"] = crank
                    unique = False
                sprefix = "\t" if rpos in de[prefix + name] else ""
                self.addtbval(de[prefix + name], rpos, sprefix + str(val) + "/" + str(maxval) + postfix)
                # self.addtbval(de[prefix + name], rpos,  str(val) + '/' + str(maxval) + postfix)
        # print(loopcount, scoretype, changes)
        return changes

    def compute_singlerun_direct_encounter(self, tb, cmps, rounds, subro, loopcount):
        (points, scoretype, prefix) = self.get_scoreinfo(tb, True)
        tb["modifiers"]["swap"] = 0
        changes = 1 if loopcount == 0 else 0
        if loopcount > 0 and len(subro) > 0:
            changes = self.compute_basic_direct_encounter(tb, cmps, rounds, subro, loopcount, points, scoretype, prefix)
        return changes

    def compute_singlerun_ext_direct_encounter(self, tb, cmps, rounds, subro, loopcount):
        # name = tb["name"].lower()
        (points, scoretype, prefix) = self.get_scoreinfo(tb, loopcount == 0 or tb["modifiers"]["primary"])
        changes = 0
        if loopcount == 0:
            tb["modifiers"]["primary"] = True
            tb["modifiers"]["points"] = points
            (spoints, secondary, sprefix) = self.get_scoreinfo(tb, False)
            tb["modifiers"]["loopcount"] = 0
            tb["modifiers"]["edechanges"] = {scoretype: 0, secondary: 1}
            tb["modifiers"]["swap"] = 0
            return True
        if tb["modifiers"]["loopcount"] != loopcount:
            # print(scoretype)
            tb["modifiers"]["loopcount"] = loopcount
            tb["modifiers"]["changes"] = 0
        if len(subro) == 0:
            if tb["modifiers"]["changes"] == 0:
                tb["modifiers"]["primary"] = not tb["modifiers"]["primary"]
                tb["modifiers"]["edechanges"][scoretype] = 0
                tb["modifiers"]["swap"] += 1
                ro = self.rank_order
                for player in ro:
                    player["tb_val"]["moreloops"] = True  # 'de' rank value initial value = rank
            else:
                (spoints, secondary, sprefix) = self.get_scoreinfo(tb, not tb["modifiers"]["primary"])
                tb["modifiers"]["edechanges"][secondary] = 1
            retsum = tb["modifiers"]["edechanges"]["match"] + tb["modifiers"]["edechanges"]["game"]
            # print('E', loopcount, tb['modifiers']['changes'], retsum, tb['modifiers']['edechanges'])
            return retsum > 0 and loopcount < 30
        changes = self.compute_basic_direct_encounter(tb, cmps, rounds, subro, loopcount, points, scoretype, prefix)
        tb["modifiers"]["changes"] += changes
        # print(loopcount, tb['modifiers']['scoretype'], tb['modifiers']['edechanges'], changes)
        # print(len(subro),loopcount, changes, tb['modifiers']['edechanges'], scoretype)
        return changes > 0 and loopcount < 30

    def compute_progressive_score(self, tb, cmps, rounds):
        (points, scoretype, prefix) = self.get_scoreinfo(tb, True)
        low = tb["modifiers"]["low"]
        for start_no, cmp in cmps.items():
            tbscore = cmp["tb_val"]
            ps = 0
            ssf = 0  # Sum so far
            tbscore[prefix + "ps"] = {"val": ps, "cut": []}
            for rnd in range(1, rounds + 1):
                p = cmp["rsts"][rnd][points] if rnd in cmp["rsts"] and points in cmp["rsts"][rnd] else Decimal("0.0")
                ssf += p
                # p = p * (rounds+1-rnd)
                tbscore[prefix + "ps"][rnd] = ssf
                if rnd <= low:
                    tbscore[prefix + "ps"]["cut"].append(rnd)
                else:
                    ps += ssf
            tbscore[prefix + "ps"]["val"] = ps
        return "ps"

    def compute_koya(self, tb, cmps, rounds):
        (points, scoretype, prefix) = self.get_scoreinfo(tb, True)
        plim = tb["modifiers"]["plim"]
        nlim = tb["modifiers"]["nlim"]
        lim = (
            plim
            * self.scoreLists[scoretype]["W"]
            * rounds
            * (self.teamsize if points == "game_points" else 1)
            / Decimal("100.0")
            + nlim
        )
        # print(lim)
        for start_no, cmp in cmps.items():
            tbscore = cmp["tb_val"]
            ks = 0
            tbscore[prefix + "ks"] = {"val": ks, "cut": []}
            for rnd, rst in cmp["rsts"].items():
                if rnd <= rounds:
                    opponent = rst["opponent"]
                    if opponent > 0:
                        oppscore = cmps[opponent]["tb_val"][prefix + "points"]["val"]
                        ownscore = cmp["tb_val"][prefix + "points"][rnd]
                        tbscore[prefix + "ks"][rnd] = ownscore
                        if oppscore >= lim:
                            ks += ownscore
                        else:
                            tbscore[prefix + "ks"]["cut"].append(rnd)
            tbscore[prefix + "ks"]["val"] = ks
        return "ks"

    def compute_buchholz_sonneborn_berger(self, tb, cmps, rounds):
        name = tb["name"].lower()
        isfb = name == "fb" or name == "afb" or tb["modifiers"]["fmo"]
        (opoints, oscoretype, oprefix) = self.get_scoreinfo(tb, True)
        (spoints, sscoretype, sprefix) = self.get_scoreinfo(tb, name == "sb")
        opointsfordraw = self.scoreLists[oscoretype]["D"] * (self.teamsize if opoints == "game_points" else 1)
        spointsfordraw = self.scoreLists[sscoretype]["D"] * (self.teamsize if spoints == "game_points" else 1)
        # print(opointsfordraw, spointsfordraw)
        name = tb["name"].lower()
        if name == "aob":
            name = "bh"
        is_sb = name == "sb" or name == "esb" or (len(name) == 5 and name[0] == "e" and name[3:5] == "sb")
        if name == "esb" or (len(name) == 5 and name[0] == "e" and name[3:5] == "sb"):
            (spoints, sscoretype, sprefix) = self.get_scoreinfo(tb, False)
        for start_no, cmp in cmps.items():
            tbscore = cmp["tb_val"]
            tbscore[oprefix + "abh"] = {"val": 0}  # Adjusted score for BH (check algorithm)
            # 16.3.2 Unplayed rounds of category 16.2.5 are evaluated as draws.
            adjfore = isfb and tbscore[oprefix + "lp"] == self.rounds  # do we need to adjust for Fore?
            for rnd, rst in cmp["rsts"].items():
                if rnd <= rounds:
                    points_no_opp = Decimal(0.0) if self.rr else opointsfordraw
                    tb_val = (
                        rst[opoints]
                        if rnd <= tbscore[oprefix + "lo"] or adjfore or rst["opponent"] > 0
                        else points_no_opp
                    )
                    tbscore[oprefix + "abh"][rnd] = tb_val
                    tbscore[oprefix + "abh"]["val"] += tb_val
            fbscore = tbscore[oprefix + "points"]["val"]
            # print(start_no, isfb, rst['opponent'], tbscore[oprefix + 'lo'],tbscore[oprefix + 'lp'], self.rounds)
            if adjfore:
                # print(start_no, tbscore[oprefix + 'abh']['val'], tbscore[oprefix + 'abh']['val'] - tbscore[oprefix +
                # 'lg'] + opointsfordraw)
                adjust = opointsfordraw - tbscore[oprefix + "lg"]
                # print(tbscore[oprefix + 'lg'])
                tbscore[oprefix + "abh"][self.rounds] += adjust
                tbscore[oprefix + "abh"]["val"] += adjust
                fbscore += adjust
            tbscore[oprefix + "ownscore"] = fbscore
        if name == "abh" or name == "afb":
            return "abh"

        for start_no, cmp in cmps.items():
            tbscore = cmp["tb_val"]
            bhvalue = []
            for rnd, rst in cmp["rsts"].items():
                if rnd <= rounds:
                    opponent = rst["opponent"]
                    vur = rst["vur"]
                    played = True if tb["modifiers"]["p4f"] or (isfb and rnd == self.rounds) else rst["played"]
                    if played and opponent > 0:
                        vur = False
                        score = cmps[opponent]["tb_val"][oprefix + "abh"]["val"]
                        # if start_no == 2:
                        #    print(start_no, rnd, isfbandlastround)
                    elif not self.rr:
                        score = cmps[start_no]["tb_val"][oprefix + "ownscore"]
                        #       cmps[start_no]['tb_val'][oprefix + 'points']['val']
                    else:
                        score = 0
                    # print(start_no, rnd, opponent,played, vur, score)
                    if tb["modifiers"]["urd"] and not self.rr:
                        sres = spointsfordraw
                    else:
                        sres = rst[spoints] if spoints in rst else Decimal("0.0")
                    tbvalue = score * sres if is_sb else score
                    # if opponent > 0 or not tb['modifiers']['p4f'] :
                    if opponent > 0 or not self.rr:
                        bhvalue.append({"vur": vur, "tbvalue": tbvalue, "score": score, "rnd": rnd})
            tbscore = cmp["tb_val"]
            tbscore[oprefix + name] = {"val": 0, "cut": []}
            for game in bhvalue:
                self.addtbval(tbscore[oprefix + name], game["rnd"], game["tbvalue"])

            low = tb["modifiers"]["low"]
            if low > rounds:
                low = rounds
            high = tb["modifiers"]["high"]
            if low + high > rounds:
                high = rounds - low
            while low > 0:
                sortall = sorted(bhvalue, key=lambda game: (game["score"], game["tbvalue"]))
                sortexp = sorted(bhvalue, key=lambda game: (-game["vur"], game["score"], game["tbvalue"]))
                if tb["modifiers"]["vun"] or sortall[0]["tbvalue"] > sortexp[0]["tbvalue"]:
                    bhvalue = sortall[1:]
                    tbscore[oprefix + name]["cut"].append(sortall[0]["rnd"])
                    # print(start_no, low, 'ALL', sortall[0]['rnd'], sortexp[0]['rnd'])
                else:
                    bhvalue = sortexp[1:]
                    tbscore[oprefix + name]["cut"].append(sortexp[0]["rnd"])
                    # print(start_no, low, 'VUR', sortexp[0]['rnd'], sortexp[0]['rnd'])
                low -= 1

            while high > 0:
                sortall = sorted(bhvalue, key=lambda game: (-game["score"], -game["tbvalue"]))
                # sortexp = sorted(bhvalue, key=lambda game: (-game['vur'], -game['score'], -game['tbvalue'])) // No
                # exception on high
                sortexp = sorted(bhvalue, key=lambda game: (-game["score"], -game["tbvalue"]))
                if tb["modifiers"]["vun"]:
                    bhvalue = sortall[1:]
                    tbscore[oprefix + name]["cut"].append(sortall[0]["rnd"])
                else:
                    bhvalue = sortexp[1:]
                    tbscore[oprefix + name]["cut"].append(sortexp[0]["rnd"])
                high -= 1

            #            if high > 0:
            #                if tb['modifiers']['vun']:
            #                    bhvalue = sorted(bhvalue, key=lambda game: (-game['score'], -game['tbvalue']))[high:]
            #                else:
            #                    bhvalue = sorted(bhvalue, key=lambda game: (game['played'], -game['score'],
            #                    -game['tbvalue']))[high:]

            for game in bhvalue:
                self.addtbval(tbscore[oprefix + name], "val", game["tbvalue"])
        return name

    def compute_ratingperformance(self, tb, cmps, rounds):
        (points, scoretype, prefix) = self.get_scoreinfo(tb, True)
        name = tb["name"].lower()
        for start_no, cmp in cmps.items():
            tbscore = cmp["tb_val"]
            tbscore[prefix + "aro"] = {"val": 0, "cut": []}
            tbscore[prefix + "tpr"] = {"val": 0, "cut": []}
            tbscore[prefix + "ptp"] = {"val": 0, "cut": []}
            ratingopp = []
            trounds = 0
            for rnd, rst in cmp["rsts"].items():
                if rnd <= rounds and rst["played"] and rst["opponent"] > 0:
                    trounds += 1
                    if rst["opprating"] > 0 or tb["modifiers"]["unr"] > 0:
                        rst["rnd"] = rnd
                        rst["adjrating"] = rtng = rst["opprating"] if rst["opprating"] > 0 else tb["modifiers"]["unr"]
                        ratingopp.append(rst)
                        self.addtbval(cmp["tb_val"][prefix + "aro"], rnd, rtng)
                        self.addtbval(cmp["tb_val"][prefix + "tpr"], rnd, rtng)
                        self.addtbval(cmp["tb_val"][prefix + "ptp"], rnd, rtng)
            # trounds = rounds // This is correct only if unplayed gmes are cut.
            low = tb["modifiers"]["low"]
            if low > rounds:
                low = rounds
            high = tb["modifiers"]["high"]
            if low + high > rounds:
                high = rounds - low
            while low > 0:
                if trounds == len(ratingopp):
                    newopp = sorted(ratingopp, key=lambda p: (p["adjrating"]))
                    if len(newopp) > 0:
                        tbscore[prefix + name]["cut"].append(newopp[0]["rnd"])
                    ratingopp = newopp[1:]
                trounds -= 1
                low -= 1
            while high > 0:
                if trounds == len(ratingopp):
                    newopp = sorted(ratingopp, key=lambda p: (p["adjrating"]))
                    if len(newopp) > 0:
                        tbscore[prefix + name]["cut"].append(newopp[-1]["rnd"])
                    ratingopp = newopp[:-1]
                trounds -= 1
                high -= 1
            rscore = 0
            ratings = []
            for p in ratingopp:
                rscore += p["rpoints"]
                ratings.append(p["adjrating"])

            tbscore[prefix + "aro"]["val"] = rating.ComputeAverageRatingOpponents(ratings)
            tbscore[prefix + "tpr"]["val"] = rating.ComputeTournamentPerformanceRating(rscore, ratings)
            tbscore[prefix + "ptp"]["val"] = rating.ComputePerfectTournamentPerformance(rscore, ratings)
        return tb["name"].lower()

    def compute_boardcount(self, tb, cmps, rounds):
        (points, scoretype, prefix) = self.get_scoreinfo(tb, True)
        for start_no, cmp in cmps.items():
            tbscore = cmp["tb_val"]
            bc = 0
            tbscore[prefix + "bc"] = {"val": bc}
            for val, points in tbscore["gpoints_" + "bp"].items():
                bc += val * points
                self.addtbval(tbscore[prefix + "bc"], val, val * points)
            tbscore[prefix + "bc"]["val"] = bc
        return "bc"

    def compute_singlerun_topbottomboardresult(self, tb, cmps, rounds, ro, loopcount):
        name = tb["name"].lower()
        (points, scoretype, prefix) = self.get_scoreinfo(tb, True)
        if loopcount == 0:
            for player in ro:
                player["tb_val"]["tbrval"] = Decimal("0.0")
                player["tb_val"]["bbeval"] = Decimal("0.0")
                for val, points in player["tb_val"]["gpoints_" + "bp"].items():
                    player["tb_val"]["bbeval"] += points
            return True
        if len(ro) == 0:
            return False
        for player in range(0, len(ro)):
            # helpers.json_output('-', ro[player]['tb_val'])
            # print(self.max_board, loopcount, self.max_board - loopcount +1)
            ro[player]["tb_val"]["tbrval"] = ro[player]["tb_val"]["gpoints_" + "bp"][loopcount]
            ro[player]["tb_val"]["bbeval"] -= ro[player]["tb_val"]["gpoints_" + "bp"][self.max_board - loopcount + 1]
        subro = sorted(ro, key=lambda p: (-p["tb_val"][name + "val"], p["cid"]))
        count = currentrank = ro[0]["tb_val"][prefix + name]["val"]
        for player in range(0, len(subro)):
            if subro[player]["tb_val"][name + "val"] != subro[player - 1]["tb_val"][name + "val"]:
                currentrank = count
            subro[player]["tb_val"][prefix + name]["val"] = currentrank
            self.addtbval(subro[player]["tb_val"][prefix + name], loopcount, subro[player]["tb_val"][name + "val"])
            # print(">", loopcount, subro[player]['cid'], subro[player]['tb_val']['mpoints_tbr'], subro[player][
            # 'tb_val']['tbrval'], subro[player]['tb_val']['moreloops'])
            count += 1
        return loopcount < self.max_board

    def compute_score_strength_combination(self, tb, cmps, current_round):
        (points, scoretype, prefix) = self.get_scoreinfo(tb, True)
        for start_no, cmp in cmps.items():
            dividend = cmp["tb_val"][prefix + "sssc"]["val"]
            divisor = 1
            key = points[0]
            if key == "m":
                score = cmp["tb_val"]["gpoints_" + "points"]["val"]
                divisor = math.floor(
                    self.scoreLists[scoretype]["W"]
                    * current_round
                    / self.scoreLists[self.game_score]["W"]
                    / self.max_board
                )
            elif key == "g":
                score = cmp["tb_val"]["mpoints_" + "points"]["val"]
                divisor = math.floor(
                    self.scoreLists[scoretype]["W"]
                    * current_round
                    * self.max_board
                    / self.scoreLists[self.matchscore]["W"]
                )
            if tb["modifiers"]["nlim"] > 0:
                divisor = tb["modifiers"]["nlim"]
            val = (score + dividend / divisor).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
            cmp["tb_val"][prefix + "sssc"] = {"val": val}
        return "sssc"

    def get_accelerated(self, rnd, start_no):
        if self.acceleration is None:
            return "Z"
        for val in self.acceleration["values"]:
            if (
                rnd >= val["firstRound"]
                and rnd <= val["lastRound"]
                and start_no >= val["firstCompetitor"]
                and start_no <= val["lastCompetitor"]
            ):
                return val["game_score"]
        return "Z"

    def compute_acc(self, tb, cmps, rounds):
        (points, scoretype, prefix) = self.get_scoreinfo(tb, True)
        if prefix + "acc" in cmps[1]["tb_val"]:
            return "acc"
        # scorelist = self.scoreLists[scoretype]

        for start_no, cmp in cmps.items():
            tbscore = cmp["tb_val"]
            acc = self.get_accelerated(1, start_no)
            val = self.scoreLists[scoretype][acc]
            tbscore[prefix + "acc"] = {"val": val, 0: val}
            spoints = 0  # Points so far
            for rnd in range(1, rounds + 1):
                p = cmp["rsts"][rnd][points] if rnd in cmp["rsts"] and points in cmp["rsts"][rnd] else Decimal("0.0")
                spoints += p
                acc = self.get_accelerated(rnd + 1, start_no)
                val = spoints + self.scoreLists[scoretype][acc]
                tbscore[prefix + "acc"][rnd] = val
            tbscore[prefix + "acc"]["val"] = val
        return "acc"

    def compute_flt(self, tb, cmps, rounds):
        (points, scoretype, prefix) = self.get_scoreinfo(tb, True)
        scorelist = self.scoreLists[scoretype]
        for start_no, cmp in cmps.items():
            tbscore = cmp["tb_val"]
            tbscore[prefix + "flt"] = {"val": 0}
            sfloat = 0  # Float so far
            for rnd in range(1, rounds + 1):
                sfloat //= 4
                p = cmp["rsts"][rnd][points] if rnd in cmp["rsts"] and points in cmp["rsts"][rnd] else Decimal("0.0")
                opp = cmp["rsts"][rnd]["opponent"] if rnd in cmp["rsts"] and "opponent" in cmp["rsts"][rnd] else 0
                if opp > 0:
                    ownacc = cmp["tb_val"][prefix + "acc"][rnd - 1]
                    oppacc = cmps[opp]["tb_val"][prefix + "acc"][rnd - 1]
                elif p > scorelist["L"]:
                    ownacc = 1
                    oppacc = 0
                else:
                    ownacc = 0
                    oppacc = 0
                if ownacc > oppacc:
                    cfloat = "d"
                    ifloat = 8
                elif ownacc < oppacc:
                    cfloat = "u"
                    ifloat = 4
                else:
                    cfloat = " "
                    ifloat = 0
                if rnd == 1 and cfloat == "u":
                    # print(start_no, opp)
                    # print(cmp['tb_val'])
                    # print(cmps[opp]['tb_val'])
                    pass
                self.addtbval(tbscore[prefix + "flt"], rnd, cfloat)
                sfloat += ifloat
            tbscore[prefix + "flt"]["val"] = sfloat
        return "flt"

    def compute_rfp(self, tb, cmps, rounds):
        (points, scoretype, prefix) = self.get_scoreinfo(tb, True)
        # print(self.lastplayedround)
        for start_no, cmp in cmps.items():
            tbscore = cmp["tb_val"]
            val = True
            tbscore[prefix + "rfp"] = {"val": val}
            for rnd in range(1, rounds + 2):
                val = True
                if rnd in cmp["rsts"]:
                    if cmp["rsts"][rnd]["opponent"] == 0:
                        clr = "w"
                    elif start_no == 0:
                        clr = "b"
                    else:
                        clr = cmp["rsts"][rnd]["color"]
                    val = (
                        str(cmp["rsts"][rnd]["opponent"]) + clr
                        if cmp["rsts"][rnd]["played"] or (cmp["rsts"][rnd]["opponent"] > 0)
                        else ""
                    )
                elif rnd > self.lastplayedround:
                    val = "Y" if cmp["present"] else ""
                else:
                    val = ""
                if rnd <= rounds:
                    tbscore[prefix + "rfp"][rnd] = val
            tbscore[prefix + "rfp"]["val"] = val
        return "rfp"

    def compute_top(self, tb, cmps, rounds):
        (points, scoretype, prefix) = self.get_scoreinfo(tb, True)
        last = self.rounds - 1
        lim = (
            self.scoreLists[scoretype]["W"] * last * (self.teamsize if points == "game_points" else 1) / Decimal("2.0")
        )
        for start_no, cmp in cmps.items():
            tbscore = cmp["tb_val"]
            val = (rounds >= last) and tbscore[prefix + "acc"][last] > lim
            tbscore[prefix + "top"] = {"val": val}
        return "top"

    def reverse_pointtype(self, txt):
        match txt:
            case "mpoints":
                return "game_points"
            case "game_points":
                return "mpoints"
            case "mmpoints":
                return "ggpoints"
            case "mgpoints":
                return "gmpoints"
            case "gmpoints":
                return "mgpoints"
            case "ggpoints":
                return "mmgpoints"
        return txt

    def parse_tiebreak(self, order, txt):
        # BH@23:IP/C1-P4F
        txt = txt.upper()
        comp = txt.replace("!", "/").replace("#", "/").split("/", 2)
        # if len(comp) == 1:
        #    comp = txt.split('-')
        nameparts = comp[0].split(":")
        nameyear = nameparts[0].split("@")
        nameyear.append("24")
        name = nameyear[0]
        year = int(nameyear[1])
        if self.primaryscore is not None:
            point_type = self.primaryscore
        elif self.is_team:
            point_type = "mpoints"
        else:
            point_type = "points"
        if name == "MPTS":
            point_type = "mpoints"
        if name == "GPTS":
            point_type = "game_points"

        if len(nameparts) == 2:
            match nameparts[1].upper():
                case "MP":
                    point_type = "mpoints"
                case "GP":
                    point_type = "game_points"
                case "MM":
                    point_type = "mmpoints"
                case "MG":
                    point_type = "mgpoints"
                case "GM":
                    point_type = "gmpoints"
                case "GG":
                    point_type = "ggpoints"
        if self.primaryscore is None and (name == "PTS" or name == "MPTS" or name == "GPTS"):
            self.primaryscore = point_type
        # if name == 'MPVGP':
        #    name = 'PTS'
        #        point_type = self.reverse_pointtype(self.primaryscore)

        tb = {
            "order": order,
            "name": name,
            "year": year,
            "point_type": point_type,
            "modifiers": {
                "low": 0,
                "high": 0,
                "plim": Decimal("50.0"),
                "nlim": Decimal("0.0"),
                "unr": self.unrated,
                "urd": False,
                "p4f": False,
                "sws": False,
                "fmo": False,
                "rb5": False,
                "z4h": False,
                "vun": False,
            },
        }
        for mf in comp[1:]:
            mf = mf.upper()
            for index in range(0, len(mf)):
                match mf[index]:
                    case "C":
                        if mf[1:].isdigit():
                            tb["modifiers"]["low"] = int(mf[1:])
                    case "M":
                        if mf[1:].isdigit():
                            tb["modifiers"]["low"] = int(mf[1:])
                            tb["modifiers"]["high"] = int(mf[1:])
                    case "L":
                        scale = Decimal("1.0") if "." in mf else Decimal(0.5)
                        numbers = mf.replace(".", "")
                        if mf[1:].isdigit():
                            tb["modifiers"]["plim"] = Decimal(mf[1:])
                        elif mf[1] == "+" and numbers[2:].isdigit():
                            tb["modifiers"]["nlim"] = Decimal(mf[2:]) * scale
                        elif mf[1] == "-" and numbers[2:].isdigit():
                            tb["modifiers"]["nlim"] = -Decimal(mf[2:]) * scale
                    case "K":
                        if mf[1:].isdigit():
                            tb["modifiers"]["nlim"] = Decimal(mf[1:])
                    case "D":
                        tb["modifiers"]["urd"] = True
                    case "U":
                        tb["modifiers"]["unr"] = int(mf[1:])
                    case "P":
                        tb["modifiers"]["p4f"] = True
                    case "F":
                        tb["modifiers"]["fmo"] = True
                    case "R":
                        tb["modifiers"]["rb5"] = True
                    case "d.S":
                        tb["modifiers"]["sws"] = True
                    case "Z":
                        tb["modifiers"]["z4h"] = True
                    case "V":
                        tb["modifiers"]["vun"] = True
        if self.rr and not tb["modifiers"]["sws"]:  # Default for RR is to treat unplayed games as played
            tb["modifiers"]["p4f"] = True
        return tb

    def addval(self, cmps, tb, value):
        (points, scoretype, prefix) = self.get_scoreinfo(tb, True)
        precision = 0
        for start_no, cmp in cmps.items():
            # print(prefix, scoretype, cmp['tb_val'])
            cmp["tiebreakScore"].append(cmp["tb_val"][prefix + value]["val"])
            cmp["tiebreakDetails"].append(cmp["tb_val"][prefix + value])
            if isinstance(cmp["tb_val"][prefix + value]["val"], Decimal):
                (s, n, e) = cmp["tb_val"][prefix + value]["val"].as_tuple()
                precision = min(precision, e)
        tb["precision"] = -precision

    def compute_average(self, tb, name, cmps, rounds, ignorezero, norm):
        (points, scoretype, prefix) = self.get_scoreinfo(tb, True)
        tbname = tb["name"].lower()
        for start_no, cmp in cmps.items():
            cmp["tb_val"][prefix + tbname] = {"val": 0, "cut": []}
            sum = Decimal(0.0)
            num = 0
            for rnd, rst in cmp["rsts"].items():
                if rst["played"] and rst["opponent"] > 0 and rnd <= rounds:
                    opponent = rst["opponent"]
                    value = cmps[opponent]["tb_val"][prefix + name]["val"]
                    if not ignorezero or value > 0:
                        num += 1
                        sum += value
                        self.addtbval(cmp["tb_val"][prefix + tbname], rnd, value)
            val = sum / Decimal(num) if num > 0 else Decimal("0.0")
            cmp["tb_val"][prefix + tbname]["val"] = val.quantize(Decimal(norm), rounding=ROUND_HALF_UP)
        return tbname

    # get_scoreinfo(self, tb, primary)
    # tb - tie-break
    # primary or secondary score

    def get_scoreinfo(self, tb, primary):
        pos = 0 if primary else 1
        key = tb["point_type"][pos]
        if not primary and (key != "g" and key != "m"):
            key = tb["point_type"][0]
            if key == "g":
                key = "m"
            elif key == "m":
                key = "g"
        match key:
            case "g":
                return ["game_points", self.game_score, "gpoints_"]
            case "m":
                return ["mpoints", self.matchscore, "mpoints_"]
            case _:
                return ["points", self.game_score, "points_"]

    def compute_tiebreak(self, tb):
        cmps = self.cmps
        tbname = ""
        match tb["name"]:
            case "PTS" | "MPTS" | "GPTS":
                tbname = "points"
            case "MPVGP":
                tb["point_type"] = self.reverse_pointtype(self.primaryscore)
                tbname = "points"
            case "SNO" | "RANK" | "RND":
                tb["modifiers"]["reverse"] = False
                tbname = tb["name"].lower()
            case "DF":
                tbname = self.compute_direct_encounter(tb, cmps, self.current_round)
            case "DE":
                # tbname = self.compute_direct_encounter(tb, cmps, self.current_round)
                tb["modifiers"]["reverse"] = False
                tbname = self.compute_recursive_if_tied(
                    tb, cmps, self.current_round, self.compute_singlerun_direct_encounter
                )
            case "EDGE":
                # tbname = self.compute_direct_encounter(tb, cmps, self.current_round)
                tb["modifiers"]["reverse"] = False
                tbname = self.compute_recursive_if_tied(
                    tb, cmps, self.current_round, self.compute_singlerun_ext_direct_encounter
                )
            case "WIN" | "WON" | "BPG" | "BWG" | "GE" | "REP" | "VUR" | "NUM" | "COP" | "COD" | "CSQ":
                tbname = tb["name"].lower()
            case "PS":
                tbname = self.compute_progressive_score(tb, cmps, self.current_round)
            case "KS":
                tbname = self.compute_koya(tb, cmps, self.current_round)
            case "BH" | "FB" | "SB" | "ABH" | "AFB":
                tbname = self.compute_buchholz_sonneborn_berger(tb, cmps, self.current_round)
            case "AOB":
                tbname = self.compute_buchholz_sonneborn_berger(tb, cmps, self.current_round)
                tbname = self.compute_average(tb, "bh", cmps, self.current_round, True, "0.01")
            case "ARO" | "TPR" | "PTP":
                tbname = self.compute_ratingperformance(tb, cmps, self.current_round)
            case "APRO":
                tbname = self.compute_ratingperformance(tb, cmps, self.current_round)
                tbname = self.compute_average(tb, "tpr", cmps, self.current_round, True, "1.")
            case "APPO":
                tbname = self.compute_ratingperformance(tb, cmps, self.current_round)
                tbname = self.compute_average(tb, "ptp", cmps, self.current_round, True, "1.")
            case "ESB" | "EMMSB" | "EMGSB" | "EGMSB" | "EGGSB":
                if len(tb["name"]) == 5:
                    tb["point_type"] = tb["name"][1:3].lower() + "points"
                tbname = self.compute_buchholz_sonneborn_berger(tb, cmps, self.current_round)
            case "BC":
                tb["modifiers"]["reverse"] = False
                tbname = self.compute_boardcount(tb, cmps, self.current_round)
            case "TBR" | "BBE":
                tb["modifiers"]["reverse"] = False
                tbname = self.compute_recursive_if_tied(
                    tb, cmps, self.current_round, self.compute_singlerun_topbottomboardresult
                )
            case "SSSC":
                tbname = self.compute_buchholz_sonneborn_berger(tb, cmps, self.current_round)
                tbname = self.compute_score_strength_combination(tb, cmps, self.current_round)
            case "ACC":
                tbname = self.compute_acc(tb, cmps, self.current_round)
            case "FLT":
                tbname = self.compute_acc(tb, cmps, self.current_round)
                tbname = self.compute_flt(tb, cmps, self.current_round)
            case "RFP":
                tbname = self.compute_rfp(tb, cmps, self.current_round)
            case "TOP":
                tbname = self.compute_acc(tb, cmps, self.current_round)
                tbname = self.compute_top(tb, cmps, self.current_round)
            case _:
                tbname = None
                return

        self.tiebreaks.append(tb)
        index = len(self.tiebreaks) - 1
        self.addval(cmps, tb, tbname)
        reverse = 1 if "reverse" in tb["modifiers"] and not tb["modifiers"]["reverse"] else -1
        # for cmp in self.rank_order:
        #    print(index, cmp['tiebreakScore'][index])
        self.rank_order = sorted(
            self.rank_order, key=lambda cmp: (cmp["rank"], cmp["tiebreakScore"][index] * reverse, cmp["cid"])
        )
        rank = 1
        val = self.rank_order[0]["tiebreakScore"][index]
        for i in range(1, len(self.rank_order)):
            rank += 1
            if self.rank_order[i]["rank"] == rank or self.rank_order[i]["tiebreakScore"][index] != val:
                self.rank_order[i]["rank"] = rank
                val = self.rank_order[i]["tiebreakScore"][index]
            else:
                self.rank_order[i]["rank"] = self.rank_order[i - 1]["rank"]
        # for i in range(0,len(self.rank_order)):
        #    t = self.rank_order[i]
        #    print(t['cid'], t['rank'], t['score'])
        # json.dump(self.cmps, sys.stdout, indent=2)
