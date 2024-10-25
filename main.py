from nginx_manager import NginxManager
from exceptions import NginxManagerError


def main():
    try:
        manager = NginxManager()
        nginx_installed = manager.is_nginx_installed()

        while True:
            print("\n=== Nginx Management CLI ===")

            if not nginx_installed:
                print("Nginx is not installed!")
                print("1. Install Nginx")
                print("2. Exit")

                choice = input("Enter your choice: ")

                if choice == "1":
                    manager.install_nginx()
                    nginx_installed = True
                    continue
                elif choice == "2":
                    break
            else:
                print(f"Current Nginx version: {manager.get_version()}\n")
                print("1. List domains")
                print("2. Add domain")
                print("3. Delete domain")
                print("4. Install SSL")
                print("5. Renew SSL")
                print("6. Add subfolder")
                print("7. View domain configuration")
                print("8. Exit")

                choice = input("Enter your choice: ")

                if choice == "1":
                    domains = manager.get_domains()
                    if not domains:
                        print("No domains configured")
                    else:
                        for idx, domain in enumerate(domains, 1):
                            print(f"{idx}. {domain}")

                elif choice == "2":
                    domain = input("Enter domain name: ")
                    config_type = input("Configuration type (static/proxy): ")
                    path = input("Enter path (HTML directory or proxy URL): ")
                    manager.add_domain(domain, config_type, path)
                    print(f"Added domain {domain}")

                elif choice == "3":
                    domain = input("Enter domain name to delete: ")
                    manager.delete_domain(domain)
                    print(f"Deleted domain {domain}")

                elif choice == "4":
                    domain = input("Enter domain name to install SSL: ")
                    manager.install_ssl(domain)
                    print(f"Installed SSL for domain {domain}")

                elif choice == "5":
                    manager.renew_ssl()
                    print("Renewed SSL certificates")

                elif choice == "6":
                    domains = manager.get_domains()
                    if not domains:
                        print("No domains configured. Please add a domain first.")
                        continue

                    print("Available domains:")
                    for idx, domain in enumerate(domains, 1):
                        print(f"{idx}. {domain}")

                    while True:
                        try:
                            domain_choice = int(
                                input("Enter the number of the domain to add a subfolder: "))
                            if 1 <= domain_choice <= len(domains):
                                domain = domains[domain_choice - 1]
                                break
                            else:
                                print(
                                    "Invalid choice. Please enter a valid number.")
                        except ValueError:
                            print("Invalid input. Please enter a number.")

                    subfolder = input("Enter subfolder name: ")
                    html_path = input("Enter path to HTML directory: ")
                    manager.add_subfolder(domain, subfolder, html_path)
                    print(f"Added subfolder {subfolder} for domain {domain}")

                elif choice == "7":
                    domain = input("Enter domain name to view configuration: ")
                    config = manager.view_domain_config(domain)
                    print(f"Configuration for domain {domain}:")
                    print(config)

                elif choice == "8":
                    break

    except NginxManagerError as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    main()
