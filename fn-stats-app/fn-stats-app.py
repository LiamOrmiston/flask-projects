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
        stats[cat] = db[cat].find_one(sort=[("_id", -1)])
    return stats


@app.route("/")
def home():
    stats = get_stats()

    if stats:
        overall = stats["overall"]
        battle_pass = stats["battlePass"]

        # 1. Overall Performance Summary
        overall_performance = {
            "wins": overall["wins"],
            "win_rate": overall["winRate"],
            "kd": overall["kd"],
            "kills_per_match": overall["killsPerMatch"]
        }

        # 4. Battle Pass Progress
        battle_pass_progress = {
            "level": battle_pass["level"],
            "progress": battle_pass["progress"]
        }

        # 7. Performance Heatmap - Kills/Deaths Over Time
        kills = overall["kills"]
        deaths = overall["deaths"]
        matches = overall["matches"]

        data = {"Kills": [kills], "Deaths": [deaths], "Matches": [matches]}

        # Create a Plotly figure
        fig = px.line(data, x='Matches', y=['Kills', 'Deaths'],
                      labels={'value': 'Rate', 'variable': 'Metric'},
                      title="Performance Over Matches")

        # Convert the figure to HTML
        plot_html = pio.to_html(fig, full_html=False)

        return render_template('index.html',
                               overall_performance=overall_performance,
                               battle_pass_progress=battle_pass_progress,
                               plot_html=plot_html)
    else:
        return "No Data", 404


app.run(host="0.0.0.0", port=80)
