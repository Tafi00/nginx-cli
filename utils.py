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
    if not nginx_installed:
        print("1. Cài đặt Nginx")
        print("2. Thoát")
    else:
        print("1. Liệt kê các domain")
        print("2. Thêm domain mới")
        print("3. Xóa domain")
        print("4. Cài đặt SSL")
        print("5. Gia hạn SSL")
        print("6. Thêm subfolder")
        print("7. Xem cấu hình domain")
        print("8. Thoát")


def get_user_choice():
    return input("Nhập lựa chọn của bạn: ")


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
