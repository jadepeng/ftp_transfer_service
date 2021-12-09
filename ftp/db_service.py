from ftp.database import Database
from ftp.dto import TaskDTO
from ftp.models import TransferTask, TransferProgress, TransferFailedFile
from ftp.settings import APISettings
from ftp.task_status import TaskStatus


class DbService:

    def __init__(self, config: APISettings, database: Database):
        self.config = config
        self.database = database

    def get_task(self, taskId) -> TransferTask:
        session = self.database.get_session()
        return session.query(TransferTask).filter(TransferTask.taskId == taskId).first()

    def get_unfinished_task(self) ->TransferProgress:
        db = self.database.get_session()
        return db.query(TransferProgress)\
            .filter(TransferProgress.total > 0)\
            .filter(TransferProgress.status < TaskStatus.FINISHED.value)\
            .first()

    def update_scaning_progress(self, task: TransferTask, count):
        db = self.database.get_session()
        progress = db.query(TransferProgress).filter(TransferProgress.taskId == task.taskId).first()
        progress.status = TaskStatus.SCANNING.value
        progress.total = count
        db.commit()

    def update_scan_progress(self, task: TransferTask, count):
        db = self.database.get_session()
        progress = db.query(TransferProgress).filter(TransferProgress.taskId == task.taskId).first()
        progress.status = TaskStatus.SCANNED.value
        progress.total = count
        db.commit()

    def scan_failed(self, task: TransferTask):
        db = self.database.get_session()
        progress = db.query(TransferProgress).filter(TransferProgress.taskId == task.taskId).first()
        progress.status = TaskStatus.SCAN_FAILED.value
        db.commit()

    def update_finished(self, taskId, increment):
        self.database.execute_sql(f"update transfer_task_progress set finished=finished+{increment} where taskId='{taskId}'")

    def finish_task(self, taskId):
        self.database.execute_sql(f"update transfer_task_progress set status={TaskStatus.FINISHED.value} where taskId="
                                  f"'{taskId}'")

    def failed_task(self, taskId):
        self.database.execute_sql(f"update transfer_task_progress set status={TaskStatus.FAILURE.value} where taskId="
                                  f"'{taskId}'")

    def get_progress(self, taskId):
        db = self.database.get_session()
        return db.query(TransferProgress).filter(TransferProgress.taskId == taskId).first()

    def get_or_create_progress(self, task: TransferTask):
        db = self.database.get_session()
        dbitem = db.query(TransferProgress).filter(TransferProgress.taskId == task.taskId).first()
        if not dbitem:
            dbitem = TransferProgress()
            dbitem.taskId = task.taskId
            dbitem.total = 0
            dbitem.status = TaskStatus.SCANNING.value
            dbitem.finished = 0
            dbitem.failed = 0
            db.add(dbitem)
            db.commit()
        return dbitem

    def get_or_create_task(self, item: TaskDTO):
        db = self.database.get_session()
        dbitem = db.query(TransferTask).filter(TransferTask.taskId == item.taskId)
        if db.query(dbitem.exists()).scalar():
            return dbitem.first()
        dbitem = TransferTask()
        dbitem.taskId = item.taskId
        dbitem.host = item.host
        dbitem.port = item.port
        dbitem.user = item.user
        dbitem.password = item.password
        dbitem.storagePath = item.storagePath
        dbitem.serverPath = item.serverPath
        db.add(dbitem)
        db.commit()
        db.refresh(dbitem)
        return dbitem

    def add_failed_file(self, taskId, file):
        self.database.execute_sql(f"update transfer_task_progress set failed=failed+1 where taskId='{taskId}'")
        db = self.database.get_session()
        failed = TransferFailedFile()
        failed.taskId = taskId
        failed.filePath = file
        db.add(failed)
        db.commit()
        db.refresh(failed)
        return failed



