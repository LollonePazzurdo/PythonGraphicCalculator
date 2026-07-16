import threading

from graphiccalculator import *


def draw_thread_test(g: Graph, eq:str):
    g.draw(eq, color=colors.r_color())
    
    
def draw_sequential_test(g: Graph, eqs:list[str]):
    t0 = time.perf_counter()
    for eq in eqs:
        g.draw(eq, color=colors.r_color())
    return time.perf_counter()-t0

def draw_multithreading_test(g: Graph, eqs:list[str]):
    t0 = time.perf_counter()
    threads = []
    for eq in eqs:
        t = threading.Thread(target=draw_thread_test, args=(g, eq))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return time.perf_counter()-t0


scale = 1
g = Graph(
    view=2, 
    size=400//scale,
    axes=True, 
    scale=scale, 
    dark_mode=True, 
    center=(0,0)
)


eqs = [
    "y=x",
    "y=-x",
    "y=x^2",
    "y=-x^2",
]

print(f"Sequential time: {draw_sequential_test(g, eqs)}")
cv2.imshow("Graph", g.img)
cv2.waitKey(0)
print(f"Parallel time: {draw_multithreading_test(g, eqs)}")
cv2.imshow("Graph", g.img)
cv2.waitKey(0)
