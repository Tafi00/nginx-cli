from nginx_manager import NginxManager
from exceptions import NginxManagerError


def main():
    try:
        manager = NginxManager()
        nginx_installed = manager.is_nginx_installed()

        while True:
            print("\n=== Quản lý Nginx CLI ===")

            if not nginx_installed:
                print("Nginx chưa được cài đặt!")
                print("1. Cài đặt Nginx")
                print("2. Thoát")

                choice = input("Nhập lựa chọn: ")

                if choice == "1":
                    manager.install_nginx()
                    nginx_installed = True
                    continue
                elif choice == "2":
                    break
            else:
                print(f"Phiên bản Nginx hiện tại: {manager.get_version()}\n")
                print("1. Liệt kê domain")
                print("2. Thêm domain")
                print("3. Xóa domain")
                print("4. Cài đặt SSL")
                print("5. Gia hạn SSL")
                print("6. Thêm thư mục con")
                print("7. Xem cấu hình domain")
                print("8. Thoát")

                choice = input("Nhập lựa chọn: ")

                if choice == "1":
                    domains = manager.get_domains()
                    if not domains:
                        print("Không có domain nào được cấu hình")
                    else:
                        for idx, domain in enumerate(domains, 1):
                            print(f"{idx}. {domain}")

                elif choice == "2":
                    domain = input("Nhập tên domain: ")
                    config_type = input("Loại cấu hình (static/proxy): ")
                    path = input(
                        "Nhập đường dẫn (thư mục HTML hoặc URL proxy): ")
                    manager.add_domain(domain, config_type, path)
                    print(f"Đã thêm domain {domain}")

                elif choice == "3":
                    domain = input("Nhập tên domain cần xóa: ")
                    manager.delete_domain(domain)
                    print(f"Đã xóa domain {domain}")

                elif choice == "4":
                    domain = input("Nhập tên domain cần cài đặt SSL: ")
                    manager.install_ssl(domain)
                    print(f"Đã cài đặt SSL cho domain {domain}")

                elif choice == "5":
                    manager.renew_ssl()
                    print("Đã gia hạn chứng chỉ SSL")

                elif choice == "6":
                    domain = input("Nhập tên domain: ")
                    subfolder = input("Nhập tên thư mục con: ")
                    html_path = input("Nhập đường dẫn đến thư mục HTML: ")
                    manager.add_subfolder(domain, subfolder, html_path)
                    print(
                        f"Đã thêm thư mục con {subfolder} cho domain {domain}")

                elif choice == "7":
                    domain = input("Nhập tên domain cần xem cấu hình: ")
                    config = manager.view_domain_config(domain)
                    print(f"Cấu hình cho domain {domain}:")
                    print(config)

                elif choice == "8":
                    break

    except NginxManagerError as e:
        print(f"Lỗi: {str(e)}")
        return 1


if __name__ == "__main__":
    main()
