import threading

from graphiccalculator import *


 
    
def draw_sequential_test(g: Graph, eqs:list[str]):
    t0 = time.perf_counter()
    for eq in eqs:
        g.draw(eq, color=colors.r_color())
    return time.perf_counter()-t0

def draw_multithreading_test(g: Graph, eqs:list[str]):

    t0 = time.perf_counter()
    threads = []
    for eq in eqs:
        # race condition is definetly a possibility here.
        t = threading.Thread(target=g.draw, args=(eq,), kwargs={'color': colors.r_color()})
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return time.perf_counter()-t0


def draw_multiprocessing_test(g: Graph, eqs:list[str]):
    t0 = time.perf_counter()
    plots = g.get_plots(equations=eqs, colors=[colors.r_color() for _ in range(len(eqs))])
    g.draw_plots_mp(plots)
    return time.perf_counter()-t0


scale = 2
g = Graph(
    view=2, 
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
]

if __name__ == "__main__":
    print(f"Sequential time: {draw_sequential_test(g, eqs)}")
    cv2.imshow("Graph", g.img)
    cv2.waitKey(0)
    g.reset()


    print(f"Multithreding time: {draw_multithreading_test(g, eqs)}")
    cv2.imshow("Graph", g.img)
    cv2.waitKey(0)
    g.reset()


    print(f"Multiprocessing time: {draw_multiprocessing_test(g, eqs)}")
    cv2.imshow("Graph", g.img)
    cv2.waitKey(0)
    g.reset()
