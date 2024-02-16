import json

import click
import requests

from config import TodoConfig


class TodoApi:
    @staticmethod
    def sync_todo(unsync_data):
        res = requests.put(TodoConfig.get_base_url() + "/todoList/sync", json=unsync_data)
        TodoApi.resolve_response(res)

    @staticmethod
    def get_client_sync_data():
        res = requests.get(TodoConfig.get_base_url() + "/todoList/client_sync_data", TodoConfig.get_config())
        res_data = TodoApi.resolve_response(res)
        return res_data

    @staticmethod
    def resolve_response(response_data):
        if response_data.status_code == 404:
            click.echo(click.style("请求异常：" + response_data.text, fg="red"))
            raise RuntimeError(404)
        data = json.loads(response_data.text)
        if data["code"] != 200:
            click.echo(click.style("响应异常：" + data["msg"], fg="red"))
            raise RuntimeError(data["msg"])
        return data["data"]
