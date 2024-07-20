"""
Hyper parameters:
    - Relevance values
    - epsilon for exploration
    - min_relevance
        
Would a longer decision path result in a better action?
Not sure how you would prune the graph for something like this. It doesn't necessarily make sense to forget about states
entirely and it also doesn't really make sense to try and make average nodes either. 
"""

import chess
import random
import ujson as json
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

piece_table = {
    'K': {'white': False, 'value': 0},  
    'k': {'white': True, 'value': 0},
    'Q': {'white': False, 'value': 9},
    'q': {'white': True, 'value': 9},
    'R': {'white': False, 'value': 5},
    'r': {'white': True, 'value': 5},
    'B': {'white': False, 'value': 3},
    'b': {'white': True, 'value': 3},
    'N': {'white': False, 'value': 3},
    'n': {'white': True, 'value': 3},
    'P': {'white': False, 'value': 1},
    'p': {'white': True, 'value': 1},
    ' ': {'white': None, 'value': -1}
}

class Node:
    def __init__(self, features, happiness=0, results={}):
        self.features = features
        self.happiness = happiness
        self.results = results

    def jsonify(self):
        """
        Converts node objects to dictionaries to store them in a JSON file.
        """
        node_json = {
            'features': self.features,
            'happiness': self.happiness,
            'results': self.results
        }
        return node_json
    
def record_results(agent_won):
    data = open(f"{CURRENT_DIR}/random_stats.json", "r")
    game_data = json.load(data)
    game_number = game_data["Current Game"]
    game_data["Games"].append({
        "Game Number": game_number,
        "Result": agent_won
    })

    game_data["Current Game"] += 1
    data.close()

    with open(f"{CURRENT_DIR}/random_stats.json", "w") as fh:
        json.dump(game_data, fh) 

