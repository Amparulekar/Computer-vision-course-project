import os,argparse,cv2

import numpy as np
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path',type=str)
    parser.add_argument('--pad',type=int,default=1)
    args = parser.parse_args()
    path = args.path
    pad = int(args.pad)
    if(not path.endswith('/')):path+='/'
    files = os.listdir(path)
    for fbasename in files:
        fpath = f'{path}{fbasename}'
        img = cv2.imread(fpath)
        img[0:pad,:,:] = np.zeros_like(img[0:pad,:,:])
        img[-(pad+1):,:,:] = np.zeros_like(img[-(pad+1):,:,:])
        img[:,-(pad+1):,:] = np.zeros_like(img[:,-(pad+1):,:])
        img[:,0:pad,:] = np.zeros_like(img[:,0:pad,:])
        cv2.imwrite(fpath,img)
    