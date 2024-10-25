import os
from typing import List, Tuple
from constants import *
from exceptions import *
from utils import run_command, test_nginx_config


class NginxManager:
    def __init__(self):
        pass  # Bỏ kiểm tra nginx trong __init__

    def get_version(self) -> str:
        """Get nginx version"""
        returncode, output = run_command(['nginx', '-v'])
        if returncode != 0:
            raise NginxManagerError("Không thể lấy phiên bản nginx")
        return output.strip()

    def get_domains(self) -> List[str]:
        """Get list of configured domains"""
        return [f for f in os.listdir(NGINX_SITES_AVAILABLE)
                if os.path.isfile(os.path.join(NGINX_SITES_AVAILABLE, f))]

    def add_domain(self, domain: str, config_type: str, path: str) -> None:
        """Add new domain configuration"""
        if config_type == "static":
            server_block = STATIC_SERVER_BLOCK.format(
                domain=domain,
                html_path=path
            )
        else:
            server_block = PROXY_SERVER_BLOCK.format(
                domain=domain,
                proxy_url=path
            )

        config_path = os.path.join(NGINX_SITES_AVAILABLE, domain)

        try:
            with open(config_path, 'w') as f:
                f.write(server_block)

            # Create symlink
            target_path = os.path.join(NGINX_SITES_ENABLED, domain)
            run_command(['sudo', 'ln', '-s', config_path, target_path])

            if not test_nginx_config():
                raise ConfigurationError("Cấu hình nginx không hợp lệ")

            run_command(['sudo', 'systemctl', 'reload', 'nginx'])

        except OSError as e:
            raise PermissionError(f"Không thể ghi cấu hình: {str(e)}")

    def delete_domain(self, domain: str) -> None:
        """Delete domain configuration"""
        available_path = os.path.join(NGINX_SITES_AVAILABLE, domain)
        enabled_path = os.path.join(NGINX_SITES_ENABLED, domain)

        run_command(['sudo', 'rm', enabled_path])
        run_command(['sudo', 'rm', available_path])

        if not test_nginx_config():
            raise ConfigurationError("Cấu hình nginx không hợp lệ")

        run_command(['sudo', 'systemctl', 'reload', 'nginx'])

    def install_ssl(self, domain: str) -> None:
        """Install SSL for domain"""
        returncode, _ = run_command([
            'sudo', 'certbot', '--nginx', '-d', domain
        ])
        if returncode != 0:
            raise NginxManagerError("Không thể cài đặt chứng chỉ SSL")

    def renew_ssl(self) -> None:
        """Renew all SSL certificates"""
        returncode, _ = run_command(['sudo', 'certbot', 'renew'])
        if returncode != 0:
            raise NginxManagerError("Không thể gia hạn chứng chỉ SSL")
        run_command(['sudo', 'systemctl', 'reload', 'nginx'])

    def is_nginx_installed(self) -> bool:
        """Check if nginx is installed"""
        returncode, _ = run_command(['which', 'nginx'])
        return returncode == 0

    def install_nginx(self) -> None:
        """Install nginx"""
        print("Đang cài đặt Nginx...")
        returncode, _ = run_command(['sudo', 'apt-get', 'update'])
        if returncode != 0:
            raise NginxManagerError("Không thể cập nhật danh sách gói")

        returncode, _ = run_command(
            ['sudo', 'apt-get', 'install', '-y', 'nginx'])
        if returncode != 0:
            raise NginxManagerError("Không thể cài đặt nginx")

        print("Đã cài đặt Nginx thành công!")

    def add_subfolder(self, domain: str, subfolder: str, html_path: str) -> None:
        """Add subfolder configuration"""
        config_path = os.path.join(NGINX_SITES_AVAILABLE, domain)

        try:
            with open(config_path, 'r') as f:
                config = f.read()

            subfolder_config = SUBFOLDER_CONFIG.format(
                subfolder=subfolder,
                html_path=html_path
            )

            updated_config = config.replace(
                "server {", f"server {{\n{subfolder_config}")

            with open(config_path, 'w') as f:
                f.write(updated_config)

            if not test_nginx_config():
                raise ConfigurationError("Cấu hình nginx không hợp lệ")

            run_command(['sudo', 'systemctl', 'reload', 'nginx'])

        except OSError as e:
            raise PermissionError(f"Không thể ghi cấu hình: {str(e)}")

    def view_domain_config(self, domain: str) -> str:
        """View domain configuration"""
        config_path = os.path.join(NGINX_SITES_AVAILABLE, domain)
        try:
            with open(config_path, 'r') as f:
                return f.read()
        except OSError as e:
            raise NginxManagerError(f"Không thể đọc cấu hình: {str(e)}")
