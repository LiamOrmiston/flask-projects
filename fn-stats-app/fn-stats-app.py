#!/bin/python3.11

import json
import plotly.express as px
import plotly.io as pio
import requests
from flask import Flask, render_template
from dotenv import dotenv_values

app = Flask(__name__)
config = dotenv_values(".env")  # hidden variables located in .env file not checked in

def get_stats():
    params = {'name': config['USERNAME']}
    url = f"https://fortnite-api.com/v2/stats/br/v2"
    response = json.loads(requests.get(url, params=params, headers={'Authorization': config['API_KEY']}).text)
    return response

api_response = get_stats()

@app.route("/")
def home():
    stats = api_response["data"]["stats"]["all"]["overall"]
    battle_pass = api_response["data"]["battlePass"]

    # 1. Overall Performance Summary
    overall_performance = {
        "wins": stats["wins"],
        "win_rate": stats["winRate"],
        "kd": stats["kd"],
        "kills_per_match": stats["killsPerMatch"]
    }

    # 4. Battle Pass Progress
    battle_pass_progress = {
        "level": battle_pass["level"],
        "progress": battle_pass["progress"]
    }

    # 7. Performance Heatmap - Kills/Deaths Over Time
    kills = stats["kills"]
    deaths = stats["deaths"]
    matches = stats["matches"]

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


app.run(host="0.0.0.0", port=80)
