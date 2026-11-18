import platform
import sys
import sqlite3
import random
from flask import Flask, render_template, jsonify
from contextlib import closing
import os
from visualizer import generate_collatz_image

app = Flask(__name__)

print("Working directory:", os.getcwd())
print("Flask root path:", app.root_path)
print("Template folder:", app.template_folder)
print("Templates exist:", os.path.exists(
    os.path.join(app.root_path, 'templates', 'index.html')
))

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "collatz.db")

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database table
with closing(get_db()) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS collatz_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            starting_number INTEGER,
            iterations INTEGER,
            max_value INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play', methods=['POST'])
def play():
    # Generate random starting number
    start = random.randint(1, 1000000)
    original = start

    sequence = []
    max_value = start

    # Calculate Collatz sequence
    while start != 1:

        sequence.append(start)

        if start % 2 == 0:
            start //= 2
        else:
            start = (3 * start) + 1

        max_value = max(max_value, start)

    sequence.append(1)

    iterations = len(sequence) - 1
    
    image_folder = os.path.join(app.root_path, 'static', 'images')
    image_url = generate_collatz_image(sequence, original, max_value, image_folder)
    # Save result and retrieve leaderboard
    with closing(get_db()) as conn:
        with conn:
            conn.execute("""
                INSERT INTO collatz_records
                (starting_number, iterations, max_value)
                VALUES (?, ?, ?)
            """, (original, iterations, max_value))

            leaderboard = conn.execute("""
                SELECT starting_number, iterations, max_value, created_at
                FROM collatz_records
                ORDER BY iterations DESC, id ASC
                LIMIT 10
            """).fetchall()

    return jsonify({
        "starting_number": original,
        "sequence": sequence,
        "iterations": iterations,
        "max_value": max_value,
        "image_url": image_url,
        "leaderboard": [dict(row) for row in leaderboard]
    })

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():

    with closing(get_db()) as conn:
        leaderboard = conn.execute("""
            SELECT starting_number, iterations, max_value, created_at
            FROM collatz_records
            ORDER BY iterations DESC, id ASC
            LIMIT 10
        """).fetchall()

    return jsonify({
        "leaderboard": [dict(row) for row in leaderboard]
    })

@app.route('/system_info')
def system_info():
    conn = sqlite3.connect(DATABASE)

    info = {
        "python": platform.python_implementation(),
        "version": platform.python_version(),
        "database": DATABASE,
        "sqlite": sqlite3.sqlite_version,
        "status": "CONNECTED"
    }

    conn.close()

    return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True, port=5001, threaded=True)