import os
from typing import List, Tuple
from constants import *
from exceptions import *
from utils import run_command, test_nginx_config, select_domain


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

    def list_domains(self):
        domains = self.get_domains()
        if not domains:
            print("No domains configured")
        else:
            for idx, domain in enumerate(domains, 1):
                print(f"{idx}. {domain}")

    def add_domain_interactive(self):
        domain = input("Enter domain name: ")
        config_type = input("Configuration type (static/proxy): ")
        path = input("Enter path (HTML directory or proxy URL): ")
        self.add_domain(domain, config_type, path)
        print(f"Added domain {domain}")

    def delete_domain_interactive(self):
        domains = self.get_domains()
        if not domains:
            print("No domains configured. Nothing to delete.")
            return

        domain = select_domain(domains, "delete")
        confirmation = input(
            f"Are you sure you want to delete {domain}? (y/n): ")
        if confirmation.lower() == 'y':
            self.delete_domain(domain)
            print(f"Deleted domain {domain}")
        else:
            print("Deletion cancelled.")

    def install_ssl_interactive(self):
        domains = self.get_domains()
        if not domains:
            print("No domains configured. Please add a domain first.")
            return

        domain = select_domain(domains, "install SSL")
        self.install_ssl(domain)
        print(f"Installed SSL for domain {domain}")

    def renew_ssl_interactive(self):
        confirmation = input(
            "Are you sure you want to renew SSL certificates for all domains? (y/n): ")
        if confirmation.lower() == 'y':
            self.renew_ssl()
            print("Renewed SSL certificates for all domains")
        else:
            print("SSL renewal cancelled.")

    def add_subfolder_interactive(self):
        domains = self.get_domains()
        if not domains:
            print("No domains configured. Please add a domain first.")
            return

        domain = select_domain(domains, "add a subfolder")
        subfolder = input("Enter subfolder name: ")
        html_path = input("Enter path to HTML directory: ")
        self.add_subfolder(domain, subfolder, html_path)
        print(f"Added subfolder {subfolder} for domain {domain}")

    def view_domain_config_interactive(self):
        domains = self.get_domains()
        if not domains:
            print("No domains configured. Nothing to view.")
            return

        domain = select_domain(domains, "view configuration")
        config = self.view_domain_config(domain)
        print(f"Configuration for domain {domain}:")
        print(config)
