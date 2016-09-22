import cv2
import numpy as np
import pickle

REM_DIST = 20
class DistanceCalcHolder(object):
    def __init__(self, cats, fname, mname = None):
        if mname is None:
            mname = ".".join(fname.split(".")[:-1]) + "_marks.dat"
        
        self.cats = cats
        self.name = ".".join(fname.split(".")[:-1])
        self.image = cv2.imread(fname)
        self.h, self.w = self.image.shape[:2]
        
        if len(self.image.shape) == 3:
            self.bwimg = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        else:
            self.bwimg = self.image
            
        self.image = cv2.cvtColor(self.bwimg, cv2.COLOR_GRAY2BGR)
        
        f = open(mname)
        try:
            self.marks, a, b = pickle.load(f)
        except:
            f.close()
            f = open(mname)
            self.marks = pickle.load(f)
        f.close()
        
    def get_dist(self, pos1, pos2):    
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
        
    def solve_one(self, marks):
        if len(marks) < 2:
            return (0.0, [])
        size = len(marks)
        
        dists = []
        for i in range(size):
            p1 = marks[i]
            for j in range(i + 1, size):
                p2 = marks[j]
                dists.append((self.get_dist(p1, p2), p1, p2))
        
        dists.sort()
        
        done = []
        radius = []
        i = 0
        while(len(done) < size):
            r = dists[i][0]/2
            
            if (not dists[i][1] in done) and (not dists[i][2] in done):
                done.append(dists[i][1])
                radius.append(r)
                done.append(dists[i][2])
                radius.append(r)
            elif (not dists[i][1] in done):
                rr = radius[done.index(dists[i][2])]
                done.append(dists[i][1])
                radius.append(r*2 - rr)
            elif (not dists[i][2] in done):
                rr = radius[done.index(dists[i][1])]
                done.append(dists[i][2])
                radius.append(r*2 - rr)
            
            i += 1
                
        res = []
        avg = 0.0
        max = 0.0
        for r, d in zip(radius, done):
            res.append((d, r))
            avg += r
            if max < r:
                max = r
        avg /= size
        
        return (avg, res, max)
            
        
    def solve(self):
        marks = [[] for i in range(self.cats)]
        for m in self.marks:
            marks[m[2]].append(m[1])
            
        solutions = []
        for m in marks:
            s = self.solve_one(m)
            print s
            solutions.append(s)
           
        return solutions
            
if __name__ == "__main__":
    dch = DistanceCalcHolder(10, "P3_7000d.tif")
    sol = dch.solve()[0]
    
    img = dch.image
    test_img = np.zeros((dch.h, dch.w))
    print len(sol[1])
    for m in sol[1]:
        img = cv2.circle(img, m[0], int(m[1]), [255, 0, 0])
        test_img = cv2.circle(test_img, m[0], int(m[1]), 255, -1)
    cv2.imwrite("test.png", img)
    
    rate = int(sol[0])
    
    kernel = np.ones((5,5), dtype=np.uint8)
    cv2.imwrite("tt0.png", test_img)
    test_img = cv2.dilate(test_img, kernel, iterations = rate)
    cv2.imwrite("tt1.png", test_img)
    test_img = cv2.erode(test_img, kernel, iterations = rate)
    cv2.imwrite("tt2.png", test_img)