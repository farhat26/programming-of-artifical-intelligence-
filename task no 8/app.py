import requests
from flask import Flask, render_template, redirect
from datetime import datetime

app = Flask(__name__)

# NASA API key
api_key = "g316u73kTr4FUzA8Wt03bNfOpZDeUS9WaTwvy0fs"
base_url = f"https://api.nasa.gov/neo/rest/v1/feed?api_key={api_key}"

@app.route('/')
def main():
    # Default: today's date
    today = datetime.today().strftime('%Y-%m-%d')
    return redirect(f'/{today}')

@app.route('/<date>')
def specificdate(date):
    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return f"Invalid date format. Use YYYY-MM-DD."

    # Fetch data for the date
    response = requests.get(base_url + f"&start_date={date}&end_date={date}")
    if response.status_code == 200:
        nasadata = response.json()
        return render_template("index.html", data=nasadata, selected_date=date)
    else:
        return f"Error fetching NASA data: {response.status_code} - {response.text}"

if __name__ == "__main__":
    app.run(debug=True)