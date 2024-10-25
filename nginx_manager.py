import os
from typing import List
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
            raise NginxManagerError("Failed to get nginx version")
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
                raise ConfigurationError("Invalid nginx configuration")

            run_command(['sudo', 'systemctl', 'reload', 'nginx'])

        except OSError as e:
            raise PermissionError(f"Failed to write configuration: {str(e)}")

    def delete_domain(self, domain: str) -> None:
        """Delete domain configuration"""
        available_path = os.path.join(NGINX_SITES_AVAILABLE, domain)
        enabled_path = os.path.join(NGINX_SITES_ENABLED, domain)

        run_command(['sudo', 'rm', enabled_path])
        run_command(['sudo', 'rm', available_path])

        if not test_nginx_config():
            raise ConfigurationError("Invalid nginx configuration")

        run_command(['sudo', 'systemctl', 'reload', 'nginx'])

    def install_ssl(self, domain: str) -> None:
        """Install SSL for domain"""
        returncode, _ = run_command([
            'sudo', 'certbot', '--nginx', '-d', domain
        ])
        if returncode != 0:
            raise NginxManagerError("Failed to install SSL certificate")

    def renew_ssl(self) -> None:
        """Renew all SSL certificates"""
        returncode, _ = run_command(['sudo', 'certbot', 'renew'])
        if returncode != 0:
            raise NginxManagerError("Failed to renew SSL certificates")
        run_command(['sudo', 'systemctl', 'reload', 'nginx'])

    def is_nginx_installed(self) -> bool:
        """Check if nginx is installed"""
        returncode, _ = run_command(['which', 'nginx'])
        return returncode == 0

    def install_nginx(self) -> None:
        """Install nginx"""
        print("Installing Nginx...")
        returncode, _ = run_command(['sudo', 'apt-get', 'update'])
        if returncode != 0:
            raise NginxManagerError("Failed to update package list")

        returncode, _ = run_command(
            ['sudo', 'apt-get', 'install', '-y', 'nginx'])
        if returncode != 0:
            raise NginxManagerError("Failed to install nginx")

        print("Nginx installed successfully!")
