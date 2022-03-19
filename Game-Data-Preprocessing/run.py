import os
import glob
import uuid
from datetime import datetime

import pandas as pd
from card_map import suit_map, rank_map
from player_game import Player_Game
COLS = [
    'S1','C1','S2','C2','S3','C3','S4','C4','S5','C5','S6','C6','S7','C7',
    'percentage_of_total_chips_hand',
    'percentage_of_hand_bet_pot',
    'percentage_of_total_chips_in_pot',
    'current_stage',
    'move',
    'result',
    'player_hand_ranking'
]

data_df = pd.DataFrame(
    
)

def data_reader():
    games = []
    for data_path in glob.glob("raw-data/*.txt"):
        data_file = open(data_path, "r")

        game = []

        for line in data_file:

            if 'PokerStars Hand' in line and len(game) != 0:
                games.append(game)
                game = []

            game.append(line)

    return games

def gather_players(game):
    players = []
    for line in game:
        if 'Seat' in line and 'button' not in line and 'won' not in line and 'lost' not in line:
            n_start, n_end, c_start, c_end =  line.find(':')+2, line.find('(')-1, line.find('(')+1, line.find(' in chips)')
            if c_end == -1:
                c_end = line.find(')')
            name = line[n_start:n_end]
            chips = float(line[c_start:c_end])

            players.append(
                {
                    'name':name,
                    'chips':chips
                }
            )
    return players

def process_game(game):
    players = gather_players(game)
    total_chips = 0
    for player in players:
        total_chips += player['chips']
    data_df_list = []
    for player in players:
        data_df_list.append(process_player(player, total_chips, game))
    data_df = pd.concat(data_df_list)
    return data_df

def process_player(player, total_chips, game):
    
    pg = Player_Game(player, game, total_chips)
    records = pg.gather_full_game_data()
    data_df = pd.DataFrame(records, columns=COLS)
    return data_df
    
def save_games(data_df_list, datetime_str):
    data_df = pd.concat(data_df_list)
    if os.path.exists(f'data-out/{datetime_str}') == False:
        os.makedirs(f'data-out/{datetime_str}')
    data_df.to_csv(f'data-out/{datetime_str}/data-{uuid.uuid4().hex}.csv')

if __name__ == '__main__':
    games = data_reader()
    data_df_list = []
    games_len = len(games)
    current_game = 0
    datetime_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    try:
        for game in games:
            current_game += 1
            print(f'{current_game}/{games_len}')
            data_df_list.append(process_game(game))
            if current_game%1000 == 0:
                save_games(data_df_list, datetime_str)
                data_df_list = []
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        save_games(data_df_list, datetime_str)