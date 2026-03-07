import requests
from flask import Flask, redirect
from datetime import datetime

app = Flask(__name__)

api_key = "g316u73kTr4FUzA8Wt03bNfOpZDeUS9WaTwvy0fs"
base_url = f"https://api.nasa.gov/neo/rest/v1/feed?api_key={api_key}"


@app.route('/')
def main():
    today = datetime.today().strftime('%Y-%m-%d')
    return redirect(f"/{today}")


@app.route('/<date>')
def asteroids(date):

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD"

    response = requests.get(base_url + f"&start_date={date}&end_date={date}")

    if response.status_code != 200:
        return "Error fetching NASA data"

    data = response.json()

    asteroids = data["near_earth_objects"].get(date, [])

    output = f"<h1>Asteroids on {date}</h1>"

    for asteroid in asteroids:
        name = asteroid["name"]
        magnitude = asteroid["absolute_magnitude_h"]

        min_d = asteroid["estimated_diameter"]["meters"]["estimated_diameter_min"]
        max_d = asteroid["estimated_diameter"]["meters"]["estimated_diameter_max"]

        hazard = asteroid["is_potentially_hazardous_asteroid"]

        output += f"""
        <hr>
        <b>Name:</b> {name}<br>
        <b>Magnitude:</b> {magnitude}<br>
        <b>Diameter:</b> {min_d:.2f} - {max_d:.2f} meters<br>
        <b>Hazardous:</b> {"YES" if hazard else "NO"}<br>
        """

    return output


if __name__ == "__main__":
    app.run(debug=True)