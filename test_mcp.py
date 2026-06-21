"""
Simple test script to verify Airflow MCP tools work correctly.
Run this locally before integrating with Claude.ai
"""

import os
import sys
from airflow_mcp import list_active_dags, get_recent_runs, get_execution_history
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def test_list_dags():
    print("\n=== Testing list_active_dags() ===")
    result = list_active_dags()
    print(f"Status: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"Found {result.get('count')} active DAGs")
        for dag in result.get('dags', [])[:3]:  # Show first 3
            print(f"  - {dag['dag_id']} (owner: {dag['owner']})")
    else:
        print(f"Error: {result.get('message')}")
    return result.get('status') == 'success'


def test_get_runs(dag_id=None):
    if not dag_id:
        # Get first active DAG
        dags_result = list_active_dags()
        if dags_result.get('dags'):
            dag_id = dags_result['dags'][0]['dag_id']
        else:
            print("No active DAGs found to test get_recent_runs")
            return False
    
    print(f"\n=== Testing get_recent_runs('{dag_id}') ===")
    result = get_recent_runs(dag_id, limit=5)
    print(f"Status: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"Found {result.get('count')} recent runs")
        for run in result.get('runs', [])[:2]:  # Show first 2
            print(f"  - {run['execution_date']}: {run['state']} (duration: {run.get('duration', 'N/A')})")
    else:
        print(f"Error: {result.get('message')}")
    return result.get('status') == 'success'


def test_execution_history(dag_id=None):
    if not dag_id:
        # Get first active DAG
        dags_result = list_active_dags()
        if dags_result.get('dags'):
            dag_id = dags_result['dags'][0]['dag_id']
        else:
            print("No active DAGs found to test get_execution_history")
            return False
    
    print(f"\n=== Testing get_execution_history('{dag_id}', days=7) ===")
    result = get_execution_history(dag_id, days=7)
    print(f"Status: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"Period: {result.get('period_days')} days")
        print(f"Total runs: {result.get('total_runs')}")
        print(f"Success: {result.get('success_count')} / Failed: {result.get('failed_count')}")
        print(f"Success rate: {result.get('success_rate')}")
        print(f"Avg duration: {result.get('avg_duration_seconds')}s")
    else:
        print(f"Error: {result.get('message')}")
    return result.get('status') == 'success'


if __name__ == "__main__":
    print("Airflow MCP Test Suite")
    print("=" * 50)
    
    # Check environment variables
    airflow_url = os.getenv("AIRFLOW_URL")
    if not airflow_url:
        print("ERROR: AIRFLOW_URL not set")
        print("Please set environment variables:")
        print("  export AIRFLOW_URL=http://your-airflow:8080")
        print("  export AIRFLOW_USERNAME=username")
        print("  export AIRFLOW_PASSWORD=password")
        sys.exit(1)
    
    print(f"Airflow URL: {airflow_url}")
    
    # Run tests
    tests = [
        ("List Active DAGs", test_list_dags),
        ("Get Recent Runs", test_get_runs),
        ("Get Execution History", test_execution_history),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} passed")
            else:
                print(f"✗ {test_name} failed")
        except Exception as e:
            print(f"✗ {test_name} error: {e}")
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n✓ All tests passed! MCP is ready to use.")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Check your Airflow connection.")
        sys.exit(1)