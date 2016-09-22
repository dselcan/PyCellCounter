import cv2
import numpy as np

REM_DIST = 10

DRAW_INITIAL_THRESHOLD = 10
DRAW_MOVE_FACTOR = 0.1
DRAW_DILATE_ITER = 5
DRAW_ERODE_ITER = 3

class ImageHolder(object):
    def __init__(self, fname = None, zoom = 0):
        self.image = None
        self.bwimg = None
        self.w = 0
        self.h = 0
        self.saved = False
        self.zoom = zoom
        self.blur = 9
        
        self.cells = []
        self.temp_poly = []
        self.temp_cells = []
        
        if fname:
            self.set_image(fname)
        else:
            self.name = None
            
    def set_image(self, fname):
        self.name = ".".join(fname.split(".")[:-1])
        self.image = cv2.imread(fname)
        self.h, self.w = self.image.shape[:2]
        
        if len(self.image.shape) == 3:
            self.bwimg = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        else:
            self.bwimg = self.image
            
        self.image = cv2.cvtColor(self.bwimg, cv2.COLOR_GRAY2BGR)
        
    def get_dist_f(self, pos1, pos2):    
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
        
    def get_dist(self, pos1, pos2):
        return int(self.get_dist_f(pos1, pos2))
        
    """    
    def get_max_fi(self, poly, scale_data):
        df = scale_data[2]/self.get_dist_f(scale_data[0], scale_data[1])
        ps = len(poly)
        
        points = None
        maxdelta = 0
        
        for i in range(ps):
            for j in range(ps-i-1):
                delta = ((poly[i][0] - poly[j][0])**2 + (poly[i][1] - poly[j][1])**2)**0.5
                if delta > maxdelta:
                    maxdelta = delta
                    points = poly[[i,j]]
                    
        return maxdelta*df, points
    """
    
    def get_area(self, poly, scale_data):
        df = scale_data[2]/self.get_dist_f(scale_data[0], scale_data[1])
        df = df**2
        return cv2.contourArea(poly)*df
        
    def get_poly(self, img):
        ret, contour, heirarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contour[0]
        
    """    
    def get_line_size(self, poly, scale_data):
        df = scale_data[2]/self.get_dist_f(scale_data[0], scale_data[1])
        if poly <= 1:
            return 0
        else:
            size = 0.0
            for i in range(poly - 1):
                size += self.get_dist_f(poly[i], poly[i+1])
            return size*df
    """
       
    def change_select(self, action):
        if action != "line":
            self.temp_poly = []
        if action != "draw":
            self.temp_poly = []
            
    def remove(self, pos):   
        if self.temp_poly:
            self.temp_poly = self.temp_poly[:-1]
        else:
            for i in range(len(self.cells)):
                if(cv2.pointPolygonTest(self.cells[i], pos, True) > -REM_DIST):
                    self.cells.pop(i)
                    break
                
    def add_by_area(self, start_pos):
        self.start_pos = start_pos
        self.cells.append([])
        self.modify_by_area(start_pos)
    
    def modify_by_area(self, end_pos):
        start_pos = self.start_pos
        img = self.bwimg
        blur = cv2.GaussianBlur(img,(self.blur, self.blur), 0)
        mask = np.zeros((self.h+2, self.w+2), dtype=np.uint8)
        
        const_up = DRAW_INITIAL_THRESHOLD
        const_down = 1
        factor = DRAW_MOVE_FACTOR
        
        if(start_pos != end_pos):
            delta = ((start_pos[0] - end_pos[0])**2 + (start_pos[1] - end_pos[1])**2)**0.5
            factor = np.log(delta)
            
        const_up = int(const_up*factor*DRAW_MOVE_FACTOR)

        ret, newimg, mask, rect = cv2.floodFill(blur, mask, start_pos, 0, const_down, const_up, (4 | (255 << 8) | cv2.FLOODFILL_MASK_ONLY))
        mask = mask[1:-1,1:-1]
        
        kernel = np.ones((3,3), dtype=np.uint8)
        mask = cv2.dilate(mask, kernel, iterations = DRAW_DILATE_ITER)
        mask = cv2.erode(mask, kernel, iterations = DRAW_ERODE_ITER)
        
        cell = self.get_poly(mask)
        
        self.cells[-1] = cell
        
    def add_by_line(self, pos):
        self.temp_poly.append(pos)
        
    def finish_by_line(self, pos):
        img = np.zeros_like(self.bwimg)
        cv2.drawContours(img, [np.array(self.temp_poly)], 0, [255], thickness=cv2.FILLED)
        self.cells.append(self.get_poly(img))
        self.temp_poly = []
        
    def add_by_draw(self, pos):
        if not pos in self.temp_poly:
            self.temp_poly.append(pos)
        
    def finish_by_draw(self, pos):
        img = np.zeros_like(self.bwimg)
        cv2.drawContours(img, [np.array(self.temp_poly)], 0, [255], thickness=cv2.FILLED)
        self.cells.append(self.get_poly(img))
        self.temp_poly = []