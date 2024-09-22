from ftplib import FTP
import os

def upload_files_to_ftp(ftp_server, ftp_user, ftp_password, local_directory, remote_directory):
    try:
        ftp = FTP(ftp_server)
        ftp.login(user=ftp_user, passwd=ftp_password)

        for root, dirs, files in os.walk(local_directory):
            for filename in files:
                local_file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(local_file_path, local_directory)
                remote_file_path = os.path.join(remote_directory, relative_path).replace("\\", "/")

                remote_dir = os.path.dirname(remote_file_path)
                try:
                    ftp.cwd(remote_dir)
                except Exception:
                    try:
                        ftp.mkd(remote_dir)
                        print(f"{remote_dir} oluşturuldu.")
                    except Exception as e:
                        if "550" not in str(e):
                            print(f"{remote_dir} oluşturulurken hata: {e}")

                try:
                    with open(local_file_path, 'rb') as file:
                        ftp.storbinary(f'STOR {remote_file_path}', file)
                    print(f"{filename} başarıyla yüklendi.")
                except Exception as upload_error:
                    print(f"{filename} yüklenirken hata oluştu: {upload_error}")

    except Exception as e:
        print(f"Hata: {e}")
    finally:
        ftp.quit()

if __name__ == "__main__":
    local_directory = os.path.dirname(os.path.abspath(__file__))

    upload_files_to_ftp(
        ftp_server='5.180.185.145',
        ftp_user='yaris_user',
        ftp_password='Ogren2024*-+',
        local_directory=local_directory,
        remote_directory='/api.yarisogren.com'
    )
