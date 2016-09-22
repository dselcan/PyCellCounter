import cv2
import numpy as np

REM_DIST = 20
class ImageHolder(object):
    def __init__(self, cats, fname = None, zoom = 0):
        self.image = None
        self.bwimg = None
        self.w = 0
        self.h = 0
        self.cats = cats
        self.saved = False
        self.zoom = zoom
        
        self.marks = []
        self.lines = [[] for i in range(self.cats)]
        self.mnums = [0 for i in range(self.cats)]
        
        if fname:
            self.set_image(fname)
        else:
            self.name = None
            
    def clear_lines(self):
        self.zoom = 0
        self.lines = [[] for i in range(self.cats)]
        
    def set_image(self, fname):
        self.name = ".".join(fname.split(".")[:-1])
        self.image = cv2.imread(fname)
        self.h, self.w = self.image.shape[:2]
        
        if len(self.image.shape) == 3:
            self.bwimg = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        else:
            self.bwimg = self.image
            
        self.image = cv2.cvtColor(self.bwimg, cv2.COLOR_GRAY2BGR)
            
    def add_mark(self, position, category):
        #print category
        if position[0] < 0 or position[0] > self.w or position[1] < 0 or position[1] > self.h:
            return
        self.mnums[category] += 1
        self.marks.append([self.mnums[category], position, category])
        self.saved = False
        
    def undo_mark(self, category):
        for m in reversed(self.marks):
            if m[2] == category:
                self.marks.remove(m)
                self.mnums[category] -= 1
                self.saved = False
                
    def undo_line(self, category):
        if self.lines[category]:
            self.lines[category].pop()
            self.saved = False
        
    def add_line(self, position, category):
        #print category
        if position[0] < 0 or position[0] > self.w or position[1] < 0 or position[1] > self.h:
            return
        self.lines[category].append(position)
        self.saved = False
        
    def get_dist_f(self, pos1, pos2):    
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
        
    def get_dist(self, pos1, pos2):
        return int(self.get_dist_f(pos1, pos2))
        
    def get_line_size(self, category, scale_data):
        df = scale_data[2]/self.get_dist_f(scale_data[0], scale_data[1])
        ls = len(self.lines[category])
        if ls <= 1:
            return 0
        else:
            size = 0.0
            for i in range(ls - 1):
                size += self.get_dist_f(self.lines[category][i], self.lines[category][i+1])
            return size*df
        
    def remove_mark(self, position, category):
        for m in self.marks:
            if(self.get_dist(m[1], position) < REM_DIST):
                self.marks.remove(m)
                self.saved = False
                break
        self.update_values()
        
    def remove_line(self, position, category):
        self.lines[category] = self.lines[category][:-1]
                    
    def remove_line_old(self, position):
        for l in self.lines:
            for p in l:
                if(self.get_dist(p, position) < REM_DIST):
                    l.remove(p)
                    self.saved = False
                    return
                    
    def update_values(self):
        self.mnums = [0 for i in range(self.cats)]
        for m in self.marks:
            self.mnums[m[2]] += 1
            m[0] = self.mnums[m[2]]