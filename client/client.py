import time
import json
import socket
import setting
import os


def read_file(rpath):
    """读文件"""
    try:
        with open(rpath, "rb") as f:
            content = f.read()
    except Exception as error:
        print("read_file_error:", error)
        return None
    return content


def make_send_content(content, curr_path):
    """把文件内容分割"""
    if content is None:
        return None
    content_list = [content[i:i+10240] for i in range(0, len(content), 10240)]
    # content_list = [content[i:i+20480] for i in range(0, len(content), 20480)]

    content_count = len(content_list)
    value_list = list()
    for val_key, val in enumerate(content_list):
        one_value = dict()
        one_value["id"] = val_key
        if isinstance(val, bytes):
            one_value["value"] = str(val)
        else:
            one_value["value"] = val
        one_value["total"] = content_count
        one_value["path"] = curr_path
        value_list.append(one_value)
    return value_list


def send_content(msg):
    """发送内容"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((setting.server_ip, setting.port))
        # msg = {
        #     'file_name': "./001.txt",
        #     'content': "hello world",
        #     'current_count': 1,
        #     "total_count": 10
        # }
        print("------", msg)
        client_socket.send(json.dumps(msg).encode("utf-8"))
        client_socket.close()
    except Exception as error:
        print("send_content_error:", error)
        return False
    return True


def main():
    file_dir_list = os.listdir(setting.file_path)
    for file_dir in file_dir_list:
        print("%s" % file_dir, os.path.isfile(file_dir))
        if os.path.isfile(file_dir):
            curr_content = read_file(file_dir)
            content_list = make_send_content(curr_content, file_dir)
            if content_list is None:
                continue
            for one_value in content_list:
                send_content(one_value)


if __name__ == "__main__":
    main()
