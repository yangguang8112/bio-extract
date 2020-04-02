from utils import mysleep
import os

# key_path = r'D:\work\202004\keywordfile'
key_path = r'/root/keywordfile/'
file_list = []
file_name = []
for root, dir, files in os.walk(key_path):
    for file in files:
        if file.endswith('txt'):
            file_list.append(file)
            file_name.append(file[:-4])

file_dir = []
for file in file_list:
    dir = key_path + file
    file_dir.append(dir)

for i in range(1, 2):
    command = 'python handle.py --timeout 20 \
--scihub https://sci-hub.tw \
--maxpage 5 \
--keys {}'.format(file_dir[i])
    print(command)
    print(i)
    os.system(command)
    mysleep(3600)

