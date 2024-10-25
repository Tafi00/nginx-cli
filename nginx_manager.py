from constants import *
from exceptions import *
from utils import run_command, select_domain


class NginxManager:
    def __init__(self):
        pass  # Bỏ kiểm tra nginx trong __init__

    def get_version(self) -> str:
        """Get nginx version"""
        returncode, output = run_command(['nginx', '-v'])
        if returncode != 0:
            raise NginxManagerError("Không thể lấy phiên bản nginx")
        return output.strip()

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
