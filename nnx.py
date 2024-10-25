#!/usr/bin/env python3
import subprocess
import sys
import os
import shutil


def get_nginx_version():
    if not shutil.which("nginx"):
        return "Nginx is not installed or not in PATH."
    try:
        version_info = subprocess.check_output(
            ['nginx', '-v'], stderr=subprocess.STDOUT).decode()
        return version_info.strip()
    except subprocess.CalledProcessError:
        return "Failed to retrieve Nginx version."


def install_nginx():
    print("Installing Nginx...")
    subprocess.run(['sudo', 'apt-get', 'update'])
    subprocess.run(['sudo', 'apt-get', 'install', '-y', 'nginx'])
    subprocess.run(['sudo', 'systemctl', 'enable', 'nginx'])
    subprocess.run(['sudo', 'systemctl', 'start', 'nginx'])
    version = get_nginx_version()
    print(f"Nginx has been installed: {version}")


def list_domains():
    sites_available = "/etc/nginx/sites-available/"
    domains = [f for f in os.listdir(sites_available) if os.path.isfile(
        os.path.join(sites_available, f))]
    if not domains:
        print("No domains are configured.")
        return
    print("Configured domains:")
    for idx, domain in enumerate(domains):
        print(f"{idx + 1}. {domain}")
    while True:
        choice = input(
            "Select the domain to view (enter number, or 'b' to go back): ")
        if choice.lower() == 'b':
            return
        try:
            domain_idx = int(choice) - 1
            if domain_idx < 0 or domain_idx >= len(domains):
                print("Invalid choice.")
                continue
            domain = domains[domain_idx]
            print(f"Domain: {domain}")
            print("Server block:")
            with open(os.path.join(sites_available, domain), 'r') as f:
                print(f.read())
            return
        except ValueError:
            print("Invalid input. Please enter a number corresponding to the domain.")


def add_domain():
    while True:
        domain = input("Enter domain name (or 'b' to go back): ")
        if domain.lower() == 'b':
            return
        if domain.strip() == '':
            print("Domain name cannot be empty.")
            continue
        break

    while True:
        print("Select configuration type:")
        print("1. Serve static HTML")
        print("2. Reverse Proxy")
        choice = input("Enter choice (1 or 2, or 'b' to go back): ")
        if choice.lower() == 'b':
            return
        if choice == '1':
            while True:
                html_path = input(
                    "Enter the path to the HTML files directory (or 'b' to go back): ")
                if html_path.lower() == 'b':
                    return
                if not os.path.isdir(html_path):
                    print("The path does not exist. Please enter a valid directory.")
                    continue
                break
            # Create server block for static HTML
            server_block = f"""
server {{
    listen 80;
    server_name {domain};

    root {html_path};
    index index.html index.htm;

    location / {{
        try_files $uri $uri/ =404;
    }}
}}
"""
            break
        elif choice == '2':
            while True:
                proxy_url = input(
                    "Enter the URL to reverse proxy (e.g., http://localhost:3000, or 'b' to go back): ")
                if proxy_url.lower() == 'b':
                    return
                if not proxy_url.startswith('http://') and not proxy_url.startswith('https://'):
                    print(
                        "Please enter a valid URL starting with 'http://' or 'https://'.")
                    continue
                break
            # Create server block for reverse proxy
            server_block = f"""
server {{
    listen 80;
    server_name {domain};

    location / {{
        proxy_pass {proxy_url};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
"""
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 'b' to go back.")

    # Write configuration to sites-available
    file_path = f"/etc/nginx/sites-available/{domain}"
    try:
        with open(file_path, 'w') as f:
            f.write(server_block)
    except PermissionError:
        print("Permission denied: Unable to write configuration file. Please run the script with appropriate permissions.")
        return

    # Create symbolic link in sites-enabled
    subprocess.run(['sudo', 'ln', '-s', file_path,
                   f"/etc/nginx/sites-enabled/"])

    # Test Nginx configuration
    result = subprocess.run(['sudo', 'nginx', '-t'])
    if result.returncode == 0:
        subprocess.run(['sudo', 'systemctl', 'reload', 'nginx'])
        print(f"Domain {domain} has been added successfully.")
    else:
        print("There is an error in the Nginx configuration.")


def delete_domain():
    while True:
        sites_available = "/etc/nginx/sites-available/"
        domains = [f for f in os.listdir(sites_available) if os.path.isfile(
            os.path.join(sites_available, f))]
        if not domains:
            print("No domains to delete.")
            return
        print("Configured domains:")
        for idx, domain in enumerate(domains):
            print(f"{idx + 1}. {domain}")
        choice = input(
            "Select the domain to delete (enter number, or 'b' to go back): ")
        if choice.lower() == 'b':
            return
        try:
            domain_idx = int(choice) - 1
            if domain_idx < 0 or domain_idx >= len(domains):
                print("Invalid choice.")
                continue
            domain = domains[domain_idx]
            confirm = input(
                f"Are you sure you want to delete the domain '{domain}'? (y/n): ")
            if confirm.lower() != 'y':
                print("Operation cancelled.")
                return
            # Remove symbolic link from sites-enabled
            subprocess.run(
                ['sudo', 'rm', f"/etc/nginx/sites-enabled/{domain}"])
            # Remove configuration file from sites-available
            subprocess.run(
                ['sudo', 'rm', f"/etc/nginx/sites-available/{domain}"])
            # Test Nginx configuration
            result = subprocess.run(['sudo', 'nginx', '-t'])
            if result.returncode == 0:
                subprocess.run(['sudo', 'systemctl', 'reload', 'nginx'])
                print(f"Domain {domain} has been deleted successfully.")
            else:
                print("There is an error in the Nginx configuration.")
            return
        except ValueError:
            print("Invalid input. Please enter a number corresponding to the domain.")


