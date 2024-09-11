#!/bin/python3.11

import json
import plotly.express as px
import plotly.io as pio
import requests
from flask import Flask, render_template
from dotenv import dotenv_values
from pymongo import MongoClient

app = Flask(__name__)
config = dotenv_values(".env")  # hidden variables located in .env file not checked in

client = MongoClient(config['MONGODB_URL'])
db = client['fortnite_db']
stats_collection = db['fortnite_stats']

@app.route('/stats')
def get_stats():
    stats = {}
    categories = ['battlePass', 'overall']
    for cat in categories:
        stats[cat] = {}  # list(db[cat].find())

        if cat == 'battlePass':
            cols = ['level', 'progress']
        else:
            cols = ['kd', 'matches', 'kills', 'wins']

        for col in cols:
            stats[cat][col] = []

        for doc in db[cat].find():
            for col in cols:
                stats[cat][col].append(doc[col])

        print(stats[cat])
    return stats


@app.route("/")
def home():
    stats = get_stats()

    if stats:
        overall = stats["overall"]
        battle_pass = stats["battlePass"]

        # 1. Overall Performance Summary
        overall_performance = {
            "wins": overall["wins"][-1],
            "kd": overall["kd"][-1],
            
        }

        # 4. Battle Pass Progress
        battle_pass_progress = {
            "level": battle_pass["level"][-1],
            "progress": battle_pass["progress"][-1]
        }

        # 7. Performance Heatmap - Kills/Deaths Over Time
        kd = overall['kd']
        matches = overall['matches']
        kills = overall['kills']
        wins = overall['wins']

        data = {"Kills": kills, "KD": kd, "Matches": matches, "Wins": wins}

        # Create a Plotly figure
        fig = px.line(data, x='Matches', y=['KD'],
                      labels={'value': 'Rate', 'variable': 'Metric'},
                      title="KD Performance Over Matches")

        # Convert the figure to HTML
        plot_html = pio.to_html(fig, full_html=False)

        return render_template('index.html',
                               overall_performance=overall_performance,
                               battle_pass_progress=battle_pass_progress,
                               plot_html=plot_html)
    else:
        return "No Data", 404


app.run(host="0.0.0.0", port=80)
