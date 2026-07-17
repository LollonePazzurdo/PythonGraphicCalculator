import numpy as np
from math import *
import cv2
from .colors import *
import time
import multiprocessing
import os

PLOTS_DIR = "plots"

class Plot:
    subs_dict = {"^":"**", "X":"x", "Y":"y", "PI":"pi"}
    line_alpha = 255 
    area_alpha = 64
    
    def __init__(self, equation:str, color:tuple[int,int,int], size:int, zoom:float, domain:str = "True", center:tuple[float, float] = (0.0, 0.0)):
        self.size = size
        self.side = size*2+1
        self.zoom = zoom
        self.color = color
        self.domain = domain
        self.text_offset = 0
        self.center = center
        self.equation = equation

        self.img = np.zeros((self.side,self.side,4), np.uint8)


    def __repr__(self)->str:
        return f"equation = \"{self.equation}\"\ncolor = {self.color}\nsize = {self.size}\nzoom = {self.zoom}\ncenter = {self.center}"
    

    def set_color(self, x:float, y:float, color:tuple):
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)
        self.img[self.to_coords(x,y)] = color
        

    def draw(self):
        print(f"Drawing {self.equation}")
        equation, domain = self.equation, self.domain
        final_color = (self.color[0], self.color[1], self.color[2], self.line_alpha)
        
        if ">" in equation or "<" in equation or ">=" in equation or "<=" in equation:
            equation = f"int(not ({self.equation}))"
            final_color = (self.color[0], self.color[1], self.color[2], self.area_alpha)
                
        elif "=" in equation: 
            equation = equation.split("=")
            equation = f"{equation[0]} - ({equation[1]})"

             
            
        equation = fix_text(equation)
        domain = fix_text(domain)
            

        function = eval("lambda x,y: "+equation)
        domain = eval("lambda x,y: "+domain)

        signs = np.zeros((self.side+2, self.side+2))

        for x in range(-self.size-1, self.size+2):
            for y in range(-self.size-1, self.size+2):
                try:
                    signs[x+self.size+1, y+self.size+1] = np.sign(function(x/self.zoom + self.center[0], y/self.zoom + self.center[1]))
                except (ZeroDivisionError, ValueError, TypeError):
                    signs[x+self.size+1, y+self.size+1] = 10

        #self.time0 = time.perf_counter()
        for x in range(-self.size, self.size+1):
            for y in range(-self.size, self.size+1):
                try:
                    defined = domain(x/self.zoom + self.center[0], y/self.zoom + self.center[1])
                except (ZeroDivisionError, ValueError, TypeError):
                    defined = False
                    
                if defined:
                    right = signs[x+self.size+2, y+self.size+1]
                    left = signs[x+self.size, y+self.size+1]
                    top = signs[x+self.size+1, y+self.size+2]
                    bottom =  signs[x+self.size+1, y+self.size]
                    s = right + left + top + bottom

                    if abs(s)<3:
                        self.set_color(x,y, final_color)


    def draw_text(self, i:int=1):

        font_size = .7*self.size/400
        self.text_offset += (font_size*25+15)*(i+1)*self.size/400
        b,g,r = self.color
        
        text = self.equation
        if self.domain!="True":
            text += f" {{{self.domain}}}"

        self.img = cv2.putText(
            img = self.img,
            text = text,
            org = (round(15*self.size/400), round(self.text_offset)),
            fontFace = cv2.FONT_HERSHEY_DUPLEX,
            fontScale = font_size,
            color = (b,g,r,255),
            thickness = 1,
            lineType=cv2.QT_FONT_BOLD)
        

    def show(self):
        cv2.imshow("by Lollo's Graphics", self.img)
        while True:
            cv2.waitKey(1)
    

    def save(self, filename:str="img.png"):
        cv2.imwrite(filename, self.img)

    
    def to_coords(self,x:float, y:float)->tuple:
        i = -y+self.side//2
        j = x+self.side//2
        return round(i), round(j)



