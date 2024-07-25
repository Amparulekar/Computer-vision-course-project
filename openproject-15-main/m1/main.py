import cv2,argparse,os,random
import numpy as np

from solver import Solver
def shuffle(segmats):
    shuffled_segmats = segmats.copy()
    random.shuffle(shuffled_segmats)
    return shuffled_segmats
def concatsave(segs,fname,ns):
    toconcat = []
    for i in range(1,ns+1):
        toconcat.append(np.concatenate(segs[(i-1)*ns:ns*i],axis=1))
    result = np.concatenate(toconcat, axis=0)
    cv2.imwrite(fname, result)    
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path',type=str)
    parser.add_argument('--ns',type=int,default=3)
    parser.add_argument('--mdm', type=int,default=1)
    args = parser.parse_args()
    segmentspath = args.path
    if(not segmentspath.endswith('/')):segmentspath+='/'
    segbasenames = os.listdir(segmentspath)
    segbasenames = sorted(segbasenames,key=lambda fname:int(fname.split('.jpg')[0].split('seg')[1]))
    segpaths = list(map(lambda x:f'{segmentspath}/{x}',segbasenames))
    segmats = list(map(lambda path:(cv2.imread(path)),segpaths))
    shuffledsegmats = shuffle(segmats)
    jigsawSolver = Solver()
    x,y = jigsawSolver.solve(shuffledsegmats,args.mdm)
    # y = list(map(lambda yold:args.ns-1-yold,y))
    pos = list(zip(x,y))
    print(pos)
    indices = list(map(lambda p:int(p[0]+args.ns*p[1]),pos))
    print(indices)
    orderedsegs = np.zeros((args.ns*args.ns,*shuffledsegmats[0].shape))
    for i in range(args.ns*args.ns):
        orderedsegs[indices[i]] = shuffledsegmats[i]
    # print(orderedsegs)
    concatsave(orderedsegs,'combined.jpg',args.ns)
    concatsave(shuffledsegmats,'shuffled.jpg',args.ns)
    # for i in range(len(segmats)):
    #     cv2.imshow(f'{i}',segmats[i])
    # cv2.waitKey(0)
    