def move_to_tuple(move_uci):
    move = chess.Move.from_uci(move_uci)
    from_square = move.from_square
    to_square = move.to_square
    
    from_x, from_y = from_square % 8, 7 - (from_square // 8)
    to_x, to_y = to_square % 8, 7 - (to_square // 8)
    
    return (from_x, from_y), (to_x, to_y)

def algebraic_to_tuple(board, algebraic_move):
    move = board.parse_san(algebraic_move)
    return move_to_tuple(board, move.uci())

def extract_features(board, color):
    # Initialize an empty 2D array
    board_array = [[' ' for _ in range(8)] for _ in range(8)]
    
    # Iterate over all squares on the board
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - (square // 8)
            col = square % 8
            board_array[row][col] = piece.symbol()
    
    return {'board': board_array, 'color': color}

def perform_move(board, start_x, start_y, end_x, end_y):
    for move in board.legal_moves:
        valid_start, valid_end = move_to_tuple(move.uci())
        valid_start_x = valid_start[0]
        valid_start_y = valid_start[1]
        valid_end_x = valid_end[0]
        valid_end_y = valid_end[1]
        if valid_start_x == start_x and valid_start_y == start_y and valid_end_x == end_x and valid_end_y == end_y:
            board.push(move)
            return -1

    return 1

def get_action(current_actions, graph_size, initial_epsilon=1.0, min_epsilon=0.1, decay_rate=0.01):
    """
    Selects actions using an epsilon-greedy strategy where epsilon decreases as the graph size grows.
    
    Parameters:
    - current_actions (dict): A dictionary containing rewards for start_x, start_y, end_x, and end_y.
    - graph_size (int): The current size of the graph, which affects the decay of epsilon.
    - initial_epsilon (float): The starting value of epsilon.
    - min_epsilon (float): The minimum value of epsilon.
    - decay_rate (float): The rate at which epsilon decays as the graph size increases.

    Returns:
    - move: The selected start and end coordinates (start_x, start_y, end_x, end_y).
    """
    
    # Calculate epsilon
    epsilon = max(min_epsilon, initial_epsilon * (1 / (1 + decay_rate * graph_size)))
    
    def select_action(rewards):
        if random.random() < epsilon:
            # Random action (exploration)
            return random.choice(list(rewards.keys()))
        else:
            # Best action (exploitation)
            return max(rewards, key=rewards.get)
    
    start_x = select_action(current_actions['actions']['start_x'])
    start_y = select_action(current_actions['actions']['start_y'])
    end_x = select_action(current_actions['actions']['end_x'])
    end_y = select_action(current_actions['actions']['end_y'])
    
    return start_x, start_y, end_x, end_y

def do_random_move(board):
    legal_moves = list(board.legal_moves)
    random_move = random.choice(legal_moves)
    board.push(random_move)

def calculate_relevance(node1, node2):
    board1 = node1.features['board']
    board2 = node2.features['board']
    node1_color = node1.features['color']
    node2_color = node2.features['color']

    relevance = 0

    if node1_color == node2_color:
        relevance += 25

    # loop over boards 
    for i in range(8):
        for j in range(8):
            piece1 = piece_table[board1[i][j]]
            piece2 = piece_table[board2[i][j]]
            piece1_color = piece1['white']
            piece2_color = piece2['white']
            piece1_value = piece1['value']
            piece2_value = piece2['value']
            # same color piece
            if piece1_color and piece2_color: # not an empty space
                if piece1_color == piece2_color:  
                    relevance += 0.5
            # piece in both positions
            if piece1_value != -1 and piece2_value != -1:
                relevance += 0.25
            # same kind of piece in the same spot
            if piece1_value == piece2_value:    
                relevance += 0.5
    
    return relevance

def find_most_relevant_node(graph, node):
    """
    Loops over the graph and finds the most relevant node.
    Returns the most relevant node and its relevance value.
    """
    max_relevance = float('-inf')
    most_relevant_node = None

    for other_node in graph:
        relevance_value = calculate_relevance(node, other_node)
        if relevance_value > max_relevance:
            max_relevance = relevance_value
            most_relevant_node = other_node
    if most_relevant_node is None:
        return False
    
    return {most_relevant_node: max_relevance}

# initial things that remain constant throughout
graph = []
graph_size = 0
min_relevance = 50
learning_rate = 0.1

for i in range(9000):
    # Every game
    board = chess.Board()
    random_num = random.choice([0, 1])
    if random_num == 1:
        agent_color = chess.WHITE
        agent_turn = True
    else:
        agent_color = chess.BLACK
        agent_turn = False
    
    game_nodes = []
    current_actions = {
        'actions':
            {
                'start_x': {},
                'start_y' : {},
                'end_x': {},
                'end_y': {}
            }
    }

    for action in current_actions['actions']:
        for i in range(8):
            current_actions['actions'][action].update({i: 0})

    while not board.is_game_over():
        if agent_turn:
            # # Every turn
            # graph_size += 1
            # feature_dict = extract_features(board, agent_color)
            # initial_node = Node(features=feature_dict)
            # decision_path = []
            # # traverse the graph
            # result = find_most_relevant_node(graph, initial_node)

            # if result: # a node above the minimum relevance was found
            #     current_node = next(iter(result))
            #     relevance = next(iter(result.values()))

            #     while relevance > min_relevance and current_node not in decision_path: 
            #         decision_path.append(result)
            #         result = find_most_relevant_node(graph, current_node) # potentially modify to be a list of nodes instead
            #         current_node = next(iter(result))
            #         relevance = next(iter(result.values()))
            #         if any(current_node in node for node in decision_path): # don't loop
            #             break

            # # update current actions
            # for result in decision_path:
            #     node = next(iter(result))
            #     relevance = next(iter(result.values()))
            #     print(f'relevance: {relevance}')
            #     for action in node.results['actions']:
            #         for number_choice, reward in node.results['actions'][action].items():
            #             current_actions['actions'][action][number_choice] += (reward * relevance * node.happiness) / learning_rate

            # from_x, from_y, to_x, to_y = get_action(current_actions, graph_size)
            
            # # do action and update the rewards
            # reward = perform_move(board, from_x, from_y, to_x, to_y)
            # current_actions['actions']['start_x'][from_x] += reward
            # current_actions['actions']['start_y'][from_y] += reward
            # current_actions['actions']['end_x'][to_x] += reward
            # current_actions['actions']['end_y'][to_y] += reward

            # initial_node.results = current_actions
            # game_nodes.append(initial_node) # Potential issue here since I want to continually add to the graph for the decision making
            # agent_turn = not agent_turn # alternate turns
            do_random_move(board)
            agent_turn = not agent_turn

        else: # not the agent's turn so just do a random move
            do_random_move(board)
            agent_turn = not agent_turn

    # game over logic here
    outcome = board.outcome()
    if outcome:
        winner = outcome.winner
        # Check if the game is a draw
        if outcome.termination in [chess.Termination.STALEMATE, chess.Termination.INSUFFICIENT_MATERIAL, chess.Termination.THREEFOLD_REPETITION, chess.Termination.FIFTY_MOVES]:
            happiness_update = 0
            print('draw')
            record_results("Draw")
        # Check for win condition
        elif (winner == chess.WHITE and agent_color == chess.WHITE) or (winner == chess.BLACK and agent_color == chess.BLACK):
            happiness_update = 1
            print('agent won')
            record_results("Win")
        # Anything else is a loss
        else:
            happiness_update = -1
            print('agent lost')
            record_results("Loss")

    for node in game_nodes:
        print('adding node')
        node.happiness += happiness_update
        graph.append(node)
    