import os
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'db'),
        database=os.environ.get('DB_NAME', 'appdb'),
        user=os.environ.get('DB_USER', 'appuser'),
        password=os.environ.get('DB_PASS', 'apppass')
    )

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            text VARCHAR(200) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def home():
    return "Flask + Postgres is running!"

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/messages')
def get_messages():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, text, created_at FROM messages ORDER BY id DESC')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"id": r[0], "text": r[1], "time": str(r[2])} for r in rows])

@app.route('/messages/add/<text>')
def add_message(text):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO messages (text) VALUES (%s)', (text,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"added": text}), 201

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
