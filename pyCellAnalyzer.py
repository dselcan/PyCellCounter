import cv2
import numpy as np
from PIL import Image, ImageTk
import Tkinter as tk
import tkFileDialog as tkfd
import ttk
import os
import pickle

from img_manip_analyze import *
from detection_windows import *

VERSION_STRING = "0.1"

#TSCALE = 0.5
#CATS = 10
#CAT_COLORS = [[255,0,0],[0,255,0],[255,255,0],[255,0,255],[255,255,255],[0,255,255],[255,70,0],[150,190,60],[0,150,200],[0,60,110]]
FINAL_OFFSET = 10
#OFFSET = [int(FINAL_OFFSET*TSCALE), int(FINAL_OFFSET*1.6*TSCALE)]

CELL_COLOR = [255,0,0]

ZOOM_VALS = [None,
        [(2030, 1825), (2452, 1825), 50.0],
        [(2163, 1798), (2481, 1798), 25.0],
        [(595, 1080), (734, 1080), 2.0],
        [(558, 1080), (771, 1080), 2.0],
        [(577, 1080), (752, 1080), 1.0],
        [(588, 1080), (743, 1080), 0.5]]
ZOOM_COLOR = [64, 128, 64]

LINE_WIDTH = 2

ROUND = 3


#style_raised = ttk.Style()
#style_raised.configure("Raised.Tbutton", relief="raised")
#style_sunken = ttk.Style()
#style_sunken.configure("Sunken.Tbutton", relief="sunken")