def install_ssl():
    while True:
        # List domains in sites-available
        sites_available = "/etc/nginx/sites-available/"
        domains = [f for f in os.listdir(sites_available) if os.path.isfile(
            os.path.join(sites_available, f))]
        if not domains:
            print("No domains to install SSL.")
            return
        print("Available domains:")
        for idx, domain in enumerate(domains):
            print(f"{idx + 1}. {domain}")
        choice = input(
            "Select the domain to install SSL (enter number, or 'b' to go back): ")
        if choice.lower() == 'b':
            return
        try:
            domain_idx = int(choice) - 1
            if domain_idx < 0 or domain_idx >= len(domains):
                print("Invalid choice.")
                continue
            domain = domains[domain_idx]
            # Install Certbot and configure SSL
            print("Installing Certbot...")
            subprocess.run(['sudo', 'apt-get', 'install', '-y',
                           'certbot', 'python3-certbot-nginx'])
            subprocess.run(['sudo', 'certbot', '--nginx', '-d', domain])
            return
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def renew_ssl():
    print("Renewing SSL certificates...")
    subprocess.run(['sudo', 'certbot', 'renew'])
    subprocess.run(['sudo', 'systemctl', 'reload', 'nginx'])
    print("SSL certificates have been renewed.")


def add_subfolder():
    sites_available = "/etc/nginx/sites-available/"
    domains = [f for f in os.listdir(sites_available) if os.path.isfile(
        os.path.join(sites_available, f))]
    if not domains:
        print("No domains are configured.")
        return

    print("Configured domains:")
    for idx, domain in enumerate(domains):
        print(f"{idx + 1}. {domain}")

    while True:
        choice = input(
            "Select the domain to add a subfolder (enter number, or 'b' to go back): ")
        if choice.lower() == 'b':
            return
        try:
            domain_idx = int(choice) - 1
            if domain_idx < 0 or domain_idx >= len(domains):
                print("Invalid choice.")
                continue
            domain = domains[domain_idx]
            break
        except ValueError:
            print("Invalid input. Please enter a number corresponding to the domain.")

    subfolder = input("Enter the subfolder name (e.g., blog): ")
    while True:
        html_path = input(
            "Enter the path to the HTML files directory for the subfolder (or 'b' to go back): ")
        if html_path.lower() == 'b':
            return
        if not os.path.isdir(html_path):
            print("The path does not exist. Please enter a valid directory.")
            continue
        break

    # Read current configuration
    config_path = f"/etc/nginx/sites-available/{domain}"
    with open(config_path, 'r') as f:
        config = f.read()

    # Add configuration for subfolder
    subfolder_config = f"""
    location /{subfolder} {{
        alias {html_path};
        index index.html index.htm;
        try_files $uri $uri/ =404;
    }}
    """

    # Insert subfolder configuration into server block
    updated_config = config.replace(
        "server {", f"server {{\n{subfolder_config}")

    # Write new configuration
    try:
        with open(config_path, 'w') as f:
            f.write(updated_config)
    except PermissionError:
        print("Permission denied: Unable to write configuration file. Please run the script with appropriate permissions.")
        return

    # Test Nginx configuration
    result = subprocess.run(['sudo', 'nginx', '-t'])
    if result.returncode == 0:
        subprocess.run(['sudo', 'systemctl', 'reload', 'nginx'])
        print(
            f"Successfully added subfolder '{subfolder}' for domain {domain}.")
    else:
        print("There is an error in the Nginx configuration.")


def main():
    while True:
        print("\n=== Nginx CLI Management ===")
        version = get_nginx_version()
        print(f"Current Nginx version: {version}\n")
        print("Please select an option:")
        print("1. Install Nginx")
        print("2. List domains")
        print("3. Add domain")
        print("4. Delete domain")
        print("5. Install SSL for domain")
        print("6. Renew SSL certificates")
        print("7. Add subfolder for domain")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            install_nginx()
        elif choice == '2':
            list_domains()
        elif choice == '3':
            add_domain()
        elif choice == '4':
            delete_domain()
        elif choice == '5':
            install_ssl()
        elif choice == '6':
            renew_ssl()
        elif choice == '7':
            add_subfolder()
        elif choice == '8':
            print("Exiting the program.")
            sys.exit()
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
