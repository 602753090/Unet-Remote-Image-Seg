import os

# 用于为mask文件添加后缀
directory = './data-m/masks'  # 当前目录
suffix = '_mask'
extension = '.png'

for filename in os.listdir(directory):
    if filename.endswith(extension):
        base = os.path.splitext(filename)[0]
        new_name = f"{base}{suffix}{extension}"
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_name))

