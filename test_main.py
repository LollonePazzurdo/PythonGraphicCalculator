import time

from graphiccalculator import *

COLORS = [CYAN, LIME, ORANGE, PINK, PURPLE, RED, YELLOW]
 
    
def draw_sequential_test(g: Graph, eqs:list[str]):
    t0 = time.perf_counter()
    for eq in eqs:
        g.draw(eq, color=colors.r_color())
    return time.perf_counter()-t0

def draw_multithreading_test(g: Graph, eqs:list[str]):
    t0 = time.perf_counter()
    plots = g.get_plots(equations=eqs, colors=COLORS)
    g.draw_plots_mt(plots)
    return time.perf_counter()-t0




scale = 1
g = Graph(
    view=10, 
    size=400//scale,
    axes=True, 
    scale=scale, 
    dark_mode=True, 
    center=(0,0)
)


eqs = [
    "x>y+2",
    "x>=-y",
]

if __name__ == "__main__":
    print(f"Multithreding time: {draw_multithreading_test(g, eqs)}")
    g.save("multithreading.png")
    g.show()
    g.reset()


