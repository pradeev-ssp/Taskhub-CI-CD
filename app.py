import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = 'taskhub_secret_key_for_flash_messages'

# Resolve paths dynamically relative to app.py location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'tasks.db')

def get_db_connection():
    """Establish a connection to the SQLite database with Row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create the database directory and tasks table if they do not exist."""
    # Ensure the database directory exists
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        print(f"Created database directory at {DB_DIR}")

    # Create table
    conn = get_db_connection()
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        conn.close()

# --- Reusable Database Operations ---

def get_all_tasks():
    """Retrieve all tasks from the database sorted by creation date (newest first)."""
    conn = get_db_connection()
    try:
        tasks = conn.execute('SELECT * FROM tasks ORDER BY created_at DESC').fetchall()
        return tasks
    except sqlite3.Error as e:
        app.logger.error(f"Error fetching tasks: {e}")
        return []
    finally:
        conn.close()

def get_task_by_id(task_id):
    """Retrieve a single task by its ID."""
    conn = get_db_connection()
    try:
        task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
        return task
    except sqlite3.Error as e:
        app.logger.error(f"Error fetching task {task_id}: {e}")
        return None
    finally:
        conn.close()

def get_task_stats():
    """Retrieve counts for total, completed, and pending tasks."""
    conn = get_db_connection()
    stats = {'total': 0, 'completed': 0, 'pending': 0}
    try:
        # Total tasks
        stats['total'] = conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
        # Completed tasks
        stats['completed'] = conn.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Completed'").fetchone()[0]
        # Pending tasks
        stats['pending'] = conn.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Pending'").fetchone()[0]
    except sqlite3.Error as e:
        app.logger.error(f"Error fetching task statistics: {e}")
    finally:
        conn.close()
    return stats

def create_task(title, description):
    """Insert a new task into the database."""
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)',
            (title, description, 'Pending')
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        app.logger.error(f"Error creating task: {e}")
        return False
    finally:
        conn.close()

def update_task_status(task_id, status):
    """Update the status of a specific task."""
    if status not in ['Pending', 'Completed']:
        return False
    
    conn = get_db_connection()
    try:
        conn.execute('UPDATE tasks SET status = ? WHERE id = ?', (status, task_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        app.logger.error(f"Error updating task status: {e}")
        return False
    finally:
        conn.close()

def delete_task(task_id):
    """Delete a task from the database by ID."""
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        app.logger.error(f"Error deleting task: {e}")
        return False
    finally:
        conn.close()


# --- Flask Routes ---

@app.route('/')
def index():
    """Dashboard page showing task statistics and task list."""
    tasks = get_all_tasks()
    stats = get_task_stats()
    return render_template('index.html', tasks=tasks, stats=stats)

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Create Task page and handler."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        if not title:
            flash('Title is required!', 'danger')
            return render_template('create_task.html', title=title, description=description)

        if create_task(title, description):
            flash('Task created successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Failed to create task. Please try again.', 'danger')
            
    return render_template('create_task.html')

@app.route('/update_status/<int:task_id>', methods=['POST'])
def update_status(task_id):
    """Toggle or set task status between Pending and Completed."""
    task = get_task_by_id(task_id)
    if not task:
        flash('Task not found.', 'danger')
        return redirect(url_for('index'))

    # Toggle logic: if Pending -> Completed, if Completed -> Pending
    new_status = 'Completed' if task['status'] == 'Pending' else 'Pending'
    
    if update_task_status(task_id, new_status):
        flash(f"Task status updated to '{new_status}'!", 'success')
    else:
        flash('Failed to update task status.', 'danger')

    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    """Delete a specific task."""
    if delete_task(task_id):
        flash('Task deleted successfully!', 'success')
    else:
        flash('Failed to delete task.', 'danger')
        
    return redirect(url_for('index'))

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Docker/Kubernetes/LBs."""
    return jsonify({"status": "UP"}), 200

# Error handlers for professional look & feel
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', tasks=get_all_tasks(), stats=get_task_stats()), 404


if __name__ == '__main__':
    # Initialize the database on startup
    init_db()
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=True)
