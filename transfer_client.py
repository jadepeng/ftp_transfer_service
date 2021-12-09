import json
import os
from time import sleep

from ftp.database import Database
from ftp.db_service import DbService
from ftp.ftpClient import FtpClient
from ftp.redis_queue import RedisQueue
from ftp.settings import APISettings

settings = APISettings()
database = Database(settings.mysql_host, settings.mysql_port, settings.mysql_user, settings.mysql_password,
                    settings.mysql_db)
db_service = DbService(settings, database)

progress_file = "current_file.lock"

def write_current_task(taskId, item):
    with open(progress_file, 'w', encoding='utf8') as f:  # 如果filename不存在会自动创建， 'w'表示写数据，写之前会清空文件中的原有数据！
        f.write(json.dumps({
            "taskId": taskId,
            "item": item
        }))


def get_unfinished_task():
    if os.path.exists(progress_file) and os.path.getsize(progress_file) > 0:
        with open(progress_file, encoding='utf8') as f:  # 默认模式为‘r’，只读模式
            contents = f.read()
            return json.loads(contents)
    return None  #


def remove_lock():
    os.remove(progress_file)


def transfer_task(task_progress, item=None):
    task = db_service.get_task(task_progress.taskId)
    queque = RedisQueue(f"transfer_queue_{task.taskId}", host=settings.redis_server, port=settings.redis_port, db=0,
                        password=settings.redis_password)
    ftp = FtpClient(task.host, task.port, task.user, task.password)
    local_path = task.storagePath

    # 继续未完成
    if item:
        transfer_task_item(ftp, local_path, queque, task, json.loads(item))

    wait_time_out_count = 0

    while True:
        task_item = queque.get_wait(5)
        if not task_item:
            wait_time_out_count = wait_time_out_count + 1
            task_progress = db_service.get_unfinished_task()
            # 这里出问题如何处理?
            if task_progress.finished + task_progress.failed >= task_progress.total:
                db_service.finish_task(task.taskId)
                break
            # 为防止一直错误，这里有退出机制
            if wait_time_out_count > settings.max_wait_time_count:
                db_service.failed_task(task.taskId)
                break
        else:
            wait_time_out_count = 0
            item_json = task_item[1].decode("utf-8")
            write_current_task(task.taskId, item_json)
            task_item = json.loads(item_json)
            transfer_task_item(ftp, local_path, queque, task, task_item)


def transfer_task_item(ftp, local_path, queque, task, task_item):
    try:
        local_file_name = local_path + task_item['fileName']
        print("transfer %s to %s" % (task_item['fileName'], local_file_name))

        # 文件已存在
        if os.path.exists(local_file_name):
            # 比较大小
            size = os.path.getsize(local_file_name)
            if size == task_item["fileSize"]:
                db_service.update_finished(task.taskId, 1)
                return

        dir = os.path.abspath(os.path.dirname(local_file_name))
        os.makedirs(dir, exist_ok=True)
        ftp.download_file(task_item['fileName'], local_file_name)
        # 更新进度
        db_service.update_finished(task.taskId, 1)
    except Exception as e:
        print(e)
        if task_item['retryCount'] < 3:
            task_item['retryCount'] = task_item['retryCount'] + 1
            queque.put(json.dumps(task_item))
        else:
            print(task_item['fileName'] + " transfer failed with max_retry_count")
            db_service.add_failed_file(task.taskId, task_item['fileName'])
    finally:
        remove_lock()


# 未完成的任务
unfinished = get_unfinished_task()
if unfinished:
    task_id = unfinished["taskId"]
    progress = db_service.get_progress(task_id)
    transfer_task(progress, unfinished["item"])

while True:
    # 当前获取首个
    task_progress = db_service.get_unfinished_task()
    if task_progress:
        transfer_task(task_progress)
    else:
        print("there is no task, sleep 5s ...")
        sleep(5)
