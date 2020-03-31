import os
from pathlib import Path

key_path = r'D:\work\202002\keywords'

file_list = []
file_name = []
for root, dir, files in os.walk(key_path):
    for file in files:
        if file.endswith('txt'):
            file_list.append(file)
            file_name.append(file[:-4])

file_dir = []
for file in file_list:
    dir = key_path + '\\' + file
    file_dir.append(dir)


for i in range(8,len(file_name)):
    command = 'python handle.py --datadir E:\\Pathogenic\\' + file_name[i] + \
              ' --timeout 20 \
--mirror https://f.glgoo.top \
--keys {}'.format(file_dir[i])
    print(command)
    print(i)
    os.system(command)
    # if i > 5:
    #    break


