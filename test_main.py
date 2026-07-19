import threading
import time

from graphiccalculator import *


 
    
def draw_sequential_test(g: Graph, eqs:list[str]):
    t0 = time.perf_counter()
    for eq in eqs:
        g.draw(eq, color=colors.r_color())
    return time.perf_counter()-t0

def draw_multithreading_test(g: Graph, eqs:list[str]):
    t0 = time.perf_counter()
    plots = g.get_plots(equations=eqs, colors=[colors.r_color() for _ in range(len(eqs))])
    g.draw_plots_mt(plots)
    return time.perf_counter()-t0


def draw_multiprocessing_test(g: Graph, eqs:list[str]):
    t0 = time.perf_counter()
    plots = g.get_plots(equations=eqs, colors=[colors.r_color() for _ in range(len(eqs))])
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
    "y=cos(x)",
    "y=-cos(x)",
    "x=cos(y)",
    "x=-cos(y)",
    "y=x",
    "y=-x",
    "y=x^2",
    "y=-x^2",
    "y=sin(x)",
    "y=-sin(x)",
    "y=tan(x)",
    "y=-tan(x)",
    "y=sin(x)+cos(x)",
    "y=sin(x)-cos(x)",
    "y=abs(x)",
    "y=-abs(x)",
    "y=sqrt(abs(x))",
    "y=-sqrt(abs(x))",
    "y=exp(x)",
    "y=-exp(x)",
    "y=log(abs(x)+1)",
    "y=-log(abs(x)+1)",
    "y=x^3",
    "y=-x^3",
    "x=y^2",
    "x=-y^2",
    "y=1/x",
    "y=-1/x",
    "y=2*x+1",
    "y=-2*x+1",
    "y=sin(x^2)",
    "y=cos(x^2)",
]

if __name__ == "__main__":
    print(f"Sequential time: {draw_sequential_test(g, eqs)}")
    g.save("sequential.png")
    g.reset()

    print(f"Multithreding time: {draw_multithreading_test(g, eqs)}")
    g.save("multithreading.png")
    g.reset()

    print(f"Multiprocessing time: {draw_multiprocessing_test(g, eqs)}")
    g.save("multiprocessing.png")
    g.reset()
