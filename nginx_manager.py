import os
from typing import List, Tuple
from constants import *
from exceptions import *
from utils import run_command, test_nginx_config, select_domain


class NginxManager:
    def __init__(self):
        pass  # Skip nginx check in __init__

    def get_version(self) -> str:
        """Get nginx version"""
        returncode, output = run_command(['nginx', '-v'])
        if returncode != 0:
            raise NginxManagerError("Unable to get nginx version")
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
        print("Installing Nginx...")
        returncode, _ = run_command(['sudo', 'apt-get', 'update'])
        if returncode != 0:
            raise NginxManagerError("Unable to update package list")

        returncode, _ = run_command(
            ['sudo', 'apt-get', 'install', '-y', 'nginx'])
        if returncode != 0:
            raise NginxManagerError("Unable to install nginx")

        print("Nginx installed successfully!")

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

    def add_subfolder_reverse_proxy_interactive(self):
        domains = self.get_domains()
        if not domains:
            print("No domains configured. Please add a domain first.")
            return

        domain = select_domain(domains, "add reverse proxy subfolder")
        subfolder = input("Enter subfolder name: ")
        target_url = input("Enter target URL for reverse proxy: ")

        config_content = f"""
location /{subfolder} {{
    proxy_pass {target_url};
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}}
        """

        self._add_subfolder_config(domain, config_content)
        print(f"Successfully added subfolder {subfolder} with reverse proxy.")

    def add_subfolder_static_html_interactive(self):
        domains = self.get_domains()
        if not domains:
            print("No domains configured. Please add a domain first.")
            return

        domain = select_domain(domains, "add static HTML subfolder")
        subfolder = input("Enter subfolder name: ")
        html_path = input("Enter path to static HTML file: ")

        config_content = f"""
location /{subfolder} {{
    alias {html_path};
    index index.html;
}}
        """

        self._add_subfolder_config(domain, config_content)
        print(f"Successfully added subfolder {subfolder} with static HTML.")

    def _add_subfolder_config(self, domain, config_content):
        config_file = os.path.join(NGINX_SITES_AVAILABLE, domain)
        if not os.path.exists(config_file):
            raise NginxManagerError(
                f"Configuration not found for domain {domain}")

        with open(config_file, 'r') as f:
            content = f.read()

        # Thêm cấu hình subfolder vào trước dấu '}'
        new_content = content.rsplit('}', 1)
        new_content = new_content[0] + config_content + '}\n'

        with open(config_file, 'w') as f:
            f.write(new_content)

        self._reload_nginx()

    def _reload_nginx(self):
        run_command(['sudo', 'systemctl', 'reload', 'nginx'])
