import numpy as np
import Tkinter as tk
import tkFileDialog as tkfd
import ttk

from img_manip_analyze import *
import detection_algos as dalgos

class DetectionWindowAB(tk.Toplevel):
    def __init__(self, ih, canvas, root):
        tk.Toplevel.__init__(self)
        self.wm_title("Alpha/Beta detection")
        self.resizable(0,0)
        
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
        self.ih = ih
        self.canvas = canvas
        self.root = root
        
        self.blur = dalgos.BLUR
        self.blur_label = ttk.Label(self)
        blur_frame = ttk.Frame(self)
        self.blur_slider = ttk.Scale(blur_frame, orient="horizontal", to=100, command=self.update_blur) 
        blur_minus = ttk.Button(blur_frame, text="-", width=1, command=self.blur_down)
        blur_plus = ttk.Button(blur_frame, text="+", width=1, command=self.blur_up)
        self.blur_label.pack(side="top", expand="y")
        self.blur_slider.pack(side="left")
        blur_minus.pack(side="left")
        blur_plus.pack(side="left")
        blur_frame.pack(side="top", expand="y")
        self.set_blur(self.blur, False)
        
        self.threshold = dalgos.THRESHOLD
        self.threshold_label = ttk.Label(self)
        threshold_frame = ttk.Frame(self)
        self.threshold_slider = ttk.Scale(threshold_frame, orient="horizontal", to=100, command=self.update_threshold)
        threshold_minus = ttk.Button(threshold_frame, text="-", width=1, command=self.threshold_down)
        threshold_plus = ttk.Button(threshold_frame, text="+", width=1, command=self.threshold_up)
        self.threshold_label.pack(side="top", expand="y")
        self.threshold_slider.pack(side="left")
        threshold_minus.pack(side="left")
        threshold_plus.pack(side="left")
        threshold_frame.pack(side="top", expand="y")
        self.set_threshold(self.threshold, False)
        
        self.iter = dalgos.ITER
        self.iter_label = ttk.Label(self)
        iter_frame = ttk.Frame(self)
        self.iter_slider = ttk.Scale(iter_frame, orient="horizontal", to=100, command=self.update_iter)
        iter_minus = ttk.Button(iter_frame, text="-", width=1, command=self.iter_down)
        iter_plus = ttk.Button(iter_frame, text="+", width=1, command=self.iter_up)
        self.iter_label.pack(side="top", expand="y")
        self.iter_slider.pack(side="left")
        iter_minus.pack(side="left")
        iter_plus.pack(side="left")
        iter_frame.pack(side="top", expand="y")
        self.set_iter(self.iter, False)
        
        self.area = dalgos.AREA
        self.area_label = ttk.Label(self)
        area_frame = ttk.Frame(self)
        self.area_slider = ttk.Scale(area_frame, orient="horizontal", to=100, command=self.update_area)
        area_minus = ttk.Button(area_frame, text="-", width=1, command=self.area_down)
        area_plus = ttk.Button(area_frame, text="+", width=1, command=self.area_up)
        self.area_label.pack(side="top", expand="y")
        self.area_slider.pack(side="left")
        area_minus.pack(side="left")
        area_plus.pack(side="left")
        area_frame.pack(side="top", expand="y")
        self.set_area(self.area, False)
        
        command_frame = ttk.Frame(self)
        command_frame.pack(side="top", fill="y", expand="true")
        ok_button = ttk.Button(self, text = "OK", command=self.ok)
        ok_button.pack(side="left")
        cancel_button = ttk.Button(self, text = "Cancel", command=self.cancel)
        cancel_button.pack(side="right")
        
        self.update()
        
    def update(self):
        print "Updating"
        self.ih.temp_cells = []
        dalgos.detect_ab(self.ih, self.blur, self.threshold, self.iter, self.area)
        print "Done"
        self.root.draw()
        
    def update_blur(self, value):
        value = float(value)
        #print value
        min = dalgos.BLUR_RANGE[0]/2
        max = dalgos.BLUR_RANGE[1]/2
        value = int(value/100*(max-min) + min)*2 + 1
        self.set_blur(value)
        
    def blur_up(self):
        self.blur = min(dalgos.BLUR_RANGE[1], self.blur + 2)
        self.set_blur(self.blur)
        
    def blur_down(self):
        self.blur = max(dalgos.BLUR_RANGE[0], self.blur - 2)
        self.set_blur(self.blur)
        
    def set_blur(self, value, update=True):
        self.blur = value
        min = dalgos.BLUR_RANGE[0]
        max = dalgos.BLUR_RANGE[1]
        s = float(value - min)/(max-min)*100
        self.blur_label.configure(text="Blur radius: " + str(value))
        self.blur_slider.configure(value=s)
        if update:
            self.update()
        
    def update_threshold(self, value):
        value = float(value)
        #print value
        min = dalgos.THRESHOLD_RANGE[0]
        max = dalgos.THRESHOLD_RANGE[1]
        value = int(value/100*(max-min) + min)
        self.set_threshold(value)
        
    def threshold_up(self):
        self.threshold = min(dalgos.THRESHOLD_RANGE[1], self.threshold + 1)
        self.set_threshold(self.threshold)
        
    def threshold_down(self):
        self.threshold = max(dalgos.THRESHOLD_RANGE[0], self.threshold - 1)
        self.set_threshold(self.threshold)    
        
    def set_threshold(self, value, update=True):
        self.threshold = value
        min = dalgos.THRESHOLD_RANGE[0]
        max = dalgos.THRESHOLD_RANGE[1]
        s = float(value - min)/(max-min)*100
        self.threshold_label.configure(text="Threshold: " + str(value))
        self.threshold_slider.configure(value=s)
        if update:
            self.update()
            
    def update_area(self, value):
        value = float(value)
        #print value
        min = np.log10(dalgos.AREA_RANGE[0])
        max = np.log10(dalgos.AREA_RANGE[1])
        value = value/100*(max-min)+min
        self.set_area(10**value)
        
    def area_up(self):
        mi = np.log10(dalgos.AREA_RANGE[0])
        ma = np.log10(dalgos.AREA_RANGE[1]) 
        val = np.log10(self.area) + (ma-mi)/100
        self.area = min(dalgos.AREA_RANGE[1], 10**val)
        self.set_area(self.area)    
        
    def area_down(self):
        mi = np.log10(dalgos.AREA_RANGE[0])
        ma = np.log10(dalgos.AREA_RANGE[1]) 
        val = np.log10(self.area) -(ma-mi)/100
        self.area = max(dalgos.AREA_RANGE[0], 10**val)
        self.set_area(self.area)    
        
    def set_area(self, value, update=True):
        self.area = value
        min = np.log10(dalgos.AREA_RANGE[0])
        max = np.log10(dalgos.AREA_RANGE[1])
        s = float(np.log10(value) - min)/(max-min)*100
        self.area_label.configure(text="Minimum area: " + str(int(value)))
        self.area_slider.configure(value=s)
        if update:
            self.update()
            
    def update_iter(self, value):
        value = float(value)
        #print value
        min = dalgos.ITER_RANGE[0]
        max = dalgos.ITER_RANGE[1]
        value = int(value/100*(max-min) + min)
        self.set_iter(value)
        
    def iter_up(self):
        self.iter = min(dalgos.ITER_RANGE[1], self.iter + 1)
        self.set_iter(self.iter)
        
    def iter_down(self):
        self.iter = max(dalgos.ITER_RANGE[0], self.iter - 1)
        self.set_iter(self.iter)    
        
    def set_iter(self, value, update=True):
        self.iter = value
        min = dalgos.ITER_RANGE[0]
        max = dalgos.ITER_RANGE[1]
        s = float(value - min)/(max-min)*100
        self.iter_label.configure(text="Morph iterations: " + str(value))
        self.iter_slider.configure(value=s)
        if update:
            self.update()
        
    def cancel(self):
        self.ih.temp_cells = []
        self.root.wait_for_window = False
        self.destroy()
        self.root.draw()
        
    def ok(self):
        self.ih.blur = self.blur
        self.ih.cells = self.ih.temp_cells
        self.ih.temp_cells = []
        self.root.wait_for_window = False
        self.destroy()
        self.root.draw()
        