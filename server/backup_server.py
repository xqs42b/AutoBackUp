import os
import json
import socket
import time
import struct
import setting
import shutil
from threading import Thread


def recv_content():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((setting.server_ip, setting.port))
    server.listen(setting.max_conn)
    while True:
        conn, addr = server.accept()
        while True:
            # 接收报头
            header = conn.recv(4)
            header_tup = struct.unpack("i", header)
            header_len = header_tup[0]
            header_bytes = conn.recv(header_len)
            header_dict = json.loads(header_bytes.decode("utf-8"))
            write_content(header_dict, conn)
            break


def make_dir(msave_path):
    """创建文件夹"""
    dir_list = msave_path.split("/")
    init_path = setting.save_path
    for tdir in dir_list:
        if tdir == "":
            continue
        curr_file_dir = os.listdir(init_path)
        new_tdir = tdir + "/"
        init_path += new_tdir
        if tdir not in curr_file_dir:
            os.mkdir(init_path)


def write_content(wheader, wconn):
    """写入文件"""
    file_name = wheader.get("file_name")
    file_size = wheader.get("file_size")
    save_path = wheader.get("save_path")
    if file_name is not None:
        if save_path != "./":
            make_dir(save_path)
            current_save_path = setting.save_path + save_path + file_name
        else:
            current_save_path = setting.save_path + file_name
        with open(current_save_path, "ab") as f:
            init_size = 0
            while True:
                if init_size >= file_size:
                    wconn.close()
                    break
                data = wconn.recv(1024)
                f.write(data)
                init_size += len(data)
    else:
        print("------dir:", wheader)
        dir_name = wheader.get("dir_name")
        dir_file_size = wheader.get("dir_size")
        save_path = wheader.get("save_path")
        dir_file_str = ""
        init_dir_size = 0
        while True:
            if init_dir_size >= dir_file_size:
                wconn.close()
                break
            dir_data = wconn.recv(1024)
            dir_file_str += dir_data.decode("utf-8")
            init_dir_size += len(dir_data)
        dir_file_list = json.loads(dir_file_str)
        if save_path == "./":
            new_dir = setting.save_path + dir_name
        else:
            save_path_list = save_path.split("./")
            new_dir = setting.save_path + save_path_list[-1]
        current_path_list = os.listdir(new_dir)
        differ_ele = set(current_path_list) - set(dir_file_list)
        if differ_ele != 0:
            trash_list = os.listdir(setting.trash_path)
            for file_dir in differ_ele:
                if file_dir not in trash_list:
                    shutil.move(new_dir + file_dir, setting.trash_path)


def monitor_del_file():
    """定时彻底删除垃圾文件"""
    trash_list = os.listdir(setting.trash_path)
    for file_dir in trash_list:
        file_dir_path = setting.trash_path + file_dir
        file_dir_time = int(os.path.getctime(file_dir_path))
        if int(time.time()) - setting.max_save_time >= file_dir_time:
            if os.path.isdir(file_dir_path):
                os.rmdir(file_dir_path)
            else:
                os.remove(file_dir_path)


if __name__ == "__main__":
    t1 = Thread(target=monitor_del_file, daemon=True)
    t1.start()

    recv_content()
