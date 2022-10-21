from webbrowser import get
import pandas as pd
import random
from potgame import Player, Hole, GolfCourse, PotGame, Rules


def main():
    game_df, hole_df = get_data_from_file("Potgame 2022 old.xlsx")

    hole_info = get_holes(hole_df)
    course = GolfCourse("York", hole_info)
    rules = Rules(skin_strokes=0.5, par_3_skin_strokes=False, par_3_net_strokes=True)
    player_list = create_player_list(game_df, course, rules)

    # get friday skins and two man results
    date = '10-21-22'
    game = PotGame(player_list, game_df, course, rules)
    write_friday_game_results(game, date)
    # get friday four man scores by team: :params: team_no, no_of_players, course_par, last_hole_par
    #game.get_friday_four_man_results(4, 4, 71, 4)

def write_friday_game_results(game, date):
    two_man = game.get_two_man_total()
    skin_winners = game.get_skins_no_validation()[0]
    skin_ties = game.get_skins_no_validation()[1]

    with pd.ExcelWriter(f"{date}_results.xlsx") as writer:
        two_man.to_excel(writer, sheet_name="two man", index=False)
        skin_winners.to_excel(writer, sheet_name="skins", index=False)
        skin_ties.to_excel(writer, sheet_name="skin ties", index=False)


def create_random_teams(n):
    """Helper function to create random numbers for teams"""
    numbers = list(range(n))
    random.shuffle(numbers)

    return numbers


def add_net_and_draw(df):
    """Helper function draw and net totals to game data"""
    draw_list = create_random_teams(df.shape[0])
    net = df["Total"] - df["HDCP"]
    df.insert(2, "Draw", draw_list)
    df.insert(3, "Net Total", net)
    df = df.sort_values("Draw")

    return df


def get_data_from_file(file):
    """
    Reads the potgame file to get the necessary dataframes for scoring
    :return: game_df (all player and score info) and hole_df (hole number, par, handicap) as a tuple
    """
    # the game data - players, handicaps, scores
    player_df = pd.read_excel(file, header=2)
    game_df = add_net_and_draw(player_df)

    # the holes
    use_cols = list(range(2, 21))
    hole_df = pd.read_excel(file, header=None, usecols=use_cols, index_col=0, nrows=2)

    return game_df, hole_df


def get_holes(df):
    """ Uses df of hole info to return a list of class Hole instances"""
    df.columns = list(range(1, 19))
    hole_dict = df.to_dict()
    hole_info = []
    for key, value in hole_dict.items():
        number = key
        par = value["Par"]
        handicap = value["Hole HDCP"]
        hole_info.append(Hole(number, par, handicap))

    return hole_info


def create_player_list(df, course, rules):
    """ Uses df, course instance and rules instance to return a list of Player instances"""
    player_list = []
    names = df[["Name"]]
    team = df[["Team"]]
    handicaps = df[["HDCP"]]
    draw = df[["Draw"]]
    net = df[["Net Total"]]
    scores = df.loc[:, 1:18]
    gross = df[["Total"]]
    for n in range(df.shape[0]):
        player = Player(
            name=names.iloc[n, 0],
            team=team.iloc[n, 0],
            handicap=handicaps.iloc[n, 0],
            draw=draw.iloc[n, 0],
            net_total=net.iloc[n, 0],
            gross_scores=scores.iloc[n, 0:18],
            gross_total=gross.iloc[n, 0],
            rules=rules,
            course=course,
        )
        player_list.append(player)

    return player_list





if __name__ == "__main__":
    main()
