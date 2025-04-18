import sqlite3
import os
from datetime import datetime
from models.task import Task


class Database:
    DB_NAME = 'todo_app.db'

    def __init__(self, db= 'todo_app.db'):
        self.db_name = db
        self.conn = None
        self.initialize()
 
    #initialize data the database connection and create tables if they don't exist.
    def initialize(self):
        self.conn = sqlite3.connect(self.db_name)
        cursor = self.conn.cursor()


        #create users table:
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        username TEXT, 
                        password TEXT, 
                        created_at TIMESPAN DEFAULT CURRENT_TIMESTAMP)''')

        #create users task:
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                       (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       user_id INTEGER, 
                       title TEXT,
                       description TEXT,
                        due_date TEXT,
                       priority INTEGER DEFAULT 0,
                       completed BOOLEAN DEFAULT 0,
                       created_at TIMESPAN DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (user_id) REFERENCES users(id))''')
        
        self.conn.commit()

    def create_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        self.conn.commit()
        return cursor.lastrowid


    def create_task(self, title, description, due_date, priority, completed, user_id):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users ( title, description, due_date, priority, completed, user_id) VALUES (?, ?, ?, ?, ?, ?)", ( title, description, due_date, priority, completed, user_id))
        self.conn.commit()
        return cursor.lastrowid


    def get_user_by_username(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()

    def get_user_by_id(self, id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
        return cursor.fetchone()

    def get_tasks_by_user(self, user_id, completed=None):
        cursor = self.conn.cursor()
        if completed is None:
            cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
        else:
            cursor.execute("SELECT * FROM tasks WHERE user_id = ? AND completed = ?", (user_id, completed))
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        tasks = [dict(zip(columns, row)) for row in rows]
        return tasks


    
    def get_user_by_credentials(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        return cursor.fetchone()


    def add_task(self, task_data: dict):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (title, description, due_date, priority, completed, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            task_data.get("title"),
            task_data.get("description"),
            task_data.get("due_date"),
            task_data.get("priority", 0),
            task_data.get("completed", 0),
            task_data.get("user_id")
        ))
        self.conn.commit()
        return cursor.lastrowid

    @staticmethod
    def delete_task(task_id):
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

    def get_task_by_id(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if row:
            columns = [col[0] for col in cursor.description]
            task_dict = dict(zip(columns, row))
            return Task.from_dict(task_dict)
        return None

    
   
    def update_task(self, task_id, title, description, due_date, priority):
        """
        Update a task in the database.

        Args:
            task_id: The ID of the task to update
            title: New task title
            description: New task description
            due_date: New task due date
            priority: New task priority
        """
        try:
            cursor = self.conn.cursor()
            query = """
                UPDATE tasks 
                SET title = ?, description = ?, due_date = ?, priority = ? 
                WHERE id = ?
            """
            cursor.execute(query, (title, description, due_date, priority, task_id))
            self.conn.commit()
            print(f"Task {task_id} updated successfully in database")
        except sqlite3.Error as e:
            print(f"Database error while updating task {task_id}: {e}")
            self.conn.rollback()

    def update_task_completion(self, task_id, completed):
        with self.conn:
            self.conn.execute(
                "UPDATE tasks SET completed = ? WHERE id = ?", (int(completed), task_id)
            )


    def close(self):
        # close the database connection
        if self.conn:
            self.conn.close()


        # user opirations
        

    