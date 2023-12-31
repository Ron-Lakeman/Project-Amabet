import csv
import os

from flask import Flask, render_template, request
from models import *

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    with open("competitions.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            # Check if the row has at least two values
            if len(row) >= 2:
                live_score_id, name = row
                competition = Competition(live_score_id=live_score_id, name=name)
                db.session.add(competition)
        db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        main()