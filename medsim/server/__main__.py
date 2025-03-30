import os
import subprocess
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Frontend-Server")

# Get working directory using Path for better cross-platform support
WORKING_DIR = Path(os.getcwd())

# Constants with proper path joining
FRONTEND_SCRIPT_PATH = WORKING_DIR / "Simulacra" / "environment" / "frontend_server"
FRONTEND_SCRIPT_FILE = "manage.py"
DEFAULT_PORT = 8000

def run_frontend_server(port=None):
    """
    Run the Django frontend server with the specified port.
    
    Args:
        port (int, optional): Port number to run the server on. Defaults to DEFAULT_PORT.
    
    Returns:
        bool: True if server started successfully, False otherwise.
    """
    port = port or DEFAULT_PORT
    logger.info(f"Running frontend server on port {port}")
    
    # Check if the frontend path exists
    if not FRONTEND_SCRIPT_PATH.exists():
        logger.error(f"Frontend path does not exist: {FRONTEND_SCRIPT_PATH}")
        logger.info(f"Current working directory: {WORKING_DIR}")
        logger.info("Available directories:")
        
        # List available directories for debugging
        simulacra_dir = WORKING_DIR / "Simulacra"
        if simulacra_dir.exists():
            logger.info(f"Contents of {simulacra_dir}:")
            for item in simulacra_dir.iterdir():
                logger.info(f"  - {item.name}")
        else:
            logger.error(f"Simulacra directory not found at {simulacra_dir}")
            
        return False
    
    # Store original directory to restore later
    original_dir = os.getcwd()
    
    try:
        # Change to the frontend script directory
        os.chdir(FRONTEND_SCRIPT_PATH)
        logger.info(f"Changed directory to {FRONTEND_SCRIPT_PATH}")
        
        # Form the command with proper path handling
        manage_py_path = FRONTEND_SCRIPT_PATH / FRONTEND_SCRIPT_FILE
        
        # Check if manage.py exists
        if not manage_py_path.exists():
            logger.error(f"manage.py not found at {manage_py_path}")
            return False
            
        # Form command with proper string representation of path
        command = f'python3 "{manage_py_path}" runserver {port}'
        logger.info(f"Executing command: {command}")
        
        # Run the command with proper error handling
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True
        )
        
        # Log the output
        if result.stdout.strip():
            logger.info(f"Server output:\n{result.stdout}")
        
        if result.stderr.strip():
            if "Error" in result.stderr or "error" in result.stderr:
                logger.error(f"Server errors:\n{result.stderr}")
            else:
                # Django often outputs to stderr even for non-errors
                logger.info(f"Server messages:\n{result.stderr}")
        
        # Check return code
        if result.returncode != 0:
            logger.error(f"Failed to run server with return code {result.returncode}")
            return False
        else:
            logger.info(f"Server started successfully on port {port}")
            logger.info(f"Server URL: http://127.0.0.1:{port}/")
            return True
            
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return False
    finally:
        # Restore original directory regardless of success/failure
        os.chdir(original_dir)

def main():
    """
    Main function to handle command line arguments and run the server.
    """
    # Parse command line arguments for port if provided
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            logger.info(f"Using port {port} from command line")
        except ValueError:
            logger.warning(f"Invalid port specified: {sys.argv[1]}. Using default port {DEFAULT_PORT}")
            port = DEFAULT_PORT
    else:
        port = DEFAULT_PORT
    
    # Run the server
    success = run_frontend_server(port=port)
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())