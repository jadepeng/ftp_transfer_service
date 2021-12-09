import ftplib
import os
from datetime import datetime
import ntpath


class FtpClient:

    def __init__(self, host: str, port: int, user: str, password: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connect()

    def connect(self):
        self.ftp = ftplib.FTP()
        self.ftp.connect(host=self.host, port=self.port)
        self.ftp.login(self.user, self.password)
        self.ftp.encoding = "utf-8"

    def list_files(self, dir):
        self.ftp.cwd(dir)
        for file_data in self.ftp.mlsd():
            file_name, meta = file_data
            file_type = meta.get("type")
            if file_type == "file":
                try:
                    self.ftp.voidcmd("TYPE I")
                    file_size = self.ftp.size(file_name)
                    yield f"{dir}/{file_name}", file_size
                except Exception as e:
                    print(e)
            else:
                yield from self.list_files(dir + "/" + file_name)

    def download_file(self, file_name:str, local_file_name:str):
        try:
            self.ftp.retrbinary('RETR %s' % file_name, open(local_file_name, 'wb').write)
        except ftplib.error_perm:
            print('ERROR: cannot read file "%s"' % file_name)
            os.unlink(local_file_name)


if __name__ == '__main__':
    ftp = FtpClient('172.31.161.38',2121,'user', '12345')
    for (file_name, size) in ftp.list_files(""):
        print(file_name, size)
        ftp.download_file(file_name, ntpath.basename(file_name))
        break
