from nginx_manager import NginxManager
from exceptions import NginxManagerError


def main():
    try:
        manager = NginxManager()
        nginx_installed = manager.is_nginx_installed()  # Thêm method kiểm tra nginx

        while True:
            print("\n=== Nginx CLI Management ===")

            if not nginx_installed:
                print("Nginx is not installed!")
                print("1. Install Nginx")
                print("2. Exit")

                choice = input("Enter choice: ")

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
                print("6. Exit")

                choice = input("Enter choice: ")

                if choice == "1":
                    domains = manager.get_domains()
                    if not domains:
                        print("No domains configured")
                    else:
                        for idx, domain in enumerate(domains, 1):
                            print(f"{idx}. {domain}")

                elif choice == "6":
                    break

                # Implement other menu options...

    except NginxManagerError as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    main()
