import os
import cv2
import sys
import argparse
def split_image(image_path,hsegs,vsegs,resize=False):
    image = cv2.imread(image_path)
    if(resize):
        image = cv2.resize(image,(600,600))
    height, width, _ = image.shape
    segment_width = width // hsegs
    segment_height = height // vsegs
    segments = []
    for i in range(vsegs):
        for j in range(hsegs):
            x = j * segment_width
            y = i * segment_height
            segment = image[y:y+segment_height, x:x+segment_width]
            segments.append(segment)
    return segments
def safekey(x):
    try:
        return int(x.split('.')[0])
    except:
        return x
if __name__=='__main__':
    rootf = 'cv';segmentedDir= 'segmented'
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean',action='store_true')
    parser.add_argument('--ss',default=1,type=int)
    parser.add_argument('--ns',default=3,type=int)
    parser.add_argument('--resize',action='store_true')
    args = parser.parse_args()
    if(args.clean):
        os.system('rm -rf segmented/*')
        exit()
    samplesize = args.ss
    for cat in os.listdir(rootf):
        folderpath = f'{rootf}/{cat}'
        fnames = sorted(os.listdir(folderpath),key=lambda x:safekey(x))[:samplesize]
        print(cat,': ',fnames)
        for fname in fnames:
            basename = fname.split('.')[0]
            segsavedir = f'{segmentedDir}/{cat}/{basename}'
            os.makedirs(segsavedir,exist_ok=True)
            segs = split_image(f'{rootf}/{cat}/{fname}',args.ns,args.ns,resize=args.resize)
            for i,seg in enumerate(segs):                    
                cv2.imwrite(f'{segsavedir}/seg{i}.jpg',seg)
    