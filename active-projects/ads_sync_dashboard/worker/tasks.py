"""
Celery background tasks for executing ads_sync CLI commands.
"""

import sys
from pathlib import Path
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from celery import Celery
from worker.cli_executor import CLIExecutor
from api.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    'ads_sync_dashboard',
    broker=f'redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}',
    backend=f'redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}'
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes
    task_soft_time_limit=570,  # 9.5 minutes
    worker_pool='solo',  # Windows-compatible pool
)

# Initialize CLI executor with settings
executor = CLIExecutor(
    settings.ads_sync_project_path,
    settings.ads_sync_cli_command
)


@celery_app.task(name='execute_cli_command', bind=True)
def execute_cli_command(self, command: str, slug: str, **kwargs) -> dict:
    """
    Celery task to execute ads_sync CLI command.
    
    This function runs as a background job in the Celery worker.
    
    Args:
        command: CLI command to execute (e.g., 'append', 'validate')
        slug: Client slug (e.g., 'priority-roofing')
        **kwargs: Additional command-specific arguments
    
    Returns:
        Dict with stdout, stderr, and exit_code
    
    Raises:
        Exception: If command fails (exit code != 0)
    
    Examples:
        >>> execute_cli_command("validate", "priority-roofing")
        {"stdout": "...", "stderr": "", "exit_code": 0}
        
        >>> execute_cli_command("repair", "priority-roofing", start="2025-09-01", end="2025-09-30")
        {"stdout": "...", "stderr": "", "exit_code": 0}
    """
    logger.info(f"Starting task: {command} for {slug}")
    logger.debug(f"Task kwargs: {kwargs}")
    
    # Validate command
    if not executor.validate_command(command):
        raise ValueError(f"Invalid command: {command}")
    
    # Build arguments list
    args = [slug]
    
    # Add command-specific arguments
    if command == "repair":
        if "start" not in kwargs or "end" not in kwargs:
            raise ValueError("repair command requires 'start' and 'end' arguments")
        args.extend(["--start", kwargs["start"], "--end", kwargs["end"]])
        
    elif command == "report":
        scope = kwargs.get("scope", "LAST-30-DAYS")
        args.extend(["--scope", scope])
    
    # Execute command
    exit_code, stdout, stderr = executor.execute(command, *args)
    
    # Prepare result
    result = {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "command": command,
        "slug": slug,
        "args": kwargs
    }
    
    # Raise exception if command failed
    if exit_code != 0:
        error_msg = f"CLI command '{command}' failed for {slug}: {stderr}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    logger.info(f"Task completed successfully: {command} for {slug}")
    return result


@celery_app.task(name='execute_report_generation', bind=True)
def execute_report_generation(self, slug: str, scope: str = "LAST-30-DAYS") -> dict:
    """
    Celery task to generate a report.
    
    This is a convenience wrapper around execute_cli_command for report generation.
    
    Args:
        slug: Client slug
        scope: Report scope (LIFETIME, LAST-30-DAYS, etc.)
    
    Returns:
        Dict with stdout, stderr, and exit_code
    
    Example:
        >>> execute_report_generation("priority-roofing", "LIFETIME")
        {"stdout": "...", "stderr": "", "exit_code": 0}
    """
    logger.info(f"Generating report for {slug} with scope {scope}")
    return execute_cli_command(self, "report", slug, scope=scope)


@celery_app.task(name='execute_validation', bind=True)
def execute_validation(self, slug: str) -> dict:
    """
    Celery task to validate a client configuration.
    
    This is a convenience wrapper for the validate command.
    
    Args:
        slug: Client slug
    
    Returns:
        Dict with validation results
    
    Example:
        >>> execute_validation("priority-roofing")
        {"stdout": "...", "stderr": "", "exit_code": 0}
    """
    logger.info(f"Validating configuration for {slug}")
    return execute_cli_command(self, "validate", slug)


@celery_app.task(name='execute_append', bind=True)
def execute_append(self, slug: str) -> dict:
    """
    Celery task to perform incremental data append.
    
    This is a convenience wrapper for the append command.
    
    Args:
        slug: Client slug
    
    Returns:
        Dict with append results
    
    Example:
        >>> execute_append("priority-roofing")
        {"stdout": "...", "stderr": "", "exit_code": 0}
    """
    logger.info(f"Executing append for {slug}")
    return execute_cli_command(self, "append", slug)

