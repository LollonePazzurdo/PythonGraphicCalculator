import numpy as np
from math import *
from PIL import Image, ImageDraw, ImageFont
from .colors import *
import multiprocessing
import threading
import os
import re
from concurrent.futures import ThreadPoolExecutor

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

        self.reset()


    def __repr__(self)->str:
        return f"equation = \"{self.equation}\"\ncolor = {self.color}\nsize = {self.size}\nzoom = {self.zoom}\ncenter = {self.center}"
    
    
    def reset(self):
        self.img = np.zeros((self.side,self.side,4), np.uint8)

    
    def set_color(self, x:float, y:float, color:tuple):
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)
        self.img[self.to_coords(x,y)] = color
        

    def draw(self, index:int=None, write_text=True):
        print(f"Drawing {self.equation}\n", end="") #to fix late newline during multithreading
        equation, domain = self.equation, self.domain
    
        inequality_match = re.search(r">=|<=|>|<", equation)

        if inequality_match:
            self._draw_inequality(equation, domain, index, inequality_match)
        else:
            self._draw_equality(equation, domain, index)
        
        if write_text:
            self.draw_text(index=index)
            
        self.save(os.path.join(PLOTS_DIR, f"{index}{'' if self.draw_text else '_tmp'}.png"))

    def _draw_equality(self, equation:str, domain:str, index:int|None):
        final_color = (self.color[0], self.color[1], self.color[2], self.line_alpha)
        if "==" in equation:
            left, right = equation.split("==", 1)
            equation = f"({left}) - ({right})"
        elif "=" in equation and not any(op in equation for op in ("==", ">=", "<=")):
            left, right = equation.split("=", 1)
            equation = f"({left}) - ({right})"

        equation = fix_text(equation)
        domain = fix_text(domain)
        X, Y = self._create_mesh()
        eval_env = self._build_eval_env(X, Y)

        with np.errstate(all='ignore'):
            Z = self._eval_expression(equation, eval_env, X.shape, is_inequality=False)
            signs = np.sign(Z)
            signs[~np.isfinite(signs)] = 10.0
            D = self._eval_domain(domain, eval_env, X.shape)

        right = signs[2:, 1:-1]
        left = signs[:-2, 1:-1]
        top = signs[1:-1, 2:]
        bottom = signs[1:-1, :-2]
        s = right + left + top + bottom
        defined = D[1:-1, 1:-1]
        mask = (np.abs(s) < 3) & defined

        self.img[mask[:, ::-1].T] = final_color


    def _draw_inequality(self, equation:str, domain:str, index:int|None, inequality_match):
        final_color = (self.color[0], self.color[1], self.color[2], self.area_alpha)
        is_boundary_inequality = inequality_match.group() in (">=", "<=")
        equation = fix_text(f"({equation})")
        domain = fix_text(domain)
        X, Y = self._create_mesh()
        eval_env = self._build_eval_env(X, Y)

        with np.errstate(all='ignore'):
            Z = self._eval_expression(equation, eval_env, X.shape, is_inequality=True)
            D = self._eval_domain(domain, eval_env, X.shape)

        defined = D[1:-1, 1:-1]
        if isinstance(Z, np.ndarray) and Z.dtype == bool:
            mask = Z[1:-1, 1:-1] & defined
        else:
            mask = np.full((self.side-2, self.side-2), bool(Z), dtype=bool) & defined

        self.img[mask[:, ::-1].T] = final_color


    def _create_mesh(self):
        coords_x = np.arange(-self.size - 1, self.size + 2, dtype=np.float64) / self.zoom + self.center[0]
        coords_y = np.arange(-self.size - 1, self.size + 2, dtype=np.float64) / self.zoom + self.center[1]
        return np.meshgrid(coords_x, coords_y, indexing='ij')

    def _build_eval_env(self, X, Y):
        return {
            "x": X, "y": Y,
            "sin": np.sin, "cos": np.cos, "tan": np.tan,
            "asin": np.arcsin, "acos": np.arccos, "atan": np.arctan,
            "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
            "exp": np.exp, "log": np.log, "log10": np.log10,
            "abs": np.abs, "sqrt": np.sqrt,
            "pi": np.pi, "e": np.e
        }

    def _eval_expression(self, expression:str, eval_env:dict, shape:tuple, is_inequality:bool):
        try:
            Z = eval(expression, {"__builtins__": None}, eval_env)
            if isinstance(Z, bool):
                return np.full(shape, float(Z), dtype=np.float64) if not is_inequality else np.full(shape, Z, dtype=bool)
            if isinstance(Z, (int, float, np.integer, np.floating)):
                return np.full(shape, float(Z), dtype=np.float64)
            if isinstance(Z, np.ndarray) and Z.dtype == bool:
                return Z.astype(bool) if is_inequality else Z.astype(np.float64)
            return Z
        except Exception:
            return np.full(shape, False, dtype=bool) if is_inequality else np.full(shape, 10.0, dtype=np.float64)

    def _eval_domain(self, domain:str, eval_env:dict, shape:tuple):
        try:
            D = eval(domain, {"__builtins__": None}, eval_env)
            if isinstance(D, bool):
                return np.full(shape, D, dtype=bool)
            if isinstance(D, (int, float, np.integer, np.floating)):
                return np.full(shape, bool(D), dtype=bool)
            return D.astype(bool)
        except Exception:
            return np.zeros(shape, dtype=bool)


    def draw_text(self, index:int=1):

        font_size = max(12, int(20*self.size/400))
        self.text_offset += (font_size+5)*(index+1)*self.size/400
        b,g,r = self.color
        
        text = self.equation
        if self.domain!="True":
            text += f" {{{self.domain}}}"

        pil_img = Image.fromarray(self.img, mode="RGBA")
        draw = ImageDraw.Draw(pil_img)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

        draw.text((round(15*self.size/400), round(self.text_offset)), text, fill=(b,g,r,255), font=font)
        self.img = np.array(pil_img)
        

    def show(self):
        pil_img = Image.fromarray(self.img[:, :, [2, 1, 0, 3]], mode="RGBA")
        pil_img.show(title="by Lollo's Graphics")
    

    def save(self, filename:str="img.png"):
        pil_img = Image.fromarray(self.img[:, :, [2, 1, 0, 3]], mode="RGBA")
        pil_img.save(filename)

    
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
            
            
    def draw_plots_mt(self, plots:list[Plot], write_text:bool=True):
        for file in os.listdir(PLOTS_DIR):
            os.remove(os.path.join(PLOTS_DIR, file))
        
        true_plots = plots.copy()
        for plot in true_plots:
            if re.search(r">=|<=", plot.equation):
                new_eq = plot.equation.replace(">", "").replace("<", "")
                new_plot = Plot(new_eq, plot.color, plot.size, plot.zoom, plot.domain, plot.center)
                plots.append(new_plot)
                

        max_workers = os.cpu_count() or 4
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(p.draw, i, i<len(true_plots))
                for i, p in enumerate(plots)
            ]
            for f in futures:
                try:
                    f.result()
                except Exception as e:
                    print(f"Error drawing plot thread: {e}")
        
        for p in plots:
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
    

    def show(self):
        pil_img = Image.fromarray(self.img[:, :, ::-1], mode="RGB")
        if self.scale != 1:
            pil_img = pil_img.resize((self.side*self.scale, self.side*self.scale), Image.Resampling.BOX)
        pil_img.show(title="by Lollo's Graphics")

    
    def save(self, filename:str = "img.png"):
        pil_img = Image.fromarray(self.img[:, :, ::-1], mode="RGB")
        pil_img.save(filename)




def fix_text(text:str):
        for key in Plot.subs_dict:
            text = text.replace(key, Plot.subs_dict[key])
        return text
        