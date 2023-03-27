# laravel queue manager

> 在 windows 中使用 laravel 队列时，无法高效的直接使用 php 动态创建或销毁队列进程，所以使用 python 做了一个 laravel 队列管理器。更多功能待完善中...

## 打包

执行根目录下的`setup.py`即可完成打包。

## 启动程序

直接打开`LaravelQueueManager-x.x.x.exe`程序。

## 配置

程序启动后，将在运行目录下生成`.env`文件，详细配置如下：

| 字段         | 类型   | 说明                              |
| ------------ | ------ | --------------------------------- |
| PORT         | int    | HTTP 服务器在本地启动的端口号     |
| PROJECT_PATH | string | 要运行队列的 laravel 项目的根路径 |

## 接口调用

### 启动指定队列

**请求地址：** `/api/start`

**请求方式：** GET

**请求参数：**

| 字段   | 类型   | 必填 | 说明                                          |
| ------ | ------ | ---- | --------------------------------------------- |
| queue  | string | 是   | 要启动的队列名称                              |
| params | string | 否   | 给队列启动时额外传递的参数，多个参数用`,`隔开 |

### 结束指定队列

**请求地址：** `/api/end`

**请求方式：** GET

**请求参数：**

| 字段  | 类型   | 必填 | 说明             |
| ----- | ------ | ---- | ---------------- |
| queue | string | 是   | 要结束的队列名称 |

**其它说明：** 执行后将直接结束队列进程，不会等待里面的任务运行完毕。

### 获取指定队列状态

**请求地址：** `/api/getStatus`

**请求方式：** GET

**请求参数：**

| 字段  | 类型   | 必填 | 说明             |
| ----- | ------ | ---- | ---------------- |
| queue | string | 是   | 要查询的队列名称 |

**响应说明：**

| 字段    | 类型       | 说明                                                |
| ------- | ---------- | --------------------------------------------------- |
| status  | enum\<int> | 运行状态；0=未在运行、1=正在运行、-1=运行异常       |
| flag    | string     | 运行状态描述常量；`STOPPED`、`RUNNING`、`EXCEPTION` |
| explain | string     | 运行状态描述解释语                                  |

### 启动所有队列列表

**请求地址：** `/api/getList`

**请求方式：** GET

**请求参数：**

| 字段 | 类型 | 必填 | 说明 |
| ---- | ---- | ---- | ---- |
| 无   |
