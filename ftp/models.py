from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime

from ftp.database import Base, Database
from ftp.settings import APISettings


class TransferTask(Base):
    __tablename__ = 'transfer_task'

    taskId = Column(String(255), primary_key=True, index=True)
    serverPath = Column(String(255), nullable=False)
    storagePath = Column(String(255), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    user = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    time = Column(DateTime, nullable=False, default=datetime.now)

class TransferFailedFile(Base):
    __tablename__ = 'transfer_failed_file'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    taskId = Column(String(255), index=True)
    filePath = Column(String(1024), nullable=False)
    time = Column(DateTime, nullable=False, default=datetime.now)

class TransferProgress(Base):
    __tablename__ = 'transfer_task_progress'

    taskId = Column(String(255), primary_key=True, index=True)
    total = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False)
    finished = Column(Integer, nullable=False)
    failed = Column(Integer, nullable=False)
    time = Column(DateTime, nullable=False, default=datetime.now)

if __name__ == '__main__':
    settings = APISettings()
    db = Database(settings.mysql_host, settings.mysql_port, settings.mysql_user, settings.mysql_password,
                  settings.mysql_db)
    Base.metadata.create_all(db.engine)
