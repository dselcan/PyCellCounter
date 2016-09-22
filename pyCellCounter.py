import cv2
import numpy as np
from PIL import Image, ImageTk
import Tkinter as tk
import tkFileDialog as tkfd
import tkMessageBox as tkmb
import ttk
import os
import pickle

from img_manip import *

VERSION_STRING = "0.1"

TSCALE = 0.5
CATS = 10
CAT_COLORS = [[255,0,0],[0,255,0],[255,255,0],[255,0,255],[255,255,255],[0,255,255],[255,70,0],[150,190,60],[0,150,200],[0,60,110]]
FINAL_OFFSET = 10
OFFSET = [FINAL_OFFSET, FINAL_OFFSET*1.6]

ZOOM_VALS = [None,
        [(2030, 1825), (2452, 1825), 50.0],
        [(2163, 1798), (2481, 1798), 25.0],
        [(595, 1080), (734, 1080), 2.0],
        [(595, 1080), (734, 1080), 2.0],
        [(558, 1080), (771, 1080), 2.0],
        [(577, 1080), (752, 1080), 1.0],
        [(588, 1080), (743, 1080), 0.5]]
ZOOM_COLOR = [64, 128, 64]

LINE_WIDTH = 2

ROUND = 3

class root_window(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("800x600")
        self.iconbitmap('icon.ico')
        self.title("PyCounter")
        
        self.previous_img_dir = "."
        self.previous_mask_dir = "."
        
        menubar=tk.Menu(self)
        filemenu=tk.Menu(menubar,tearoff=0)
        #filemenu.add_command(label="Save",       command=self.save_all)
        #filemenu.add_separator()
        filemenu.add_command(label="Load Image", command=self.load_image)
        filemenu.add_command(label="Save Image", command=self.save_image)
        filemenu.add_separator()
        filemenu.add_command(label="Load Marks", command=self.load_marks)
        filemenu.add_command(label="Save Marks", command=self.save_marks)
        filemenu.add_separator()
        #filemenu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
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
        
        self.font_var = tk.IntVar()
        self.font_var.set(1)
        fontmenu=tk.Menu(menubar,tearoff=0)
        fontmenu.add_radiobutton(label="Small", variable=self.font_var, value=1, command = self.change_font)
        fontmenu.add_radiobutton(label="Medium", variable=self.font_var, value=2, command = self.change_font)
        fontmenu.add_radiobutton(label="Large", variable=self.font_var, value=3, command = self.change_font)
        menubar.add_cascade(label="Font size", menu=fontmenu)
        
        helpmenu=tk.Menu(menubar,tearoff=0)
        helpmenu.add_command(label="About", command=self.about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        
        self.config(menu=menubar)
        
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(side = "left", fill = "both", expand = "true")
        self.canvas = tk.Label(canvas_frame)
        self.canvas.bind("<Button-1>", self.mark)
        self.canvas.bind("<Button-3>", self.unmark)
        #self.canvas.bind("<B1-Motion>", self.test)
        #self.canvas.bind("<ButtonRelease-1>", self.test)
        #self.bind("<Return>", self.test2)
        self.canvas.pack(side = "left", fill = "both", expand = "true")
        
        side = ttk.LabelFrame(self, padding = 4)
        side.pack(side = "left", fill="y")
        
        tools = ttk.Frame(side)
        tools.pack(side = "top", fill = "x")
        
        self.action = "none"
        self.count_button = tk.Button(tools, text="Count", relief="raised", command=self.select_count)
        self.count_button.pack(side = "top", fill = "x", expand = "true")
        
        self.line_button = tk.Button(tools, text="Line", relief="raised", command=self.select_line)
        self.line_button.pack(side = "top", fill = "x", expand = "true")
        
        categories = ttk.LabelFrame(tools, text = "Category", padding = 4)
        categories.pack(side = "top")
        
        self.cats = []
        self.selected = tk.IntVar()
        for i in range(CATS):
            self.cats.append(ttk.Radiobutton(categories, text="Category " + str(i), variable=self.selected, value=i, command = self.update_category))
            self.cats[-1].pack(side = "top")
        
        info = ttk.Frame(side)
        info.pack(side = "bottom", fill = "x")
        self.line_size = ttk.Label(info, width = 22)
        self.line_size.pack(side="top", fill = "x", expand = "true")
        
        self.ih = None
        self.yoff, self.xoff = (0,0)
        self.scale = 1.0
        
        self.start_pos = (0,0)
        
        self.setup_screen()
        self.bind("<Configure>", self.on_resize)

    """
    def undo(self):
        if self.ih:
            if self.line.get():
                self.ih.undo_line(self.selected.get())
            else:
                self.ih.undo_mark(self.selected.get())
            self.draw()
    """
    
    def about(self):
        tkmb.showinfo("About", "Version " + VERSION_STRING + " of pyCellCounter.")
    
    def update_category(self):
        self.update_line_size()
        
    def change_zoom(self):
        if self.ih:
            self.ih.zoom = self.zoom_var.get()
        self.draw()
        
    def change_font(self):
        self.draw()
        
    def update_line_size(self):
        if self.ih and self.ih.lines[self.selected.get()]:
            if self.ih.zoom:
                self.line_size.configure(text="Line size: " + str(round(self.ih.get_line_size(self.selected.get(), ZOOM_VALS[self.ih.zoom]), ROUND)) + " um")
            else:
                self.line_size.configure(text="Zoom not selected.")
        else:
            self.line_size.configure(text="")
        
    def load_image(self):
        fn =  tkfd.askopenfilename(initialdir=self.previous_img_dir, defaultextension=".png", filetypes=[('Image file', (".png", ".tif", ".tiff", ".bmp", ".jpg", ".jpeg", ".gif"))])
        self.zoom_var.set(0)
        if fn:
            self.ih = ImageHolder(CATS, fn)
            try:
                self.previous_img_dir = os.path.split(fn)[0]
            except:
                print "Warning."
                
        self.draw()
        
    def save_image(self):
        if self.ih:
            fn =  tkfd.asksaveasfilename(initialdir=self.previous_img_dir, defaultextension=".png", initialfile=self.ih.name + "_counted.png", filetypes=[('Image file', '.png')])
        else:
            fn = None
        if fn:
            img = self.prepare_image()
            img = self.mark_image(img)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            try:
                cv2.imwrite(fn, img)
                self.previous_img_dir = os.path.split(fn)[0]
            except:
                print "Warning."
            #else:
                #self.ih.saved = True
        #self.draw()
        
    def load_marks(self):
        if self.ih:
            fn =  tkfd.askopenfilename(initialdir=self.previous_mask_dir, defaultextension=".dat", filetypes=[('Pycounter marks file', '.dat')])
        else:
            fn = None
        if fn:
            f = open(fn, "r")
            try:
                self.ih.marks, self.ih.zoom, self.ih.lines = pickle.load(f)
            except: 
                f.close()
                f = open(fn, "r")
                self.ih.marks = pickle.load(f)
                self.ih.clear_lines()
            try:
                self.previous_mask_dir = os.path.split(fn)[0]
            except:
                print "Warning."
                
            f.close()
            
        self.zoom_var.set(self.ih.zoom)
        self.ih.update_values()
        self.draw()    
        
    def save_marks(self):
        if self.ih:
            fn =  tkfd.asksaveasfilename(initialdir=self.previous_mask_dir, defaultextension=".dat", initialfile=self.ih.name + "_marks.dat", filetypes=[('Pycounter marks file', '.dat')])
        else:
            fn = None
            
        if fn:
            try:
                f = open(fn, "w")
                pickle.dump((self.ih.marks, self.ih.zoom, self.ih.lines), f)
                f.close()
                self.previous_mask_dir = os.path.split(fn)[0]
            except:
                print "Warning."
                
    def select_count(self):
        if self.ih:
            if self.action == "count":
                self.count_button.configure(relief="raised")
                self.action = "none"
            else:
                self.count_button.configure(relief="sunken")
                self.line_button.configure(relief="raised")
                self.action = "count"
            self.draw()
            
    def select_line(self):
        if self.ih:
            if self.action == "line":
                self.line_button.configure(relief="raised")
                self.action = "none"
            else:
                self.count_button.configure(relief="raised")
                self.line_button.configure(relief="sunken")
                self.action = "line"
            self.draw()
        
    def mark(self, event):
        if self.ih:
            pos = int((event.x - self.xoff)/self.scale), int((event.y - self.yoff)/self.scale)
            if self.action == "line":
                self.ih.add_line(pos, self.selected.get())
            elif self.action == "count":
                self.ih.add_mark(pos, self.selected.get())
            self.draw()
        
    def unmark(self, event):
        if self.ih:
            pos = int((event.x - self.xoff)/self.scale), int((event.y - self.yoff)/self.scale)
            if self.action == "line":
                self.ih.remove_line(pos, self.selected.get())
            elif self.action == "count":
                self.ih.remove_mark(pos, self.selected.get())
            self.draw()
        
    def on_resize(self, event):
        if event.widget == self and (event.width != self.width or event.height != self.height):
            self.setup_screen()

    def prepare_image(self):
        ih = self.ih
        img = np.array(ih.image, dtype=np.uint8)
        
        if ih.zoom > 0:
            img = cv2.line(img, ZOOM_VALS[ih.zoom][0], ZOOM_VALS[ih.zoom][1], ZOOM_COLOR, 2*LINE_WIDTH)

        for i, l in enumerate(ih.lines):
            ls = len(l)
            if ls == 1:
                img = cv2.line(img, tuple(l[0]), tuple(l[0]), CAT_COLORS[i], LINE_WIDTH)
            else:
                for j in range(ls-1):
                    img = cv2.line(img, tuple(l[j]), tuple(l[j+1]), CAT_COLORS[i], LINE_WIDTH)
            
        for m in ih.marks:
            if m[0] < 10:
                #print m[0]
                tscale = TSCALE*self.font_var.get()
                p = (m[1][0] - int(OFFSET[0]*tscale), m[1][1] + int(OFFSET[0]*tscale))
            else:
                p = (m[1][0] - int(OFFSET[1]*tscale), m[1][1] + int(OFFSET[0]*tscale))
            cv2.putText(img, str(m[0]), p, cv2.FONT_HERSHEY_DUPLEX, tscale, CAT_COLORS[m[2]], thickness=int(2*tscale))
            
        return img
        
    def mark_image(self, img):
        img = cv2.copyMakeBorder(img, 0, (1+CATS*4)*FINAL_OFFSET, 0, 0, cv2.BORDER_CONSTANT, (0, 0, 0))
        ih = self.ih
        
        for i in range(CATS):
            text = "Category " + str(i) + " total: " + str(ih.mnums[i])
            if ih.zoom:
                text += ";      Line " + str(round(self.ih.get_line_size(i, ZOOM_VALS[self.ih.zoom]), ROUND)) + " um"
            cv2.putText(img, text, (ih.w/50, ih.h + 3*FINAL_OFFSET + i*2*2*FINAL_OFFSET), cv2.FONT_HERSHEY_DUPLEX, 1.0, CAT_COLORS[i])
           
        return img
            
    def draw(self):
        self.update_line_size()
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
        self.update()
        
    def setup_screen(self):
        self.update()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.width, self.height = width, height
        self.draw()
        

if __name__ == "__main__":
    root = root_window()
    root.mainloop()