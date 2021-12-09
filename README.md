# ftp_transfer

可以接收指令，从远程ftp服务器同步指定目录数据

接收到任务后，将task写入mysql
启动任务后，会扫描ftp文件列表，写入redis，`transfer_client`会读取redis队列，进行文件下载

## 配置

修改 `.env` 文件, 配置mysql和redis地址

```
REDIS_SERVER=""
REDIS_PORT=6380
REDIS_PASSWORD=""
MYSQL_HOST=""
MYSQL_PORT=3306
MYSQL_PASSWORD=""
MYSQL_USER=""
MYSQL_DB=""
```

## 启动服务

server 端

    python3 task_server.py

传输端，可以部署多个

    python3 transfer_client.py


## 接收任务

POST /task/

```json
{
  "taskId": "9",
  "serverPath": "/weblog",
  "storagePath": "/data",
  "host": "ftpServer",
  "port": 21,
  "user": "user",
  "password": "password"
}
```

## 启动传输

GET /task/{taskId}/start