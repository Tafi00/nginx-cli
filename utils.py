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


def display_menu(nginx_installed):
    print("\n=== Nginx Management CLI ===")
    if not nginx_installed:
        print("Nginx is not installed!")
        print("1. Install Nginx")
        print("2. Exit")
    else:
        print("1. List domains")
        print("2. Add domain")
        print("3. Delete domain")
        print("4. Install SSL")
        print("5. Renew SSL")
        print("6. Add subfolder")
        print("7. View domain configuration")
        print("8. Exit")


def get_user_choice():
    return input("Enter your choice: ")


def select_domain(domains, action):
    print("Available domains:")
    for idx, domain in enumerate(domains, 1):
        print(f"{idx}. {domain}")

    while True:
        try:
            domain_choice = int(
                input(f"Enter the number of the domain to {action}: "))
            if 1 <= domain_choice <= len(domains):
                return domains[domain_choice - 1]
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
