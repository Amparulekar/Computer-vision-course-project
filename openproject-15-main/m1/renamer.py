import os

cats = os.listdir('cv')
for folder in cats:
    fnames = os.listdir(f'cv/{folder}')
    for i in range(len(fnames)):
        srcname = f'cv/{folder}/{fnames[i]}'
        dstname = f'cv/{folder}/{i}.jpg'
        os.rename(srcname,dstname)