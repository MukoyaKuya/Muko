import os
import shutil

target = '/home1/bbintern/mukoyakuya.online/media'
source = '/home1/bbintern/muko/media'

print(f"Checking target: {target}")
if os.path.exists(target):
    if os.path.islink(target):
        print(f"Target is already a symlink: {os.readlink(target)}")
    elif os.path.isdir(target):
        print("Target is a directory. Removing it...")
        shutil.rmtree(target)
        os.symlink(source, target)
        print("Symlink created successfully.")
    else:
        print("Target is a file. Removing it...")
        os.remove(target)
        os.symlink(source, target)
        print("Symlink created successfully.")
else:
    print("Target does not exist. Creating symlink...")
    os.symlink(source, target)
    print("Symlink created successfully.")
