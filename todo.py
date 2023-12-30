import json
import os.path
import time
import hashlib
import click
import os

filepath = "E:/Todo/todo-list.json"


@click.group()
def cli():
    pass


@cli.command("add", help="添加")
@click.option("--t", prompt="标题", help="添加标题", default="默认", type=str)
@click.option("--c", prompt="内容", help="添加内容")
def add(t, c):
    # TodoList内容
    data = {
        "id": "",
        "title": t,
        "content": c,
        "createOn": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "status": "Pending"
    }
    md5 = hashlib.md5()
    md5.update(str(data).encode())
    data["id"] = md5.hexdigest()

    file_exists = True
    if not os.path.exists(filepath):
        # 文件不存在则创建文件
        file = open(filepath, "w")
        file_exists = False
        file.close()
    with open(filepath, "r", encoding="utf-8") as f:
        if file_exists:
            old_data = json.load(f)
        else:
            old_data = []
        old_data.append(data)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(old_data, f, ensure_ascii=False)
    click.echo(click.style("ok! generate id " + data["id"], fg="green"))


@cli.command("del", help="删除")
@click.option("--ids", help="要删除的ID,按逗号分隔")
def delete(ids):
    ids = ids.split(",")
    print(ids)
    with open(filepath, "r", encoding="utf-8") as f:
        old_data = json.load(f)
    new_data = []
    for item in old_data:
        if not item["id"] in ids:
            new_data.append(item)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False)


@cli.command("ll", help="列表")
@click.option("--id", is_flag=True, help="显示ID")
@click.option("--done", is_flag=True, help="显示已完成的内容")
def ll(id, done):
    with open(filepath, "r", encoding="utf-8") as f:
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
        if status == "Closed":
            continue
        print_item(item, id)


@cli.command("detail", help="查看详情")
@click.option("--id", help="id")
def ll(id):
    with open(filepath, "r", encoding="utf-8") as f:
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
    common_print(item, "createOn", "创建时间", nl)


def common_print(item, field, filed_display_name, nl=False):
    click.echo(click.style(filed_display_name + ": ", fg="green", bold=True), nl=False)
    click.echo(click.style(item[field] + " ", fg="white"), nl=nl)


@cli.command("source", help="打开文件")
def source():
    os.startfile(filepath)


@cli.command("edit", help="编辑")
@click.option("--id", prompt="ID", help="要编辑的ID")
@click.option("--title", prompt="标题", help="修改标题")
@click.option("--content", prompt="内容", help="修改内容")
def edit(id, title, content, file):
    with open(filepath, "r", encoding="utf-8") as f:
        old_data = json.load(f)
    new_data = []
    success = False
    for item in old_data:
        if item["id"] == id:
            if content is not None:
                item["content"] = content
            if title is not None:
                item["content"] = content
            success = True
        new_data.append(item)
    if not success:
        click.echo(click.style("编辑失败，请检查ID", fg="red"))
        return
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False)


@cli.command("done", help="完成一项TODO")
@click.option("--id", help="要完成的ID")
def done(id):
    update_status_by_id(id)


def update_status_by_id(id):
    with open(filepath, "r", encoding="utf-8") as f:
        old_data = json.load(f)
    new_data = []
    success = False
    for item in old_data:
        if item["id"] == id:
            item["status"] = "Closed"
            success = True
        new_data.append(item)
    if not success:
        click.echo(click.style("更新失败，请检查ID", fg="red"))
        return
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False)


if __name__ == '__main__':
    cli()
