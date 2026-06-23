import customtkinter
from graphiccalculator import *
import threading


#interface
customtkinter.set_appearance_mode("dark") 
customtkinter.set_default_color_theme("dark-blue")

#actual graph
GRAPH_COLORS = ["BLUE", "BLACK", "CYAN", "GREEN", "GRAY", "LIGHTBLUE" ,"LIME", "ORANGE", "PINK", "PURPLE", "RED", "WHITE", "YELLOW"]
DEFAULT_BG = 1              # 0->white | 1->dark
DEFAULT_COLOR = "WHITE"     # one of the the GRAPH_COLORS


class GraphFrame(customtkinter.CTkFrame):
    def __init__(self, master, width, height):
        super().__init__(master=master, width=width, height=height)

        BIG_FONT = customtkinter.CTkFont(size=20, weight="bold")
        SMALL_FONT = customtkinter.CTkFont(size=15, weight="bold")
        
        #first row
        self.graph_entry = customtkinter.CTkEntry(self, width=width-40, height=35, font=BIG_FONT)
        self.graph_entry.grid(row=1, column=1, columnspan=6, padx=(10,10), pady=(10,5)) 

        #sencond row  
        self.domain_label = customtkinter.CTkLabel(self, text="Domain:", width=20, height=30, font=SMALL_FONT)
        self.domain_label.grid(row=2, column=1, pady=(5, 10), padx=(10,0))

        self.domain_entry = customtkinter.CTkEntry(self, width=100, height=30, font=SMALL_FONT)
        self.domain_entry.insert(0, "True")
        self.domain_entry.grid(row=2, column=2, pady=(5, 10), padx=(0,5))

        self.color_str = customtkinter.StringVar(value=DEFAULT_COLOR)
        self.color_optionmenu = customtkinter.CTkOptionMenu(self, height=20, values=GRAPH_COLORS, font=SMALL_FONT, variable=self.color_str)
        self.color_optionmenu.grid(row=2, column=3, pady=(5, 10), padx=(5,5))

        self.destroy_button = customtkinter.CTkButton(self, width=20, height=20, text="X", font=SMALL_FONT, fg_color="darkred", command=self.destroy)
        self.destroy_button.grid(row=2, column=6, pady=(5, 10), padx=(5,10))

    


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.width, self.height = 400, 600
        self.img_thread = None
        BIG_FONT = customtkinter.CTkFont(size=20, weight="bold")
        SMALL_FONT = customtkinter.CTkFont(size=15, weight="bold")

        self.title("by Lollo")
        self.geometry(f"{self.width}x{self.height}")
        #self.maxsize(self.width, self.height)

        #bottom part
        self.bottom_frame = customtkinter.CTkFrame(self, width=self.width, height=50, fg_color="transparent")
        self.bottom_frame.pack(side="bottom")

        self.new_button = customtkinter.CTkButton(self.bottom_frame, width=self.width//2-20, height=50, text="new", command=self.add_graph_frame, font=BIG_FONT)
        self.new_button.grid(row=2, column=1, columnspan= 3, padx=(10,0), pady=(5,10))

        self.draw_button = customtkinter.CTkButton(self.bottom_frame, width=self.width//2-20, height=50, text="draw", font=BIG_FONT, command=self.draw_all)
        self.draw_button.grid(row=2, column=4, columnspan= 3, padx=10, pady=(5,10))

        self.view_label = customtkinter.CTkLabel(self.bottom_frame, width=30, height=30, text="view:", font=SMALL_FONT)
        self.view_label.grid(row=1, column=1, padx=(10,0), pady=5)

        self.view_entry = customtkinter.CTkEntry(self.bottom_frame, width=40, height=30, font=SMALL_FONT)
        self.view_entry.insert(0, "10")
        self.view_entry.grid(row=1, column=2, padx=(0,5), pady=5)

        self.center_label = customtkinter.CTkLabel(self.bottom_frame, width=30, height=30, text="center:", font=SMALL_FONT)
        self.center_label.grid(row=1, column=3, padx=(5,0), pady=5)

        self.center_x_entry = customtkinter.CTkEntry(self.bottom_frame, width=30, height=30, font=SMALL_FONT)
        self.center_x_entry.insert(0, "0")
        self.center_x_entry.grid(row=1, column=4, padx=(0,0), pady=5)
        
        self.center_y_entry = customtkinter.CTkEntry(self.bottom_frame, width=30, height=30, font=SMALL_FONT)
        self.center_y_entry.insert(0, "0")
        self.center_y_entry.grid(row=1, column=5, padx=(0,5), pady=5)

        self.darkbg_var = customtkinter.IntVar()
        self.darkbg_checkbox = customtkinter.CTkCheckBox(self.bottom_frame, width=100, height=30, text = "dark bg",font=SMALL_FONT, variable=self.darkbg_var)
        self.darkbg_var.set(DEFAULT_BG)
        self.darkbg_checkbox.grid(row=1, column=6, padx=(5,10), pady=5)
        


        #top part
        self.top_frame = customtkinter.CTkScrollableFrame(self, width=self.width, height=self.height-70, fg_color="transparent")
        self.top_frame.pack(side="top")
        self.add_graph_frame()

        

    def add_graph_frame(self):
        new_graph_frame = GraphFrame(self.top_frame, width=self.width, height=100)
        new_graph_frame.pack(side="top", pady=5)

    

    def draw_all(self):
        self.draw_button.configure(state=customtkinter.DISABLED)
        

        g = Graph(
            view = eval(fix_text(self.view_entry.get())),
            size=  400,
            dark_mode = self.darkbg_checkbox.get(), 
            center = (eval(fix_text(self.center_x_entry.get())), eval(fix_text(self.center_y_entry.get())))
            )
        boxes = list(self.top_frame.children.values())
        
        texts = []
        colors = []
        domains = []

        for box in boxes:
            text = box.graph_entry.get()
            if text.replace(" ", "") != "":
                texts.append(text)
                colors.append(eval(box.color_optionmenu.get()))
                domains.append(box.domain_entry.get())
        
        plots = g.get_plots(equations=texts, colors=colors, domains=domains)

        self.img_thread = threading.Thread(target=self.draw_thread, args=(g, plots, self.img_thread))
        self.img_thread.start()
         
    
    def draw_thread(self, g:Graph, plots:list[Plot], img_thread:threading.Thread):
        try:
            g.draw_plots(plots)
            self.draw_button.configure(state=customtkinter.NORMAL)
            g.save()
            
            if img_thread and img_thread.is_alive():
                ... #to implement a way to kill the img_thread
            
            g.show()
        except:
            self.draw_button.configure(state=customtkinter.NORMAL)
            print("Error drawing the plots")   
        
        

if __name__=="__main__":
    app = App()
    app.mainloop()