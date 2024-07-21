import matplotlib.pyplot as plt
import json
import os
import numpy as np
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

random_path = os.path.join(CURRENT_DIR, 'random_stats.json')
agent_path = os.path.join(CURRENT_DIR, 'agent_stats.json')

def plot_game_results(path):
    with open(path, "r") as file:
        data = json.load(file)

    games = data['Games']
    results = [game['Result'] for game in games]

    # Calculate cumulative statistics
    total_games = len(results)
    wins = results.count('Win')
    losses = results.count('Loss')
    draws = total_games - wins - losses  # Assuming any non-Win and non-Loss is a Draw

    # Calculate rates over time
    def calculate_rate(result_type):
        return [sum(1 for r in results[:i+1] if r == result_type) / (i+1) for i in range(total_games)]

    win_rates = calculate_rate('Win')
    loss_rates = calculate_rate('Loss')
    draw_rates = calculate_rate('Draw')

    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(range(1, total_games + 1), win_rates, label='Win Rate', color='green')
    plt.plot(range(1, total_games + 1), loss_rates, label='Loss Rate', color='red')
    plt.plot(range(1, total_games + 1), draw_rates, label='Draw Rate', color='blue')

    # Customize the plot
    plt.title('Chess Agent Performance')
    plt.xlabel('Number of Games Played')
    plt.ylabel('Rate')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    # Set x-axis ticks to show fewer, rounded numbers
    x_ticks = np.linspace(1, total_games, 10, dtype=int)
    plt.xticks(x_ticks)

    # Add text for total statistics
    stats_text = f'Total Games: {total_games}\nWins: {wins}\nLosses: {losses}\nDraws: {draws}'
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.show()    

plot_game_results(agent_path)