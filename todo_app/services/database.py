import mysql.connector
from datetime import datetime
from models.task import Task


class Database:
    def __init__(self, host='localhost', user='root', password='123AZE', database='todo_app'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.initialize()

    def initialize(self):
        # First connect without specifying database to create it if needed
        temp_conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password
        )
        temp_cursor = temp_conn.cursor()

        # Create database if it doesn't exist
        temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
        temp_conn.close()

        # Connect to the newly created database
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        cursor = self.conn.cursor()

        # Create users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                          (id INT AUTO_INCREMENT PRIMARY KEY, 
                          username VARCHAR(255), 
                          password VARCHAR(255), 
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        # Create tasks table
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                          (id INT AUTO_INCREMENT PRIMARY KEY, 
                          user_id INT, 
                          title VARCHAR(255),
                          description TEXT,
                          due_date VARCHAR(255),
                          priority INT DEFAULT 0,
                          completed BOOLEAN DEFAULT 0,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY (user_id) REFERENCES users(id))''')

        self.conn.commit()

    def create_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        self.conn.commit()
        return cursor.lastrowid

    def get_user_by_credentials(self, username, password):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        return cursor.fetchone()

    def get_user_by_username(self, username):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()

    def get_user_by_id(self, id):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        return cursor.fetchone()

    def create_task(self, title, description, due_date, priority, completed, user_id):
        cursor = self.conn.cursor()
        cursor.execute("""INSERT INTO tasks (title, description, due_date, priority, completed, user_id)
                          VALUES (%s, %s, %s, %s, %s, %s)""",
                       (title, description, due_date, priority, completed, user_id))
        self.conn.commit()
        return cursor.lastrowid

    def get_tasks_by_user(self, user_id, completed=None):
        cursor = self.conn.cursor(dictionary=True)
        if completed is None:
            cursor.execute("SELECT * FROM tasks WHERE user_id = %s", (user_id,))
        else:
            cursor.execute("SELECT * FROM tasks WHERE user_id = %s AND completed = %s", (user_id, completed))
        return cursor.fetchall()

    def add_task(self, task_data: dict):
        cursor = self.conn.cursor()
        cursor.execute("""INSERT INTO tasks (title, description, due_date, priority, completed, user_id)
                          VALUES (%s, %s, %s, %s, %s, %s)""",
                       (
                           task_data.get("title"),
                           task_data.get("description"),
                           task_data.get("due_date"),
                           task_data.get("priority", 0),
                           task_data.get("completed", 0),
                           task_data.get("user_id")
                       ))
        self.conn.commit()
        return cursor.lastrowid

    def delete_task(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        self.conn.commit()

    def get_task_by_id(self, task_id):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        task_dict = cursor.fetchone()
        if task_dict:
            return Task.from_dict(task_dict)
        return None

    def update_task(self, task_id, title, description, due_date, priority):
        try:
            cursor = self.conn.cursor()
            query = """UPDATE tasks 
                       SET title = %s, description = %s, due_date = %s, priority = %s 
                       WHERE id = %s"""
            cursor.execute(query, (title, description, due_date, priority, task_id))
            self.conn.commit()
            print(f"Task {task_id} updated successfully in database")
        except mysql.connector.Error as e:
            print(f"Database error while updating task {task_id}: {e}")
            self.conn.rollback()

    def update_task_completion(self, task_id, completed):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE tasks SET completed = %s WHERE id = %s", (int(completed), task_id))
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
