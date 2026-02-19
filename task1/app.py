import os
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time
from flask import Flask, request, render_template, jsonify, send_file, url_for
import threading

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
PROGRESS_FILE = 'progress.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# --- Helper functions ---
def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"status": "", "results": [], "done": False}

def extract_emails(html):
    return set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html))

def get_internal_links(base_url, html):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            links.add(full_url.split('#')[0])
    return links

def crawl_website(base_url, max_pages=50):
    visited = set()
    to_visit = set([base_url])
    all_emails = set()
    while to_visit and len(visited) < max_pages:
        url = to_visit.pop()
        if url in visited:
            continue
        progress = load_progress()
        progress["status"] = f"Searching: {url}"
        save_progress(progress)
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                visited.add(url)
                continue
            html = response.text
            all_emails.update(extract_emails(html))
            internal_links = get_internal_links(base_url, html)
            to_visit.update(internal_links - visited)
        except:
            pass
        visited.add(url)
        time.sleep(1)
    return list(all_emails)

def scrape_file(filepath):
    df = pd.read_excel(filepath)
    results = []
    for index, row in df.iterrows():
        url = str(row['URL']).strip()
        if not url.startswith("http"):
            url = "http://" + url
        emails = crawl_website(url, max_pages=10)
        results.append({'URL': url, 'Emails': ', '.join(emails)})
    output_file = os.path.join(DOWNLOAD_FOLDER, 'company_emails.xlsx')
    pd.DataFrame(results).to_excel(output_file, index=False)
    progress = {"status": "Done!", "results": results, "done": True}
    save_progress(progress)

# --- Flask Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file"}), 400
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    save_progress({"status": "Starting...", "results": [], "done": False})
    threading.Thread(target=scrape_file, args=(filepath,), daemon=True).start()
    return jsonify({"success": True})

@app.route("/progress")
def progress_route():
    return jsonify(load_progress())

@app.route("/download")
def download_file():
    return send_file(os.path.join(DOWNLOAD_FOLDER, "company_emails.xlsx"), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=False, threaded=True)  # <-- debug=False important
