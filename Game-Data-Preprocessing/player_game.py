from card_map import suit_map, rank_map
import pickle
import itertools

hand_strength_model = pickle.load(open('hand-classication-model.pickle', 'rb'))


# Helper Functions
def combinationsNoOrder(a, n):
    if n == 1:
        for x in a:
            yield [x]
    else:
        for i in range(len(a)):
            for x in combinationsNoOrder(a[:i], n-1):
                yield [a[i]] + x

def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

class Player_Game():
    winner_list = []
    winner_hands = []
    
    player_name = None
    player_chips = 0
    player_chips_in_pot = 0
    pot_chips = 0
    total_chips = 0
    last_move = None

    player_hand = {
        'S1':0,
        'C1':0,
        'S2':0,
        'C2':0
    }

    community_hand = {
        'S3':0,
        'C3':0,
        'S4':0,
        'C4':0,
        'S5':0,
        'C5':0,
        'S6':0,
        'C6':0,
        'S7':0,
        'C7':0
    }

    game = None
    stage = -1

    flop_index = None
    turn_index = None
    river_index = None
    summery_index = None

    game_complete = False

    def __init__(self, player_stats, game, total_chips):
        self.player_name = player_stats['name']
        self.player_chips = player_stats['chips']
        self.game = game
        self.total_chips = total_chips

    def set_hand(self):
        hand_str = ''
        l = ''
        for line in self.game:
            if f'Dealt to {self.player_name}' in line:
                h_start, h_end = line.find('[')+1, line.find(']')
                hand_str = line[h_start:h_end]

        h1, h2 = hand_str.split(' ')

        self.player_hand['C1'] = rank_map[h1[0]]
        self.player_hand['C2'] = rank_map[h2[0]]
        self.player_hand['S1'] = suit_map[h1[1]]
        self.player_hand['S2'] = suit_map[h2[1]]

    def set_winner_list(self):
        for line in self.game:
            if 'collected' in line:
                self.winner_list.append(line.split(' ')[0])

    def set_winner_hands(self):
        for winner in self.winner_list:
            hand_str = ''
            for line in self.game:
                if f'Dealt to {self.player_name}' in line:
                    h_start, h_end = line.find('[')+1, line.find(']')
                    hand_str = line[h_start:h_end]
            h1, h2 = hand_str.split(' ')
            winner_hand = {}
            winner_hand['S1'] = suit_map[h1[1]]
            winner_hand['S2'] = suit_map[h2[1]]
            winner_hand['C1'] = rank_map[h1[0]]
            winner_hand['C2'] = rank_map[h2[0]]

            self.winner_hands.append(winner_hand)

    def get_current_status(self, stage):
        data = Merge(self.player_hand, self.community_hand)
        if (stage < 3):
            data['C7'] = 0
            data['S7'] = 0
        if (stage < 2):
            data['C6'] = 0
            data['S6'] = 0
        if (stage < 1):
            data['C3'] = 0
            data['S3'] = 0
            data['C4'] = 0
            data['S4'] = 0
            data['C5'] = 0
            data['S5'] = 0
        data['percentage_of_total_chips_hand'] = self.player_chips/self.total_chips
        data['percentage_of_hand_bet_pot'] = self.player_chips_in_pot/self.player_chips
        data['percentage_of_total_chips_in_pot'] = self.pot_chips/self.total_chips
        data['current_stage'] = self.stage
        data['move'] = self.last_move
        data['player_hand_ranking'] = self.rank_hand(Merge(self.player_hand, self.community_hand))

        return data

    def rank_hand(self, data):
        suit_keys = ['S1','S2','S3','S4','S5','S6','S7']
        rank_keys = ['C1','C2','C3','C4','C5','C6','C7']

        index_list = range(7)

        player_hand_rank = 0

        for index_list in combinationsNoOrder(index_list, 5):
            s_list = []
            r_list = []
            index_list_sorted = sorted(index_list)

            for index in index_list_sorted:
                r_list.append(data[rank_keys[index]])
                s_list.append(data[suit_keys[index]])
            l = r_list+s_list
            l = [l,]
            
            temp_hand_rank = hand_strength_model.predict(l)[0]
            if temp_hand_rank > player_hand_rank:
                player_hand_rank = temp_hand_rank
        return player_hand_rank

    def _reset(self):
        self.pot_chips=0
        self.player_chips_in_pot=0
        self.flop_index = None
        self.turn_index = None
        self.river_index = None
        self.summery_index = None
        
    def process_preflop(self):
        self.stage = 0
        self._reset() 
        for index, line in enumerate(self.game):
            self._process_line(line)
            if '*** FLOP ***' in line:
                self.flop_index = index
                return
        self.game_complete = True

    def process_postflop(self):
        if self.flop_index == None or self.turn_index != None:
            raise Exception('Process Preflop Must Be Run First')
        
        self.stage = 1
        
        line = self.game[self.flop_index]
        start, end = line.find('[')+1, line.find(']')
        cards_str = line[start:end]

        h3,h4,h5 = cards_str.split(' ')

        self.community_hand['C3'] = rank_map[h3[0]]
        self.community_hand['C4'] = rank_map[h4[0]]
        self.community_hand['C5'] = rank_map[h5[0]]
        self.community_hand['S3'] = suit_map[h3[1]]
        self.community_hand['S4'] = suit_map[h4[1]]
        self.community_hand['S5'] = suit_map[h5[1]]

        for index in range(self.flop_index, len(self.game)):
            line = self.game[index]
            self._process_line(line)
            if '*** TURN ***' in line:
                self.turn_index = index
                return
        self.game_complete = True

    def process_postturn(self):

        self.stage = 2
        
        line = self.game[self.turn_index]
        start, end = line.find('[', 24)+1, line.find(']', 25)
        cards_str = line[start:end]

        h6 = cards_str

        self.community_hand['C6'] = rank_map[h6[0]]
        self.community_hand['S6'] = suit_map[h6[1]]

        for index in range(self.turn_index, len(self.game)):
            line = self.game[index]
            self._process_line(line)
            if '*** RIVER ***' in line:
                self.river_index = index
                return
        self.game_complete = True

    def process_postriver(self):

        self.stage = 3
        
        line = self.game[self.river_index]
        start, end = line.find('[', 29)+1, line.find(']', 29)
        cards_str = line[start:end]

        h7 = cards_str

        self.community_hand['C7'] = rank_map[h7[0]]
        self.community_hand['S7'] = suit_map[h7[1]]

        for index in range(self.river_index, len(self.game)):
            line = self.game[index]
            self._process_line(line)
            if '*** SUMMARY ***' in line:
                self.game_complete = True
                return
        self.game_complete = True

    def _process_line(self, line):
        if 'posts small blind' in line or 'posts big blind' in line:
            val = int(line.split(' ')[-1])
            self.pot_chips += val
            if self.player_name in line:
                self.player_chips_in_pot += val 
        if 'raises' in line:
            index = -3
            if 'all-in' in line:
                index = -6
            val = int(line.split(' ')[index])
            self.pot_chips += val
            if self.player_name in line:
                self.player_chips_in_pot += val
                self.last_move = 2
        if 'calls' in line:
            index = -1
            if 'all-in' in line:
                index = -4
            val = int(line.split(' ')[index])
            self.pot_chips += val
            if self.player_name in line:
                self.player_chips_in_pot += val 
                self.last_move = 1
        if 'folds' in line and self.player_name in line:
            self.last_move = 0
            self.game_complete = True


    def gather_full_game_data(self):
        records = []
        self.set_hand()
        self.set_winner_list()
        self.process_preflop()
        records.append(self.get_current_status(0))
        if self.game_complete != True:
            self.process_postflop()
            records.append(self.get_current_status(1))
            if self.game_complete != True:
                self.process_postturn()
                records.append(self.get_current_status(2))
                if self.game_complete != True:
                    self.process_postriver()
                    records.append(self.get_current_status(3))
        self.set_winner_hands()
        won = self.player_name in self.winner_list
        for record in records:
            if won:
                record['result'] = 1
            else:
                winning_hand_rank = 0
                for hand in self.winner_hands:
                    rank = self.rank_hand(Merge(hand, self.community_hand))
                    if rank > winning_hand_rank:
                        winning_hand_rank = rank
                player_hand_rank = self.rank_hand(Merge(self.player_hand, self.community_hand))
                
                record['result'] = 1
                if winning_hand_rank < player_hand_rank:
                    record['result'] = 0
        return records