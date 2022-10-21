from operator import concat
import pandas as pd
from dataclasses import dataclass


"""
A potgame has the following:
1. Players - a list with name, handicap and gross scores
2. A course - with hole numbers and pars (also yardages, but that's another matter)
3. Games (4 man, 2 man, skins, etc.) with game rules
4. Game scores (gross, net, skins)
5. Entry fees
6. Payouts

Any mutable objects must use the dataclasses 'field' keyword (see Advanced Default Values in RP tutorial)
"""


@dataclass
class Hole:
    number: int
    par: int
    handicap: int


@dataclass
class GolfCourse:
    name: str
    hole_info: list


@dataclass
class Rules:
    skin_strokes: float
    par_3_skin_strokes: bool
    par_3_net_strokes: bool
    to_make_cut: int = 77


@dataclass
class Player:
    name: str
    team: int
    handicap: int
    draw: int
    net_total: int
    gross_scores: list
    gross_total: int
    course: GolfCourse
    rules: Rules

    def get_net_scores(self):
        net_scores = []
        for ind, score in enumerate(self.gross_scores):
            hole = self.course.hole_info[ind]
            if self.handicap >= hole.handicap:
                if hole.par > 3:
                    net_scores.append(score - 1)
                elif self.rules.par_3_net_strokes:
                    net_scores.append(score - 1)
                else:
                    net_scores.append(score)
            else:
                net_scores.append(score)

        self.net_scores = net_scores

        return self.net_scores

    def get_skin_scores(self):
        skin_scores = []
        for ind, score in enumerate(self.gross_scores):
            hole = self.course.hole_info[ind]
            if self.handicap >= hole.handicap:
                if hole.par > 3:
                    skin_scores.append(score - self.rules.skin_strokes)
                elif self.rules.par_3_skin_strokes:
                    skin_scores.append(score - self.rules.skin_strokes)
                else:
                    skin_scores.append(score)
            else:
                skin_scores.append(score)

        self.skin_scores = skin_scores

        return self.skin_scores


@dataclass
class PotGame:
    players: list
    df: pd.core.frame.DataFrame
    course: GolfCourse # do I need?
    rules: Rules

    # games to code: four man, two man total, two man best ball, skins (with and without validation), leaderboard (gross and net)



    def get_friday_four_man_results(self, team_no, no_of_players, course_par, last_hole_par):
        temp_list = []
        for player in self.players:
            if player.team == team_no:
                temp_list.append(player.get_net_scores())
        
        # THIS IS WHAT I NEED. NEED A FUNCTION TO TAKE IT OUT OF THIS METHOD? Use in 2 man best ball
        score_list = []
        hole = 0
        while hole < 17:
            temp_score_list = []
            player = 0
            while player < no_of_players:
                temp_score_list.append(temp_list[player][hole])
                player +=1
            score_list.append(sorted(temp_score_list)[0])
            score_list.append(sorted(temp_score_list)[1])
            hole+=1

        # all balls on 18
        player = 0
        while player < no_of_players:
                score_list.append(temp_list[player][17])
                player +=1

        total_team_score = sum(score_list)
        total_par = course_par * 2 + last_hole_par * 2
        score_to_par = total_team_score - total_par
        print(total_par)

        print(f"Team #{team_no}'s score was {total_team_score} or {score_to_par}")
                

    def get_two_man_total(self):
        # create a list of players who made the cut
        draw_contestants = []
        for player in self.players:
            if self.rules.to_make_cut and player.net_total <= self.rules.to_make_cut:
                contestant = {"name": player.name, "draw": player.draw, "net": player.net_total}
                draw_contestants.append(contestant)
            elif self.rules.to_make_cut and player.net_total > self.rules.to_make_cut:
                print(f"{player.name} had net {player.net_total} and missed the cut")
            else:
                contestant = {"name": player.name, "draw": player.draw, "net": player.net_total}
                draw_contestants.append(contestant)
        
        # create teams and tally scores - the players list is in draw order already
        team_results = {}
        for n in range(0, len(draw_contestants), 2):
            team_results[f"team {n}"] = {}
            player1 = draw_contestants[n]["name"]
            draw1 = draw_contestants[n]["draw"]
            score1 = draw_contestants[n]["net"]
            try:
                player2 = draw_contestants[n+1]["name"]
                draw2 = draw_contestants[n+1]["draw"]
                score2 = draw_contestants[n+1]["net"]
            except:  # if odd number of players, player2 becomes the first player in the draw
                player2 = draw_contestants[0]["name"]
                draw2 = draw_contestants[0]["draw"]
                score2 = draw_contestants[0]["net"]

            team_results[f"team {n}"]["Draws"] = f"{draw1}, {draw2}"
            team_results[f"team {n}"]["Players"] = f"{player1} ({score1}) / {player2} ({score2})"
            team_results[f"team {n}"]["Score"] = score1 + score2

        return pd.DataFrame.from_dict(team_results, orient="index").sort_values(by="Score")

    
    def get_two_man_bestball(self):
        pass

    def get_skins_no_validation(self):
        skin_list = []
        for i in range(0, 18):
            temp_skin_list = []
            for player in self.players:
                player_score = player.get_skin_scores()[i]
                hole = i + 1
                data = {"hole": hole, "name": player.name, "score": player_score}
                if len(temp_skin_list) == 0:
                    temp_skin_list.append(data)
                else:
                    if player_score < temp_skin_list[0]["score"]:
                        temp_skin_list = []
                        temp_skin_list.append(data)
                    elif player_score == temp_skin_list[0]["score"]:
                        temp_skin_list.append(data)
            
            skin_list.append(temp_skin_list) 
        
        winners = {}
        ties = {}
        for i, l in enumerate(skin_list):
            if len(l) == 1:
                winners[l[0]["hole"]] = {"hole": l[0]["hole"], "name": l[0]["name"], "score": l[0]["score"]}
            else:
                for ind, tie in enumerate(l):
                    ties[f"{tie['hole']}.{ind}"] = {"hole": tie["hole"], "name": tie["name"], "score": tie["score"]}
        
        return (
                pd.DataFrame.from_dict(winners, orient="index"),
                pd.DataFrame.from_dict(ties, orient="index")
            )
                