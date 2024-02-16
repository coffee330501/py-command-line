import json
import os
import time


class TodoConfig:
    config_path = "E:/Todo/todo-config.json"
    __config = {}

    @staticmethod
    def get_config():
        if TodoConfig.__config.__len__() == 0:
            with open(TodoConfig.config_path, "r", encoding="utf-8") as f:
                TodoConfig.config = json.load(f)
        return TodoConfig.config

    @staticmethod
    def init():
        # 初始化配置文件
        with open(TodoConfig.config_path, "w", encoding="utf-8") as f:
            config = {
                "lastSyncTime": "2020-01-01 00:00:00",
                "baseUrl": "http://127.0.0.1:8000",
                "todoFilePath": "E:/Todo/todo-list.json"
            }
            json.dump(config, f, ensure_ascii=False)

        # 初始化todo文件
        todo_file_path = TodoConfig.get_todo_file_path()
        if not os.path.exists(todo_file_path):
            # 文件不存在则创建文件
            file = open(todo_file_path, "w")
            file.write("[]")
            file.close()

    @staticmethod
    def get_base_url():
        return TodoConfig.get_config().get("baseUrl")

    @staticmethod
    def get_todo_file_path():
        return TodoConfig.get_config().get("todoFilePath")

    @staticmethod
    def update_sync_time():
        config = TodoConfig.get_config()
        config["lastSyncTime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        with open(TodoConfig.config_path, 'w', encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False)
