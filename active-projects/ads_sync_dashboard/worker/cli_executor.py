"""
Subprocess wrapper for executing ads_sync CLI commands.
"""

import subprocess
from pathlib import Path
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class CLIExecutor:
    """Executes ads_sync CLI commands via subprocess."""
    
    def __init__(self, project_path: str, cli_command: str):
        """
        Initialize CLI executor.
        
        Args:
            project_path: Path to ads_sync project directory
            cli_command: Base command to run CLI (e.g., 'poetry run python ads_sync_cli.py')
        """
        self.project_path = Path(project_path).resolve()
        
        # If cli_command uses "poetry", try to find it with common Windows paths
        if "poetry" in cli_command.lower() and "poetry.exe" not in cli_command.lower():
            import shutil
            poetry_path = shutil.which("poetry")
            if poetry_path:
                self.cli_command = cli_command.replace("poetry", poetry_path, 1)
                logger.info(f"Resolved poetry to: {poetry_path}")
            else:
                # Try common Windows poetry location
                common_poetry = r"C:\Users\james\AppData\Roaming\Python\Python313\Scripts\poetry.exe"
                if Path(common_poetry).exists():
                    self.cli_command = cli_command.replace("poetry", common_poetry, 1)
                    logger.info(f"Using poetry from: {common_poetry}")
                else:
                    self.cli_command = cli_command
                    logger.warning("Could not find poetry executable, using command as-is")
        else:
            self.cli_command = cli_command
        
        if not self.project_path.exists():
            raise ValueError(f"ads_sync project path does not exist: {self.project_path}")
        
        logger.info(f"CLIExecutor initialized with project_path={self.project_path}")
        logger.info(f"CLI command: {self.cli_command}")
    
    def execute(self, command: str, *args) -> Tuple[int, str, str]:
        """
        Execute ads_sync CLI command via subprocess.
        
        Args:
            command: CLI command (e.g., 'append', 'validate')
            *args: Additional command arguments
        
        Returns:
            Tuple of (exit_code, stdout, stderr)
        
        Example:
            >>> executor = CLIExecutor("../ads_sync", "poetry run python ads_sync_cli.py")
            >>> exit_code, stdout, stderr = executor.execute("validate", "priority-roofing")
        """
        # Build full command
        args_str = ' '.join(str(arg) for arg in args)
        full_command = f"{self.cli_command} {command} {args_str}".strip()
        
        logger.info(f"Executing: {full_command}")
        logger.debug(f"Working directory: {self.project_path}")
        
        try:
            # Execute subprocess
            result = subprocess.run(
                full_command,
                shell=True,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            logger.info(f"Command completed with exit code {result.returncode}")
            
            if result.stdout:
                logger.debug(f"STDOUT: {result.stdout[:200]}...")  # Log first 200 chars
            if result.stderr:
                logger.debug(f"STDERR: {result.stderr[:200]}...")
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after 300 seconds"
            logger.error(error_msg)
            return 1, "", error_msg
            
        except Exception as e:
            error_msg = f"Subprocess execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return 1, "", error_msg
    
    def validate_command(self, command: str) -> bool:
        """
        Validate that a command is supported.
        
        Args:
            command: Command name to validate
        
        Returns:
            True if command is valid
        """
        valid_commands = {"init", "append", "validate", "repair", "force-unlock", "report", "discover"}
        return command in valid_commands

