import uvicorn
from fastapi import FastAPI, Path, BackgroundTasks

from ftp.database import Database
from ftp.db_service import DbService
from ftp.dto import TaskDTO
from ftp.settings import APISettings
from ftp.task.scan_task import scan_server_files

app = FastAPI()
settings = APISettings()
database = Database(settings.mysql_host, settings.mysql_port, settings.mysql_user, settings.mysql_password,
                    settings.mysql_db)
db_service = DbService(settings, database)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/task")
def create_task(item: TaskDTO):
    dbitem = db_service.get_or_create_task(item)
    return {
        'error': 0,
        'data': dbitem
    }


@app.get("/task/{taskid}/start")
def start_task(background_tasks: BackgroundTasks, taskid: str = Path(..., title="The ID of the task to get")):
    task = db_service.get_task(taskid)
    background_tasks.add_task(scan_server_files, task, settings, db_service)
    return {
        'error': 0,
        'taskId': taskid,
        'data': 0
    }


@app.get("/task/{taskid}/progress")
def get_progress(taskid: str = Path(..., title="The ID of the task to get"), ):
    return {
        'error': 0,
        'taskId': taskid,
        'data': db_service.get_progress(taskid)
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
