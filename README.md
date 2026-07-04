# TaskHub

TaskHub is a lightweight, responsive, and production-ready task management application built using Python, Flask, and SQLite. The user interface features a custom premium dark-mode theme powered by Bootstrap 5 and custom CSS layouts.

This application is designed specifically as a practice project for DevOps, CI/CD pipelines, Docker containerization, AWS deployments, and Kubernetes orchestration exercises.

---

## Features

- **Dashboard**: Track tasks with automatic metrics calculation (Total Tasks, Completed Tasks, and Pending Tasks) and a responsive table display.
- **Task Management**: Create tasks (title is required, description is optional), toggle status (Pending / Completed), and delete tasks.
- **Health Check Endpoint**: `/health` endpoint returning server status. Suitable for Kubernetes Liveness/Readiness probes and Cloud Load Balancer checks.
- **Sleek Custom UI**: Clean dark-mode layout with custom glassmorphism components, micro-animations, and full responsiveness.
- **SQLite Database**: Lightweight storage, automatically initialized on application startup.

---

## Folder Structure

```text
Taskhub-Code/
├── app.py                   # Main Flask application with database operations & routes
├── requirements.txt         # Project dependencies
├── README.md                # Documentation
├── database/
│   └── tasks.db             # SQLite database file (created automatically on startup)
├── static/
│   └── style.css            # Custom premium styles & variables
└── templates/
    ├── index.html           # Dashboard template
    └── create_task.html     # Create Task form template
```

---

## Installation & Setup

Ensure you have Python 3.x installed on your machine.

### 1. Set Up Virtual Environment (Recommended)
Navigate to the root workspace folder `Taskhub-Code` and run:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
Install the required packages using pip:

```bash
pip install -r requirements.txt
```

---

## Running Locally

To run the application, execute:

```bash
python app.py
```

Upon starting, you will see output confirming that the database has been initialized:
```text
Created database directory at ...\database
Database initialized successfully.
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://<your-ip>:5000
```

Open your browser and navigate to `http://localhost:5000` to access the application.

---

## Health Check Endpoint

To check the application's health status, perform a GET request to the `/health` endpoint:

**Request:**
```bash
curl http://localhost:5000/health
```

**Response (HTTP 200 OK):**
```json
{
  "status": "UP"
}
```

This endpoint is ideal for:
- Docker health checks (`HEALTHCHECK` in Dockerfile)
- Kubernetes Liveness & Readiness Probes (`livenessProbe`, `readinessProbe`)
- AWS Application Load Balancer health checks

---

## Docker Quickstart (Optional)

To containerize the application:

1. Create a `Dockerfile`:
   ```dockerfile
   FROM python:3.12-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 5000
   CMD ["python", "app.py"]
   ```

2. Build the Docker image:
   ```bash
   docker build -t taskhub:latest .
   ```

3. Run the container:
   ```bash
   docker run -d -p 5000:5000 --name taskhub-app taskhub:latest
   ```


git add . ":(exclude)venv"