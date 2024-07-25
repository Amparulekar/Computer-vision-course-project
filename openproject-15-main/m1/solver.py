
from itertools import groupby
import random
from scipy.spatial.distance import mahalanobis
from scipy.optimize import linprog
import numpy as np
CONSTRAINTS = 2
THRES_REJ = 10e-5
DX = [0, -1, 0, 1];DY = [1, 0, -1, 0]
MGCROTINDS = [3, 0, 1, 2]
MGCROTS_N = len(MGCROTINDS)
MGC_DIST_MARGIN = 1
CONSTR_ORIENT_PROD = MGCROTS_N*CONSTRAINTS
class Solver:
    def computeWeights(self,pairwiseMatches, numImages):
        indexSet = set(range(numImages))
        weights = {}
        for i, j, o in pairwiseMatches:
            minRow = min(self.mgcDistances[k, j, o] for k in indexSet - {i})
            minCol = min(self.mgcDistances[i, k, o] for k in indexSet - {j})
            weights[i, j, o] = min(minRow, minCol) / self.mgcDistances[i, j, o]
        return weights
    def iOKey(l1):
        return l1[0], l1[-1]
    def computeActiveSelection(self,pairwiseMatches):
        activeSelection = []
        for _, group in groupby(sorted(pairwiseMatches,key=Solver.iOKey), Solver.iOKey):
            entries = list(group)
            distances = np.array([self.mgcDistances[entry] for entry in entries])
            lowestIndex = np.argmin(distances)
            entry = entries[lowestIndex]
            activeSelection.append(entry)
        return activeSelection
    def getSolutionComputationMatrices(self,activeSelection,weights):
        def rowIndex(i, o):
            return (CONSTR_ORIENT_PROD * i) + (CONSTRAINTS * o)
        n = int(len(activeSelection) / MGCROTS_N)
        sortedA = sorted(activeSelection,key=Solver.iOKey)
        hBase = np.array([-1] * CONSTRAINTS + [0] * (CONSTR_ORIENT_PROD*n - CONSTRAINTS))
        H = np.array([np.roll(hBase, k) for k in range(0, CONSTR_ORIENT_PROD * n, CONSTRAINTS)]).T
        xiBase = np.array([1, -1] * MGCROTS_N + [0] *(CONSTR_ORIENT_PROD)*(n - 1))
        Xi = np.array([np.roll(xiBase, k) for k in range(0, CONSTR_ORIENT_PROD * n,CONSTRAINTS * MGCROTS_N)]).T
        Xj = np.zeros(Xi.shape, dtype=np.int32)
        for i, j, o in sortedA:
            r = rowIndex(i, o)
            Xj[r:r + 2, j] = [-1, 1]
        X = Xi + Xj
        h, w = H.shape
        ZH = np.zeros((h, w), dtype=np.int32)
        ZX = np.zeros((h, n), dtype=np.int32)
        AUb = np.vstack([H, ZH])
        AUb = np.hstack([AUb, np.vstack([ZH, H])])
        AUb = np.hstack([AUb, np.vstack([X, ZX])])
        AUb = np.hstack([AUb, np.vstack([ZX, X])])
        bX = [];bY = []
        for (_,_,o) in sortedA:
            bX.extend([DX[o],-DX[o]])
            bY.extend([DY[o],-DY[o]])
        bUb = np.array(bX + bY)
        cBase = [weights[_] for _ in sortedA]
        c = np.array(cBase * CONSTRAINTS + ([0] * CONSTRAINTS * n))
        return c,AUb,bUb
    def computeSolution(self,activeSelection, weights, maxiter=None):
        n = int(len(activeSelection) / MGCROTS_N)
        c,AUb,bUb = self.getSolutionComputationMatrices(activeSelection,weights)
        options = {'maxiter': maxiter} if maxiter else {}
        solution = linprog(c, AUb, bUb, options=options)
        if not solution.success:
            if solution.message == 'Iteration limit reached.':
                raise ValueError('maxiters reached')
            else:
                raise ValueError('no solution: {}'.format(
                    solution.message))
        xy = solution.x[-n * 2:]
        return xy[:n], xy[n:]
    def computeRejectedMatches(self,activeSelection, x, y):
        rejectedMatches = set()
        for i, j, o in activeSelection:
            if abs(x[i] - x[j] - DX[o]) > THRES_REJ:
                rejectedMatches.add((i, j, o))
            if abs(y[i] - y[j] - DY[o]) > THRES_REJ:
                rejectedMatches.add((i, j, o))
        return rejectedMatches
    def computeMgcDistances(self,images, pairwiseMatches):
        return {(i, j, o): Solver.mgc(images[i], images[j], o) for
                i, j, o in pairwiseMatches}
    def mgc(image1, image2, orientation):
        numRotations = MGCROTINDS[orientation]
        image1Signed = np.rot90(image1, numRotations).astype(np.int16)
        image2Signed = np.rot90(image2, numRotations).astype(np.int16)
        gIL = image1Signed[:, -1] - image1Signed[:, -2]
        mu = gIL.mean(axis=0)
        s = np.cov(gIL.T) + np.eye(3) * 10e-6
        gIjLr = np.mean(image2Signed[:, :MGC_DIST_MARGIN],axis=1) - np.mean(image1Signed[:, -(MGC_DIST_MARGIN+1):-1],axis=1)
        return sum(mahalanobis(row, mu, np.linalg.inv(s)) for row in gIjLr)
    def initialPairwiseMatches(self,numImages):
        x,y,z = np.meshgrid(np.arange(numImages),np.arange(numImages),np.arange(MGCROTS_N))
        ans = np.stack([x.flatten(),y.flatten(),z.flatten()],axis=1)
        return [tuple(x) for x in ans.tolist()]
    def solve(self,images, mgcdistmargin=1,maxiter=None, randomSeed=None):
        global MGC_DIST_MARGIN
        MGC_DIST_MARGIN = mgcdistmargin
        if randomSeed:
            random.seed(randomSeed)
        pairwiseMatches = self.initialPairwiseMatches(len(images))
        #initialize space of all possible matchings.👆
        self.mgcDistances = self.computeMgcDistances(images, pairwiseMatches)
        #dictionary from match tuple to distance.
        weights = self.computeWeights(pairwiseMatches, len(images))
        #weights for loss function?
        activeSelection = self.computeActiveSelection(pairwiseMatches)
        x, y = self.computeSolution(activeSelection, weights, maxiter)
        oldX, oldY = np.zeros_like(x), np.zeros_like(y)
        while (not np.array_equal(oldX, x) and np.array_equal(oldY, y)):
            rejectedMatches = self.computeRejectedMatches(activeSelection, x, y)
            pairwiseMatches = list(set(pairwiseMatches) - rejectedMatches)
            activeSelection = self.computeActiveSelection(pairwiseMatches)
            oldX, oldY = x, y
            x, y = self.computeSolution(activeSelection, weights, maxiter)
        return x, y