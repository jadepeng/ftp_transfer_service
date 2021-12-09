import dataclasses
import json

from ftp.beans import TransferItem
from ftp.db_service import DbService
from ftp.ftpClient import FtpClient
from ftp.models import TransferTask
from ftp.redis_queue import RedisQueue
from ftp.settings import APISettings
from ftp.simple_bloomfilter import BloomFilter


def scan_server_files(task: TransferTask, config: APISettings, db_service: DbService):
    queque = RedisQueue(f"transfer_queue_{task.taskId}", host=config.redis_server, port=config.redis_port, db=0,
                        password=config.redis_password)
    ftp = FtpClient(task.host, task.port, task.user, task.password)
    bloomFilter = BloomFilter(f"transfer_bf_{task.taskId}", bit_size=2000000, hash_count=4, start_seed=41,
                              host=config.redis_server, port=config.redis_port, db=0,
                              password=config.redis_password)
    count = 0

    db_service.get_or_create_progress(task)
    try:
        for (file_name, size) in ftp.list_files(task.serverPath):
            count = count + 1
            if not bloomFilter.exists(file_name):
                item = TransferItem(file_name, size, 0)
                queque.put(json.dumps(dataclasses.asdict(item)))
                bloomFilter.add(file_name)
            # 每5000更新一次扫描进度
            if count % 5000 == 0:
                db_service.update_scaning_progress(task, count)
    except Exception as e:
        print("list ftp files failed %s" % e)

    if count > 0:
        # 更新进度
        db_service.update_scan_progress(task, count)
    else:
        # 扫描失败
        db_service.scan_failed(task)