import subprocess
import shutil
from typing import Tuple

def run_command(command: list) -> Tuple[int, str]:
    """Run a shell command and return returncode and output"""
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        return result.returncode, result.stdout
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stderr

def is_nginx_installed() -> bool:
    """Check if nginx is installed"""
    return shutil.which("nginx") is not None

def test_nginx_config() -> bool:
    """Test nginx configuration"""
    returncode, _ = run_command(['sudo', 'nginx', '-t'])
    return returncode == 0
