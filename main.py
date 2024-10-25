from nginx_manager import NginxManager
from exceptions import NginxManagerError
from utils import display_menu, get_user_choice


def main():
    try:
        manager = NginxManager()
        nginx_installed = manager.is_nginx_installed()

        while True:
            display_menu(nginx_installed)
            choice = get_user_choice()

            if not nginx_installed:
                if choice == "1":
                    manager.install_nginx()
                    nginx_installed = True
                elif choice == "2":
                    break
            else:
                if choice == "1":
                    manager.list_domains()
                elif choice == "2":
                    manager.add_domain_interactive()
                elif choice == "3":
                    manager.delete_domain_interactive()
                elif choice == "4":
                    manager.install_ssl_interactive()
                elif choice == "5":
                    manager.renew_ssl_interactive()
                elif choice == "6":
                    subfolder_choice = input(
                        "Choose subfolder type (1: Reverse Proxy, 2: Static HTML file): ")
                    if subfolder_choice == "1":
                        manager.add_subfolder_reverse_proxy_interactive()
                    elif subfolder_choice == "2":
                        manager.add_subfolder_static_html_interactive()
                    else:
                        print("Invalid choice for subfolder.")
                elif choice == "7":
                    manager.view_domain_config_interactive()
                elif choice == "8":
                    break
                else:
                    print("Invalid choice. Please try again.")

    except NginxManagerError as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    main()