class root_window(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("800x600")
        self.iconbitmap('icon2.ico')
        self.title("PyCellAnalyzer")
        
        self.wait_for_window = False
        
        self.previous_dir = "."
        
        menubar=tk.Menu(self)
        filemenu=tk.Menu(menubar,tearoff=0)
        #filemenu.add_command(label="Save",       command=self.save_all)
        #filemenu.add_separator()
        filemenu.add_command(label="Load Image", command=self.load_image)
        filemenu.add_command(label="Save Image", command=self.save_image)
        #filemenu.add_separator()
        #filemenu.add_command(label="Load Marks", command=self.load_marks)
        #filemenu.add_command(label="Save Marks", command=self.save_marks)
        #filemenu.add_separator()
        #filemenu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        detectmenu=tk.Menu(menubar,tearoff=0)
        detectmenu.add_command(label="Alpha/Beta detection", command = self.ab_detection)
        menubar.add_cascade(label="Automate", menu=detectmenu)
        
        self.zoom_var = tk.IntVar()
        zoommenu=tk.Menu(menubar,tearoff=0)
        zoommenu.add_radiobutton(label="No Zoom", variable=self.zoom_var, value=0, command = self.change_zoom)
        zoommenu.add_separator()
        zoommenu.add_radiobutton(label="400x Zoom", variable=self.zoom_var, value=1, command = self.change_zoom)
        zoommenu.add_radiobutton(label="600x Zoom", variable=self.zoom_var, value=2, command = self.change_zoom)
        zoommenu.add_separator()
        zoommenu.add_radiobutton(label="3000x Zoom", variable=self.zoom_var, value=3, command = self.change_zoom)
        zoommenu.add_radiobutton(label="4400x Zoom", variable=self.zoom_var, value=4, command = self.change_zoom)
        zoommenu.add_radiobutton(label="7000x Zoom", variable=self.zoom_var, value=5, command = self.change_zoom)
        zoommenu.add_radiobutton(label="12000x Zoom", variable=self.zoom_var, value=6, command = self.change_zoom)
        menubar.add_cascade(label="Measure", menu=zoommenu)
        
        helpmenu=tk.Menu(menubar,tearoff=0)
        helpmenu.add_command(label="About", command=self.about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        
        self.config(menu=menubar)
        
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(side = "left", fill = "both", expand = "true")
        self.canvas = tk.Label(canvas_frame)
        self.canvas.bind("<Button-1>", self.mark_single)
        self.canvas.bind("<Double-Button-1>", self.mark_double)
        self.canvas.bind("<Button-3>", self.mark_right)
        self.canvas.bind("<B1-Motion>", self.mark_move)
        self.canvas.bind("<ButtonRelease-1>", self.mark_stop)
        self.canvas.pack(side = "left", fill = "both", expand = "true")
        
        side = ttk.LabelFrame(self, padding = 4)
        side.pack(side = "left", fill="y")
        
        info = ttk.Frame(side)
        info.pack(side = "bottom", fill = "x")
        self.l1 = ttk.Label(info, width = 22)
        self.l2 = ttk.Label(info, width = 22)
        self.l1.pack(side="top", fill = "x", expand = "true")
        self.l2.pack(side="top", fill = "x", expand = "true")
        
        tools = ttk.Frame(side)
        tools.pack(side = "top", fill = "x")
        
        self.action = "none"
        self.area_button = tk.Button(tools, text="Fill", relief="raised", command=self.select_area)
        self.area_button.pack(side = "top", fill = "x", expand = "true")
        
        self.line_button = tk.Button(tools, text="Line", relief="raised", command=self.select_line)
        self.line_button.pack(side = "top", fill = "x", expand = "true")
        
        self.draw_button = tk.Button(tools, text="Draw", relief="raised", command=self.select_draw)
        self.draw_button.pack(side = "top", fill = "x", expand = "true")
        
        self.ih = None
        self.yoff, self.xoff = (0,0)
        self.scale = 1.0
        
        self.start_pos = (0,0)
        
        self.setup_screen()
        self.bind("<Configure>", self.on_resize)
    
    def about(self):
        tkmb.showinfo("About", "Version " + VERSION_STRING + " of pyCellAnalyzer.")
    
    def change_zoom(self):
        if self.ih:
            self.ih.zoom = self.zoom_var.get()
        self.draw()
        
    def load_image(self):
        fn =  tkfd.askopenfilename(initialdir=self.previous_dir, defaultextension=".png", filetypes=[('Image file', (".png", ".tif", ".tiff", ".bmp", ".jpg", ".jpeg", ".gif"))])
        self.zoom_var.set(0)
        if fn:
            self.ih = ImageHolder(fn)
            try:
                self.previous_dir = os.path.split(fn)[0]
            except:
                print "Warning."
                
        self.draw()
        
    def save_image(self):
        if self.ih:
            fn =  tkfd.asksaveasfilename(initialdir=self.previous_dir, defaultextension=".png", initialfile=self.ih.name + "_counted.png", filetypes=[('Image file', '.png')])
        else:
            fn = None
        if fn:
            img = self.prepare_image()
            img = self.prepare_image_for_saving(img)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            try:
                cv2.imwrite(fn, img)
                self.previous_dir = os.path.split(fn)[0]
            except:
                print "Warning."
        
    def load_marks(self):
        if self.ih:
            fn =  tkfd.askopenfilename(initialdir=self.previous_dir, defaultextension=".dat", filetypes=[('Pycounter marks file', '.dat')])
        else:
            fn = None
        if fn:
            f = open(fn, "r")
            try:
                self.ih.cells = pickle.load(f)
                self.previous_dir = os.path.split(fn)[0]
            except:
                print "Warning."
                
            f.close()
            
        self.zoom_var.set(self.ih.zoom)
        self.draw()    
        
    def save_marks(self):
        if self.ih:
            fn =  tkfd.asksaveasfilename(initialdir=self.previous_dir, defaultextension=".dat", initialfile=self.ih.name + "_marks.dat", filetypes=[('Pycounter marks file', '.dat')])
        else:
            fn = None
            
        if fn:
            try:
                f = open(fn, "w")
                pickle.dump(self.ih.cells, f)
                f.close()
                self.previous_dir = os.path.split(fn)[0]
            except ValueError:
                print "Warning."
                
    def ab_detection(self):
        if self.ih:
            self.wait_for_window = True
            DetectionWindowAB(self.ih, self.canvas, self)
        
    def select_area(self):
        if self.ih:
            if self.action == "area":
                self.area_button.configure(relief="raised")
                self.action = "none"
            else:
                self.area_button.configure(relief="sunken")
                self.line_button.configure(relief="raised")
                self.draw_button.configure(relief="raised")
                self.action = "area"
            self.ih.change_select(self.action)
            self.draw()
            
    def select_line(self):
        if self.ih:
            if self.action == "line":
                self.line_button.configure(relief="raised")
                self.action = "none"
            else:
                self.area_button.configure(relief="raised")
                self.line_button.configure(relief="sunken")
                self.draw_button.configure(relief="raised")
                self.action = "line"
            self.ih.change_select(self.action)
            self.draw()
            
    def select_draw(self):
        if self.ih:
            if self.action == "draw":
                self.draw_button.configure(relief="raised")
                self.action = "none"
            else:
                self.area_button.configure(relief="raised")
                self.line_button.configure(relief="raised")
                self.draw_button.configure(relief="sunken")
                self.action = "draw"
            self.ih.change_select(self.action)
            self.draw()
                
    def undo(self):
        if self.ih:
            self.draw()
            
    def mark_single(self, event):
        self.mark("single", event.x, event.y)
        
    def mark_right(self, event):
        self.mark("right", event.x, event.y)
        
    def mark_double(self, event):
        self.mark("double", event.x, event.y)
        
    def mark_stop(self, event):
        self.mark("stop", event.x, event.y)    
        
    def mark_move(self, event):
        if event.type == "6":
            self.mark("move", event.x, event.y)
        
    def mark(self, type, x, y):
        #print type
        if self.ih and not self.wait_for_window:
            ih = self.ih
            pos = int((x - self.xoff)/self.scale), int((y - self.yoff)/self.scale)
            if pos[0] >= 0 and pos[0] < self.ih.w and pos[1] >= 0 and pos[1] < self.ih.h:
                if type == "right":
                    ih.remove(pos)
                elif self.action == "area":
                    if type == "single":
                        ih.add_by_area(pos)
                    elif type == "move":
                        ih.modify_by_area(pos)
                elif self.action == "line":
                    if type == "single":
                        ih.add_by_line(pos)
                    elif type == "double":
                        ih.finish_by_line(pos)
                elif self.action == "draw":
                    if type == "single":
                        self.ih.add_by_draw(pos)
                    elif type == "stop":
                        self.ih.finish_by_draw(pos)
                    elif type == "move":
                        self.ih.add_by_draw(pos)
                self.draw()
        
    def on_resize(self, event):
        if event.widget == self and (event.width != self.width or event.height != self.height):
            self.setup_screen()

    def prepare_image(self):
        ih = self.ih
        img = np.array(ih.image, dtype=np.uint8)
        
        if ih.zoom > 0:
            img = cv2.line(img, ZOOM_VALS[ih.zoom][0], ZOOM_VALS[ih.zoom][1], ZOOM_COLOR, 2*LINE_WIDTH)
        
        l = ih.temp_poly
        ls = len(l)
        if ls == 1:
            img = cv2.line(img, tuple(l[0]), tuple(l[0]), [255, 0, 0], LINE_WIDTH)
        else:
            for i in range(ls-1):
                img = cv2.line(img, tuple(l[i]), tuple(l[i+1]), [255, 0, 0], LINE_WIDTH)
            
            
        for c in ih.cells:
            cv2.drawContours(img, [c], 0, [0, 255, 128], thickness=cv2.FILLED)
            
        for c in ih.temp_cells:
            cv2.drawContours(img, [c], 0, [255, 0, 0], thickness=cv2.FILLED)

        #Draw blobs
            
        return img
        
    def sum_areas(self):
        total_area = 0.0
        ih = self.ih
        zoom = ih.zoom
        for c in ih.cells:
            area = ih.get_area(c, ZOOM_VALS[zoom])
            total_area += area
                
        if zoom > 2:
            img_area = ih.get_area(np.array([[0,0],[ih.w,0], [ih.w,ih.w], [0,ih.w]]), ZOOM_VALS[zoom]) #quick hack - image usually extended horizontally with junk
        elif zoom == 1 or zoom == 2:  
            img_area = ih.get_area(np.array([[0,0],[ih.h,0], [ih.w,ih.h], [0,ih.h]]), ZOOM_VALS[zoom]) #has no junk region
        return total_area, img_area
            
        
    def prepare_image_for_saving(self, img):
        img = cv2.copyMakeBorder(img, 0, 8*FINAL_OFFSET, 0, 0, cv2.BORDER_CONSTANT, (0, 0, 0))
        ih = self.ih
        zoom = ih.zoom
        
        total_area = 0.0
        if zoom > 0:
            total_area, img_area = self.sum_areas()
            text = "Cell area: " + str(round(total_area, 3)) + "um2 out of total area: " + str(round(img_area, 3)) + "um2."
            cv2.putText(img, text, (ih.w/50, ih.h + 3*FINAL_OFFSET), cv2.FONT_HERSHEY_DUPLEX, 1.0, [255, 255, 255])
           
        return img
            
    def draw(self):
        #self.update_line_size()
        if self.ih:
            draw_img = self.prepare_image()
            ws = float(self.width)/self.ih.w
            hs = float(self.height)/self.ih.h
            s = min(ws, hs)
            resimg = cv2.resize(draw_img, (0, 0), fx = s, fy = s)
            #resimg = np.transpose(resimg, (1, 0, 2))
            nh, nw = resimg.shape[:2]
            #print nw, nh
            self.yoff, self.xoff = (self.height - nh)/2, (self.width - nw)/2
            self.scale = s
            img = Image.fromarray(resimg)
            img = ImageTk.PhotoImage(img)
            self.canvas.configure(image=img)
            self.canvas._image_cache = img
            
            
            if self.ih.zoom > 0:
                total_area, img_area = self.sum_areas()
                self.l1.configure(text="Cell area: " + str(round(total_area, 3)) + " um2")
                self.l2.configure(text="All area: " + str(round(img_area, 3)) + " um2")
            else:
                self.l1.configure(text="")
                self.l2.configure(text="")
        #self.update()
        
    def setup_screen(self):
        self.update()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.width, self.height = width, height
        self.draw()
        
    #def start_loop(self):
    #    while 1:
    #        self.update()

if __name__ == "__main__":
    root = root_window()
    #root.start_loop()
    root.mainloop()