class Graph:
    def __init__(self, view:float=10, size:int=400, axes:bool=True, scale:int=1, dark_mode:bool=True, center:tuple[float, float] = (0,0)):
        self.scale = scale
        self.size = size
        self.side = size*2+1
        self.zoom = size/view
        self.dark_mode = dark_mode
        self.center = center
        self.default_color = int(dark_mode)*255, int(dark_mode)*255, int(dark_mode)*255
        self.axes = axes
        
        self.reset()
        
        if not os.path.exists(PLOTS_DIR):
            os.mkdir(PLOTS_DIR)


    def __repr__(self)->str:
        return f"scale = {self.scale}\nsize = {self.size}\nside = {self.side}\nzoom = {self.zoom}\ndark_mode = {self.dark_mode}\ncenter = {self.center}"


    def reset(self):
        self.img = np.zeros((self.side,self.side,3), np.uint8)
        if self.dark_mode:
            self.img.fill(25)
        else:
            self.img.fill(255)

        if self.axes:
            for i in range(-self.size, self.size+1):
                self.set_color(-self.center[0]*self.zoom, i, GRAY)
                self.set_color(i, -self.center[1]*self.zoom, GRAY)
    

    def to_coords(self,x:float, y:float)->tuple:
        i = -y+self.side//2
        j = x+self.side//2
        return round(i), round(j)
    

    def set_color(self, x:float,y:float, color):
        x, y = self.to_coords(x,y)
        if x>=0 and y>=0 and x<self.side and y<self.side:
            self.img[(x,y)] = color


    def get_plots(self, equations:list[str], colors:list[tuple[int,int,int]]=None, domains:list[str]=None)->list:
        plots = []
        if not colors:
            colors = [self.default_color]

        if not domains:
            domains = ["True"]*len(equations)
        elif len(domains) < len(equations):
            domains = domains + ["True"]*(len(equations)-len(domains))

        for i,eq in enumerate(equations):
            plots.append(Plot(
                equation=eq, 
                color=colors[i%len(colors)], 
                size=self.size, 
                zoom=self.zoom,
                domain=domains[i],
                center=self.center))
            
        return plots


    def draw_plots(self, plots:list[Plot], write_text:bool=True):
        for file in os.listdir(PLOTS_DIR):
            os.remove(os.path.join(PLOTS_DIR, file))

        processes = []
        for i,p in enumerate(plots):
            processes.append(multiprocessing.Process(target=draw_process, args=(p.equation, p.color, p.size, p.zoom, p.domain, i, write_text, self.center)))
            while len(multiprocessing.active_children()) > multiprocessing.cpu_count(): pass #so the pc wont be overloaded with processes
            processes[i].start()

        for p in processes:
            p.join()
        
        for i,p in enumerate(plots):
            p.img = cv2.imread(os.path.join(PLOTS_DIR, f"{i}.png"), cv2.IMREAD_UNCHANGED)
            self.overlay_plot(p)

    
    def overlay_plot(self, plot:Plot):
        alpha = plot.img[:,:,3:4] / 255
        self.img[:,:,:] = alpha * plot.img[:,:,:3] + (1-alpha) * self.img


    def draw(self, equation, color=None, domain:str = "True"):
        if not color:
            color = self.default_color

        plot = Plot(equation, color, self.size, self.zoom, domain, center=self.center)
        plot.draw()
        self.overlay_plot(plot)

     
    def point(self, px, py, color=None,  r=5):
        if not color:
            color = self.default_color

        circle=lambda x,y: (x-px)**2 + (y-py)**2 - (r/self.zoom)**2
        
        _px = round(px*self.zoom)
        _py = round(py*self.zoom)
        for x in range(_px-r, _px+r +1):
            for y in range(_py-r, _py+r +1):
                if circle(x/self.zoom, y/self.zoom)<0 and (x<=self.size and y<=self.size and x>=-self.size and y>=-self.size):
                    self.set_color(x,y, color)
    

    def show(self):
        img_tmp = cv2.resize(self.img, (self.side*self.scale, self.side*self.scale), interpolation = cv2.INTER_AREA)
        cv2.imshow("by Lollo's Graphics", img_tmp)
        while True:
            cv2.waitKey(1)

    
    def save(self, filename:str = "img.png"):
        cv2.imwrite(filename, self.img)



def draw_process(equation:str, color:tuple[int,int,int], size:int, zoom:float, domain:str, i:int, write_text:bool, center:tuple[float,float]):
    p = Plot(equation=equation, color=color, size=size, zoom=zoom, domain=domain, center=center)
    p.draw()
    if write_text:
        p.draw_text(i=i)
    p.save(os.path.join(PLOTS_DIR, f"{i}.png"))


def fix_text(text:str):
        for key in Plot.subs_dict:
            text = text.replace(key, Plot.subs_dict[key])
        return text
        