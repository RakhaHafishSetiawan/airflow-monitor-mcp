# Airflow MCP Monitor

A FastMCP-based Model Context Protocol server for **monitoring** Apache Airflow DAGs. Provides read-only real-time access to DAG status, execution history, and performance metrics. Agents using this server cannot modify, trigger, or pause any DAGs.

**Security Note:** This server is intentionally read-only for safe integration with untrusted clients and AI agents.

## Features

- **List Active DAGs**: Query all active DAGs with metadata (description, owner, schedule)
- **Recent Runs**: Fetch recent execution runs for specific DAGs with timing and status
- **Execution History**: Analyze DAG performance over configurable time periods with success rates and average durations
- **Stdio Transport**: Lightweight stdio-based MCP interface for seamless integration with Claude and other MCP clients
- **READ-ONLY Access**: Safe monitoring interface with no write operations—agents can only read DAG status and metrics

## ⚠️ Read-Only Server

This is a **READ-ONLY MCP server**. Agents and clients using this server have **no write access** to Airflow. All tools provide monitoring and analysis capabilities only:

- ✓ Query DAG status and metadata
- ✓ View execution history and performance metrics
- ✓ Monitor recent runs and logs
- ✗ No ability to pause/resume DAGs
- ✗ No ability to trigger DAG runs
- ✗ No ability to modify DAG configurations
- ✗ No ability to clear task states

Safe for integration with untrusted agents and AI models without risk of accidental modifications.

## Requirements

- Python 3.11+
- Apache Airflow instance with API access
- Docker & Docker Compose (for containerized deployment)

## Installation

### Local Setup

```bash
# Clone and navigate to project directory
cd "airflow-monitor-mcp"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the project root:

```env
AIRFLOW_URL=
AIRFLOW_USERNAME=
AIRFLOW_PASSWORD=
```

## MCP Server Demo with Claude Desktop

<img width="1156" height="761" alt="image" src="https://github.com/user-attachments/assets/cf311245-868c-4b98-8d00-59fe66ffef62" />

## Usage

### Local Execution

```bash
python airflow_mcp.py
```

The MCP server will start and communicate via stdin/stdout using the Model Context Protocol.

### Docker Deployment

```bash
docker-compose up -d
```

The containerized MCP server will initialize and be ready to accept stdio connections:
```bash
docker-compose logs -f
```

## API Tools

All tools are **READ-ONLY** monitoring operations:

### list_active_dags()
Returns all active DAGs with metadata.

**Returns:**
- `dag_id`: Unique DAG identifier
- `description`: DAG description
- `owner`: DAG owner
- `schedule_interval`: Schedule interval
- `is_paused`: Pause status
- `next_dagrun`: Next scheduled run time

### get_recent_runs(dag_id, limit=10)
Fetch recent execution runs for a DAG.

**Parameters:**
- `dag_id` (str): Target DAG ID
- `limit` (int): Number of runs to fetch (default: 10)

**Returns:**
- `execution_date`: Run execution timestamp
- `state`: Run state (success/failed/running)
- `start_date`: Run start time
- `end_date`: Run end time
- `duration`: Total execution duration

### get_execution_history(dag_id, days=7)
Get DAG performance metrics over a time period.

**Parameters:**
- `dag_id` (str): Target DAG ID
- `days` (int): Lookback period in days (default: 7)

**Returns:**
- `success_count`: Successful runs
- `failed_count`: Failed runs
- `success_rate`: Success percentage
- `avg_duration_seconds`: Average run duration

## Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `AIRFLOW_URL` | Airflow instance base URL | `http://localhost:8080` |
| `AIRFLOW_USERNAME` | API authentication username | `admin` |
| `AIRFLOW_PASSWORD` | API authentication password | `secure_password` |

## Project Structure

```
Python Scripts/
├── airflow_mcp.py          # Main MCP server application
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── Dockerfile              # Container image definition
├── docker-compose.yml      # Multi-container orchestration
├── .dockerignore           # Docker build exclusions
└── README.md              # This file
```

## Docker Deployment

The application includes Docker support with Python 3.11. See `docker-compose.yml` for configuration options.

## Troubleshooting

**Connection Error**: Verify `AIRFLOW_URL` and credentials in `.env`  
**API 403 Errors**: Ensure Airflow user has API permissions  
**Timeout Issues**: Increase timeout in `get_client()` or check network connectivity

## License

MIT
