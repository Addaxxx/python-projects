from fastapi import FastAPI, HTTPException
import uvicorn
import psutil
import logging
import os


def cpu_usage():
    """
    Get current CPU usage percentage.

    Returns:
        float: CPU usage percentage.
    """
    return psutil.cpu_percent(interval=1)


def ram_usage():
    """
    Get current RAM usage percentage.

    Returns:
        float: RAM usage percentage.
    """
    return psutil.virtual_memory().percent


def disk_usage(disk_path):
    """
    Get current disk usage percentage for a given path.

    Args:
        disk_path (str): Path to check disk usage.

    Returns:
        float: Disk usage percentage.
    """
    return psutil.disk_usage(disk_path).percent


app = FastAPI()


@app.get("/health")
def health():
    """
        Health check endpoint to verify that the API is running.

    """
    return {"status": "ok"}


@app.get("/metrics")
def metrics(disk_path='/'):
    """
        Get system metrics for CPU, RAM, and Disk usage.

    Args:
        disk_path (str): Path to check disk usage.

    Raises:
        HTTPException: If there is an error while fetching the metrics,
        an HTTPException with status code 500 is raised.

    Returns:
       dict: A dictionary containing the key:value pairs
       for system metrics (CPU, RAM, Disk usage).
    """
    try:
        system_metrics = {
            'cpu': cpu_usage(),
            'memory': ram_usage(),
            'disk': disk_usage(disk_path)
        }
        logging.info(f"Fetched system metrics: {system_metrics}")
        return system_metrics
    except Exception as e:
        logging.error(f"Error fetching system metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/cpu")
def metrics_cpu():
    """
        Get current CPU usage percentage.

    Raises:
        HTTPException: If there is an error while fetching the CPU usage,
        an HTTPException with status code 500 is raised.

    Returns:
        float: CPU usage percentage.
    """
    try:
        cpu = cpu_usage()
        logging.info(f"Fetched CPU usage: {cpu}%")
        return cpu
    except Exception as e:
        logging.error(f"Error fetching CPU usage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/memory")
def metrics_memory():
    """
        Get current RAM usage percentage.

    Raises:
        HTTPException: If there is an error while fetching the RAM usage,
        an HTTPException with status code 500 is raised.

    Returns:
        float: RAM usage percentage.
    """
    try:
        memory = ram_usage()
        logging.info(f"Fetched RAM usage: {memory}%")
        return memory
    except Exception as e:
        logging.error(f"Error fetching RAM usage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/disk")
def metrics_disk():
    """
    Get current disk usage percentage for the root path.

    Raises:
        HTTPException: If there is an error while fetching the disk usage,
        an HTTPException with status code 500 is raised.

    Returns:
        float: Disk usage percentage for the root path.
    """
    try:
        disk = disk_usage('/')
        logging.info(f"Fetched disk usage for '/': {disk}%")
        return disk
    except Exception as e:
        logging.error(f"Error fetching disk usage for '/': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def main():

    # Build log path relative to the script, not the working directory.
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        filename=os.path.join(log_dir, 'monitoring_api.log'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
