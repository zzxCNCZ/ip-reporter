# IP Reporter

A real-time client IP monitoring system consisting of a FastAPI server and a Python client.

## Features

- **Real-time Monitoring**: WebSocket-based connection for instant status updates.
- **Web Dashboard**: Beautiful, modern UI to view connected clients.
- **Client Auto-discovery**: Automatically detects and reports client connection details.
- **Resilient**: Client automatically reconnects on connection loss.

## Project Structure

```
ip-reporter/
├── server/             # Server application
│   ├── main.py         # FastAPI backend
│   └── static/         # Frontend assets
├── client/             # Client application
│   └── client.py       # Client script
├── Dockerfile          # Docker build definition
├── docker-compose.yml  # Docker Compose configuration
├── requirements.txt    # Python dependencies
└── pyproject.toml      # Project configuration
```

## Local Installation

### Prerequisites

- Python 3.12+
- `pdm` or `uv` (recommended)

### Steps

1.  **Clone the repository** (or navigate to directory).
2.  **Install dependencies**:
    ```bash
    # Using uv (Recommended)
    uv pip install -r requirements.txt
    
    # Or using pip
    pip install -r requirements.txt
    ```
3.  **Configure Client**:
    Create a `.env` file in the root directory (optional, defaults allow localhost):
    ```env
    SERVER_URL=ws://localhost:8000/ws/client
    ```

## Usage

### 1. Start Server
```bash
uvicorn server.main:app --host 0.0.0.0 --port 8000
```
Open [http://localhost:8000](http://localhost:8000) to view the dashboard.

### 2. Start Client
Run in a separate terminal:
```bash
python client/client.py
```

## Docker Deployment

### Method 1: Docker Compose (Recommended)

Build and start the container:
```bash
docker-compose up -d --build
```
The dashboard will be available at [http://localhost:8000](http://localhost:8000).

### Method 2: Manual Docker Build

1.  **Build the image**:
    ```bash
    docker build -t ip-reporter .
    ```

2.  **Run Server (Default)**:
    ```bash
    docker run -d -p 8000:8000 --name ip-reporter-server ip-reporter
    ```

3.  **Run Client (Override CMD)**:
    ```bash
    # Note: Use host networking or correct SERVER_URL if running on different machines
    # In this example we link to the server container or use host network
    docker run -d --network="host" --name ip-reporter-client ip-reporter python client/client.py
    ```
    *Or if using Docker Compose, see the `ip-reporter-client` service in `docker-compose.yml`.*

## API / Endpoints

- `GET /`: Dashboard Web Interface.
- `GET /api/clients`: JSON list of connected clients.
- `WS /ws/client/{client_id}`: WebSocket endpoint for clients.
