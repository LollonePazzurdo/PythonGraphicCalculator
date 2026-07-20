import threading
import time

from graphiccalculator import *

COLORS = [CYAN, LIME, ORANGE, PINK, PURPLE, RED, YELLOW]
 
    
def draw_sequential_test(g: Graph, eqs:list[str]):
    t0 = time.perf_counter()
    for i,eq in enumerate(eqs):
        g.draw(eq, color=COLORS[i%len(COLORS)])
    return time.perf_counter()-t0

def draw_multithreading_test(g: Graph, eqs:list[str]):
    t0 = time.perf_counter()
    plots = g.get_plots(equations=eqs, colors=COLORS)
    g.draw_plots_mt(plots)
    return time.perf_counter()-t0


def draw_multiprocessing_test(g: Graph, eqs:list[str]):
    t0 = time.perf_counter()
    plots = g.get_plots(equations=eqs, colors=COLORS)
    g.draw_plots_mp(plots)
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
    "y>=x+4",
    "x>=y+4",
    "x>=3",
]

if __name__ == "__main__":
    #print(f"Sequential time: {draw_sequential_test(g, eqs)}")
    #cv2.imshow("Graph", g.img)
    #cv2.waitKey(0)
    #g.reset()


    print(f"Multithreding time: {draw_multithreading_test(g, eqs)}")
    cv2.imshow("Graph", g.img)
    cv2.waitKey(0)
    g.reset()


    print(f"Multiprocessing time: {draw_multiprocessing_test(g, eqs)}")
    cv2.imshow("Graph", g.img)
    cv2.waitKey(0)
    g.reset()
