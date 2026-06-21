import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import httpx
from fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()  
 
# Initialize FastMCP server
mcp = FastMCP("airflow-monitor")
 
# Airflow configuration from environment variables
AIRFLOW_URL = os.getenv("AIRFLOW_URL")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")
 
# Create HTTP client with basic auth
def get_client():
    return httpx.Client(
        base_url=AIRFLOW_URL,
        auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
        timeout=30.0
    )
 
@mcp.tool()
def list_active_dags() -> dict:
    """
    List all active DAGs in Airflow.
    Returns DAG ID, description, owner, and schedule interval.
    """
    try:
        with get_client() as client:
            response = client.get("/api/v1/dags?limit=100&only_active=True")
            response.raise_for_status()
            data = response.json()
            
            dags = []
            for dag in data.get("dags", []):
                dags.append({
                    "dag_id": dag.get("dag_id"),
                    "description": dag.get("description", "No description"),
                    "owner": dag.get("owner", "Unknown"),
                    "schedule_interval": dag.get("schedule_interval"),
                    "is_paused": dag.get("is_paused", False),
                    "next_dagrun": dag.get("next_dagrun"),
                })
            
            return {
                "status": "success",
                "count": len(dags),
                "dags": dags
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list DAGs: {str(e)}"
        }
 
@mcp.tool()
def get_recent_runs(dag_id: str, limit: int = 10) -> dict:
    """
    Get recent runs for a specific DAG.
    Returns run status, start/end times, and duration.
    
    Args:
        dag_id: The ID of the DAG
        limit: Number of recent runs to fetch (default: 10)
    """
    try:
        with get_client() as client:
            response = client.get(
                f"/api/v1/dags/{dag_id}/dagRuns",
                params={"limit": limit, "order_by": "-execution_date"}
            )
            response.raise_for_status()
            data = response.json()
            
            runs = []
            for run in data.get("dag_runs", []):
                start_time = datetime.fromisoformat(run.get("start_date", "").replace("Z", "+00:00")) if run.get("start_date") else None
                end_time = datetime.fromisoformat(run.get("end_date", "").replace("Z", "+00:00")) if run.get("end_date") else None
                
                duration = None
                if start_time and end_time:
                    duration = str(end_time - start_time)
                
                runs.append({
                    "execution_date": run.get("execution_date"),
                    "state": run.get("state"),
                    "start_date": run.get("start_date"),
                    "end_date": run.get("end_date"),
                    "duration": duration,
                    "data_interval_start": run.get("data_interval_start"),
                    "data_interval_end": run.get("data_interval_end"),
                })
            
            return {
                "status": "success",
                "dag_id": dag_id,
                "count": len(runs),
                "runs": runs
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get runs for {dag_id}: {str(e)}"
        }
 
@mcp.tool()
def get_execution_history(dag_id: str, days: int = 7) -> dict:
    """
    Get execution history summary for a DAG over the past N days.
    Returns success/failure counts and average duration.
    
    Args:
        dag_id: The ID of the DAG
        days: Number of days to look back (default: 7)
    """
    try:
        with get_client() as client:
            response = client.get(
                f"/api/v1/dags/{dag_id}/dagRuns",
                params={"limit": 100, "order_by": "-execution_date"}
            )
            response.raise_for_status()
            data = response.json()
            
            runs = data.get("dag_runs", [])
            cutoff_date = datetime.now(datetime.now().astimezone().tzinfo) - timedelta(days=days)
            
            # Filter runs within the date range
            recent_runs = []
            for run in runs:
                exec_date = datetime.fromisoformat(run.get("execution_date", "").replace("Z", "+00:00"))
                if exec_date >= cutoff_date:
                    recent_runs.append(run)
            
            # Calculate statistics
            success_count = sum(1 for r in recent_runs if r.get("state") == "success")
            failed_count = sum(1 for r in recent_runs if r.get("state") == "failed")
            running_count = sum(1 for r in recent_runs if r.get("state") == "running")
            
            # Calculate average duration
            durations = []
            for run in recent_runs:
                start = run.get("start_date")
                end = run.get("end_date")
                if start and end:
                    start_time = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    end_time = datetime.fromisoformat(end.replace("Z", "+00:00"))
                    durations.append((end_time - start_time).total_seconds())
            
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            return {
                "status": "success",
                "dag_id": dag_id,
                "period_days": days,
                "total_runs": len(recent_runs),
                "success_count": success_count,
                "failed_count": failed_count,
                "running_count": running_count,
                "success_rate": f"{(success_count / len(recent_runs) * 100):.1f}%" if recent_runs else "N/A",
                "avg_duration_seconds": round(avg_duration, 2),
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get execution history for {dag_id}: {str(e)}"
        }
 
# Run MCP Server via stdio transport
if __name__ == "__main__":
    mcp.run()