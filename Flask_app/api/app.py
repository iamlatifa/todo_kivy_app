from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import pooling, Error
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from config import Config
import os

load_dotenv()
print("ENV DB_HOST:", os.getenv('DB_HOST'))

app = Flask(__name__)

# MySQL connection pooling setup

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'pool_name': "mypool",
    'pool_size': 15,
    'use_pure': True 
}

# Connection Pool initialization
db_pool = pooling.MySQLConnectionPool(**DB_CONFIG)

if app.debug:
    print("Connecting to DB as:", Config.DB_USER)
    print("Using DB config:", DB_CONFIG)



def get_db_connection():
    try:
        return db_pool.get_connection()
    except Error as e:
        print(f"MySQL connection pool error: {e}")
        return None

def initialize_db():
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            # Ensure the database and tables are created once
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255),
                email VARCHAR(255),
                password VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                title VARCHAR(255),
                description TEXT,
                due_date VARCHAR(255),
                priority VARCHAR(255),
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )''')

            conn.commit()
            conn.close()
    except Error as e:
        print(f"DB Initialization error: {e}")

@app.before_request
def init_once():
    initialize_db()

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm = data.get('confirm_password')

    if not all([username, email, password, confirm]):
        return jsonify({'error': 'All fields required'}), 400
    if password != confirm:
        return jsonify({'error': 'Passwords do not match'}), 400

    hashed_password = generate_password_hash(password)
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'DB connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Username or email exists'}), 409

    try:
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                       (username, email, hashed_password))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': user_id, 'username': username}), 201
    except Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'DB connection failed'}), 503

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    user.pop('password')
    return jsonify(user), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, created_at FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()

    return jsonify(user or {'error': 'User not found'}), 200 if user else 404

@app.route("/api/tasks/<int:user_id>", methods=["GET"])
def get_tasks(user_id):
    user_id = request.args.get("user_id", type=int)
    completed_str = request.args.get("completed", default=None)

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if completed_str is not None:
        completed = 1 if completed_str.lower() == "true" else 0
        cursor.execute(
            "SELECT * FROM tasks WHERE user_id = %s AND completed = %s",
            (user_id, completed),
        )
    else:
        cursor.execute("SELECT * FROM tasks WHERE user_id = %s", (user_id,))

    tasks = cursor.fetchall()
    conn.close()
    return jsonify(tasks), 200



@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    required_fields = ['user_id', 'title']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'User ID and title required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(""" 
        INSERT INTO tasks (user_id, title, description, due_date, priority, completed)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data['user_id'], data['title'], data.get('description'),
        data.get('due_date'), data.get('priority', 'Low'), data.get('completed', 0)
    ))

    conn.commit()
    task_id = cursor.lastrowid
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    conn.close()

    return jsonify(task), 201



@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if task exists
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    updates, params = [], []
    for field in ['title', 'description', 'due_date', 'priority', 'completed']:
        if field in data:
            updates.append(f"{field} = %s")
            params.append(data[field])

    if not updates:
        conn.close()
        return jsonify({'error': 'No fields to update'}), 400

    params.append(task_id)
    cursor.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = %s", params)
    conn.commit()

    # Return updated task
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    updated_task = cursor.fetchone()
    conn.close()
    return jsonify(updated_task), 200

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task deleted'}), 200

@app.route('/api/tasks/completion/<int:task_id>', methods=['PATCH'])
def update_task_completion(task_id):
    completed = request.json.get('completed')
    if completed is None:
        return jsonify({'error': 'Completed status required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    cursor.execute("UPDATE tasks SET completed = %s WHERE id = %s", (completed, task_id))
    conn.commit()
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    conn.close()
    return jsonify(task), 200

if __name__ == '__main__':
    app.run(debug=True)