import struct
import json
import socket
import config 
import os
import time


def read_file(rfilepath):
    """读文件"""
    try:
        with open(rfilepath, "rb") as file:
            return file.readlines()
    except Exception as error:
        print("read_file_error:", error)
        return None


def send_content(file_name, scpath, scfile):
    """发送文件内容"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((config.server_ip, config.port))

    file_path = "%s%s" % (scpath, file_name)
    file_size = os.path.getsize(file_path)
    if scpath == config.file_path:
        save_path = "./"
    else:
        path_split_list = scpath.split(config.file_path)
        save_path = path_split_list[-1]
    file_info = {
        "file_name": file_name,
        "file_size": file_size,
        "save_path": save_path
    }
    header_bytes = json.dumps(file_info).encode("utf-8")
    header = struct.pack("i", len(header_bytes))
    client_socket.send(header)
    client_socket.send(header_bytes)
    for line in scfile:
        client_socket.send(line)
    return True


def operate_file_dir(gfdpath, gfnext_time):
    """操作文件，和文件夹"""
    file_dir_list = os.listdir(gfdpath)
    for file_dir in file_dir_list:
        if os.path.isfile(gfdpath + file_dir):
            file_path = "%s%s" % (gfdpath, file_dir)
            if gfnext_time is None:
                curr_content = read_file(file_path)
                if curr_content is not None:
                    send_content(file_dir, gfdpath, curr_content)
                else:
                    print("读取%s失败！" % file_path)
                continue
            # 获取文件最近一次修改时间
            update_file_time = int(os.path.getmtime(file_path))
            if update_file_time < int(time.time()) - config.gap_time:
                continue
            curr_content = read_file(file_path)
            if curr_content is not None:
                send_content(file_dir, gfdpath, curr_content)
            else:
                print("读取%s失败！" % file_path)
        else:
            dir_path = "%s%s/" % (gfdpath, file_dir)
            operate_file_dir(dir_path, gfnext_time)
            file_dir_list_json = json.dumps(os.listdir(dir_path)).encode("utf-8")
            send_dir(file_dir, gfdpath, file_dir_list_json)


def main():
    next_time = None
    while True:
        curr_time = int(time.time())
        if curr_time == next_time or next_time is None:
            read_file_path = config.file_path
            operate_file_dir(read_file_path, next_time)
            next_time = int(time.time()) + config.gap_time


def send_dir(dir_name, scpath, dir_content):
    """发送文件夹，有那些文件"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((config.server_ip, config.port))

    dir_size = len(dir_content)
    if scpath == config.file_path:
        save_path = "./"
    else:
        path_split_list = scpath.split(config.file_path)
        save_path = "./" + path_split_list[-1]
    dir_info = {
        "dir_name": dir_name,
        "dir_size": dir_size,
        "save_path": save_path
    }
    header_bytes = json.dumps(dir_info).encode("utf-8")
    header = struct.pack("i", len(header_bytes))
    client_socket.send(header)
    client_socket.send(header_bytes)
    client_socket.sendall(dir_content)
    return True


if __name__ == "__main__":
    main()
