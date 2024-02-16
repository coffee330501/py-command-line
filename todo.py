import hashlib
import json
import os
import os.path
import time

import click

from api import TodoApi
from config import TodoConfig

todo_file_path = TodoConfig.get_todo_file_path()
config_path = TodoConfig.config_path


@click.group()
def cli():
    pass


@cli.command("init", help="初始化")
def init():
    TodoConfig.init()


@cli.command("add", help="添加")
@click.option("--t", prompt="标题", help="添加标题", default="默认", type=str)
@click.option("--c", prompt="内容", help="添加内容")
@click.option("--tg", prompt="标签", help="添加标签")
def add(t, c, tg):
    # TodoList内容
    data = {
        "id": "",
        "title": t,
        "content": c,
        "tag": tg,
        "createTime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "status": "Pending",
        "sync": 0
    }
    md5 = hashlib.md5()
    md5.update(str(data).encode())
    data["id"] = md5.hexdigest()

    file_exists = True
    if not os.path.exists(todo_file_path):
        # 文件不存在则创建文件
        file = open(todo_file_path, "w")
        file_exists = False
        file.close()
    with open(todo_file_path, "r", encoding="utf-8") as f:
        if file_exists:
            old_data = json.load(f)
        else:
            old_data = []
        old_data.append(data)
    with open(todo_file_path, "w", encoding="utf-8") as f:
        json.dump(old_data, f, ensure_ascii=False)
    click.echo(click.style("ok! generate id " + data["id"], fg="green"))


@cli.command("del", help="删除")
@click.option("--id", help="要删除的ID,按逗号分隔")
def delete(id):
    ids = id.split(",")
    with open(todo_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        if item["id"] in ids:
            item["status"] = "Deleted"
            item["sync"] = 0
    with open(todo_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


@cli.command("ll", help="列表")
@click.option("--id", is_flag=True, help="显示ID")
@click.option("--done", is_flag=True, help="显示已完成的内容")
def ll(id, done):
    with open(todo_file_path, "r", encoding="utf-8") as f:
        todo_list = json.load(f)
    for item in todo_list:
        status = item["status"]
        # 展示已完成的
        if done:
            if status == "Closed":
                print_item(item, id)
            else:
                continue

        # 正常不输出已完成的
        if status in ("Closed", "Deleted"):
            continue
        print_item(item, id)


@cli.command("detail", help="查看详情")
@click.option("--id", help="id")
def ll(id):
    with open(todo_file_path, "r", encoding="utf-8") as f:
        todo_list = json.load(f)
    for item in todo_list:
        if item["id"] == id:
            print_id(item, True)
            print_title(item, True)
            print_create_on(item, True)
            print_content(item, True)
            print_status(item, True)


def print_item(item, show_id):
    # 正常不输出id
    if show_id:
        print_id(item)
    print_title(item)
    print_content(item)


def print_id(item, nl=False):
    common_print(item, "id", "id", nl)


def print_title(item, nl=False):
    common_print(item, "title", "标题", nl)


def print_content(item, nl=True):
    common_print(item, "content", "内容", nl)


def print_status(item, nl=True):
    common_print(item, "status", "状态", nl)


def print_create_on(item, nl=False):
    common_print(item, "createTime", "创建时间", nl)


def common_print(item, field, filed_display_name, nl=False):
    click.echo(click.style(filed_display_name + ": ", fg="green", bold=True), nl=False)
    click.echo(click.style(item[field] + " ", fg="white"), nl=nl)


@cli.command("source", help="打开Todo文件")
def source():
    print("正在打开文件，稍等哦")
    os.startfile(todo_file_path)


@cli.command("config", help="打开配置文件")
def source():
    print("正在打开文件，稍等哦")
    os.startfile(TodoConfig.config_path)


@cli.command("edit", help="编辑")
@click.option("--id", prompt="ID", help="要编辑的ID")
@click.option("--title", prompt="标题", help="修改标题")
@click.option("--content", prompt="内容", help="修改内容")
def edit(id, title, content):
    with open(todo_file_path, "r", encoding="utf-8") as f:
        old_data = json.load(f)
    new_data = []
    success = False
    for item in old_data:
        if item["id"] == id:
            if content is not None:
                item["content"] = content
            if title is not None:
                item["content"] = content
            item["sync"] = 0
            success = True
        new_data.append(item)
    if not success:
        click.echo(click.style("编辑失败，请检查ID", fg="red"))
        return
    with open(todo_file_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False)


@cli.command("done", help="完成一项TODO")
@click.option("--id", help="要完成的ID")
def done(id):
    update_status_by_id(id)


def update_status_by_id(id):
    with open(todo_file_path, "r", encoding="utf-8") as f:
        old_data = json.load(f)
    new_data = []
    success = False
    for item in old_data:
        if item["id"] == id:
            item["status"] = "Closed"
            item["sync"] = 0
            success = True
        new_data.append(item)
    if not success:
        click.echo(click.style("更新失败，请检查ID", fg="red"))
        return
    with open(todo_file_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False)


# 同步云端
def sync_server():
    with open(todo_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        # 获取所有未同步的数据
        unsync_data = []
        for item in data:
            if item["sync"] == 0:
                unsync_data.append(item)
        # 同步数据
        TodoApi.sync_todo(unsync_data)
        # 将本地数据置为已同步
        for item in unsync_data:
            item["sync"] = 1
        # 保存本地数据
    with open(todo_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


# 同步本地
def sync_local():
    res_data = TodoApi.get_client_sync_data()

    with open(todo_file_path, 'r', encoding="utf-8") as f:
        todos = json.load(f)
        todo_dic = {}
        for todo in todos:
            todo_dic[todo["id"]] = todo

        for item in res_data:
            # 存在则更新
            if item["id"] in todo_dic:
                todo_local = todo_dic[item["id"]]
                for key in item:
                    todo_local[key] = item[key]
            # 不存在则新增
            else:
                todos.append({
                    "id": item["id"],
                    "status": item["status"],
                    "tag": item["tag"],
                    "title": item["title"],
                    "content": item["content"],
                    "createTime": item["createTime"],
                    "sync": 1,
                })

    with open(todo_file_path, 'w', encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False)


# 删除本地已删除的Todo
def clear_local_deleted():
    new_list = []
    with open(todo_file_path, 'r', encoding="utf-8") as f:
        todo_list = json.load(f)
        for item in todo_list:
            if item.get("status") == "Deleted":
                continue
            new_list.append(item)

    with open(todo_file_path, 'w', encoding="utf-8") as f:
        json.dump(new_list, f, ensure_ascii=False)


@cli.command("sync", help="同步本地与云端")
def sync_todo_list():
    sync_server()
    sync_local()
    TodoConfig.update_sync_time()
    click.echo(click.style("sync success", fg="green"))
    clear_local_deleted()


if __name__ == '__main__':
    cli()
