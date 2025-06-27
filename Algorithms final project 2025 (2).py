import turtle
import random
import tkinter as tk
from tkinter import ttk, messagebox
import heapq
from collections import deque
import time
import matplotlib.pyplot as plt

# ------------------ Global Settings ------------------
sizex, sizey = 20, 20
Walls = []
DRAW = True  

# ------------------ Maze Generator ------------------
def mazegenerate(width, height):
    grid = [[[1, 1, 1, 1] for _ in range(width)] for _ in range(height)]
    visited = [[False] * width for _ in range(height)]

    def in_bounds(x, y): return 0 <= x < width and 0 <= y < height

    def carve(x, y):
        visited[y][x] = True
        dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and not visited[ny][nx]:
                if dx == 0 and dy == -1:
                    grid[y][x][0] = 0; grid[ny][nx][1] = 0
                elif dx == 0 and dy == 1:
                    grid[y][x][1] = 0; grid[ny][nx][0] = 0
                elif dx == -1 and dy == 0:
                    grid[y][x][2] = 0; grid[ny][nx][3] = 0
                elif dx == 1 and dy == 0:
                    grid[y][x][3] = 0; grid[ny][nx][2] = 0
                carve(nx, ny)

    carve(0, 0)
    return grid

# ------------------ Drawing Setup ------------------
def setup_turtle():
    screen = turtle.Screen()
    screen.setup(700, 700)
    screen.setworldcoordinates(0, 0, 700, 700)
    screen.tracer(0)
    pen = turtle.Turtle()
    pen.hideturtle()
    pen.penup()
    return screen, pen

screen, pen = setup_turtle()

# ------------------ Rendering ------------------
def printmaze():
    if not DRAW:
        return
    pen.clear()
    cell = 700 / sizex
    pen.color('black'); pen.width(3)
    pen.penup()
    for y in range(sizey):
        for x in range(sizex):
            top, bottom, left, right = Walls[y][x]
            wx, wy = x * cell, 700 - y * cell
            if top:
                pen.goto(wx, wy); pen.setheading(0); pen.pendown(); pen.forward(cell); pen.penup()
            if bottom:
                pen.goto(wx, wy - cell); pen.setheading(0); pen.pendown(); pen.forward(cell); pen.penup()
            if left:
                pen.goto(wx, wy); pen.setheading(-90); pen.pendown(); pen.forward(cell); pen.penup()
            if right:
                pen.goto(wx + cell, wy); pen.setheading(-90); pen.pendown(); pen.forward(cell); pen.penup()
    screen.update()

def draw_point(x, y, color):
    if not DRAW:
        return
    cell = 700 / sizex
    pen.goto(x * cell + cell / 2, 700 - y * cell - cell / 2)
    pen.dot(cell * 0.6, color)
    pen.penup()

def get_wall_neighbors(x, y):
    dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    nbrs = []
    for i, (dx, dy) in enumerate(dirs):
        nx, ny = x + dx, y + dy
        if 0 <= nx < sizex and 0 <= ny < sizey and Walls[y][x][i] == 0:
            nbrs.append((nx, ny))
    return nbrs

def trace_path(parent, start, end, color):
    node = end
    while node != start:
        draw_point(node[0], node[1], color)
        node = parent[node]
    draw_point(start[0], start[1], 'green'); draw_point(end[0], end[1], 'red')
    screen.update()

# ------------------ Solvers ------------------
def solve_dfs():
    parent = {}; visited = set()

    def dfs(x, y):
        draw_point(x, y, 'lightblue'); screen.update()
        if (x, y) == (sizex - 1, sizey - 1): return True
        visited.add((x, y))
        nbrs = get_wall_neighbors(x, y); random.shuffle(nbrs)
        for nx, ny in nbrs:
            if (nx, ny) not in visited:
                parent[(nx, ny)] = (x, y)
                if dfs(nx, ny): return True
        return False

    printmaze()
    if dfs(0, 0): trace_path(parent, (0, 0), (sizex - 1, sizey - 1), 'blue')
    else: messagebox.showinfo('DFS', 'No path found')

def solve_dijkstra():
    dist = {(0, 0): 0}; parent = {}; pq = [(0, (0, 0))]; visited = set()
    goal = (sizex - 1, sizey - 1)
    while pq:
        d, (x, y) = heapq.heappop(pq)
        if (x, y) in visited: continue
        visited.add((x, y)); draw_point(x, y, '#FFD580'); screen.update()
        if (x, y) == goal: break
        for nx, ny in get_wall_neighbors(x, y):
            nd = d + 1
            if nd < dist.get((nx, ny), float('inf')):
                dist[(nx, ny)] = nd; parent[(nx, ny)] = (x, y)
                heapq.heappush(pq, (nd, (nx, ny)))
    printmaze(); trace_path(parent, (0, 0), goal, 'orange')

def solve_a_star():
    def h(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    start, goal = (0, 0), (sizex - 1, sizey - 1)
    open_set = [(h(start, goal), 0, start)]; parent = {}; g = {start: 0}; visited = set()
    while open_set:
        _, cost, cur = heapq.heappop(open_set)
        if cur in visited: continue
        visited.add(cur); draw_point(cur[0], cur[1], '#D0FFFF'); screen.update()
        if cur == goal: break
        for nx, ny in get_wall_neighbors(*cur):
            tg = cost + 1
            if tg < g.get((nx, ny), float('inf')):
                g[(nx, ny)] = tg; parent[(nx, ny)] = cur
                heapq.heappush(open_set, (tg + h((nx, ny), goal), tg, (nx, ny)))
    printmaze(); trace_path(parent, start, goal, 'cyan')

def solve_dp():
    q = deque([(0, 0)]); visited = {(0, 0)}; parent = {}
    goal = (sizex - 1, sizey - 1)
    while q:
        x, y = q.popleft(); draw_point(x, y, '#E0E0E0'); screen.update()
        if (x, y) == goal: break
        for nx, ny in get_wall_neighbors(x, y):
            if (nx, ny) not in visited:
                visited.add((nx, ny)); parent[(nx, ny)] = (x, y); q.append((nx, ny))
    printmaze(); trace_path(parent, (0, 0), goal, 'magenta')

def solve_dead_fill():
    mg = [[1] * sizex for _ in range(sizey)]
    for y in range(sizey):
        for x in range(sizex):
            if all(Walls[y][x]): mg[y][x] = 0
    dq = deque([(0, 0)]); parent = {}; visited = {(0, 0)}
    while dq:
        x, y = dq.popleft()
        if (x, y) == (sizex - 1, sizey - 1): break
        for nx, ny in get_wall_neighbors(x, y):
            if mg[ny][nx] == 1 and (nx, ny) not in visited:
                visited.add((nx, ny)); parent[(nx, ny)] = (x, y); dq.append((nx, ny))
    path = []; cur = (sizex - 1, sizey - 1)
    while cur != (0, 0): path.append(cur); cur = parent[cur]
    path.append((0, 0))
    printmaze(); draw_point(0, 0, 'green'); draw_point(sizex - 1, sizey - 1, 'red')
    changed = True
    while changed:
        changed = False
        for y in range(sizey):
            for x in range(sizex):
                if (x, y) in path or mg[y][x] == 0: continue
                if sum(mg[ny][nx] for nx, ny in get_wall_neighbors(x, y)) <= 1:
                    mg[y][x] = 0; draw_point(x, y, '#800080'); screen.update(); changed = True
    for x, y in path: draw_point(x, y, '#00FF00')
    screen.update()

def timed_solver(func):
    t0 = time.perf_counter()
    func()
    t1 = time.perf_counter()
    return t1 - t0

# ------------------ Empirical Analysis ------------------
def run_empirical_analysis():
    global DRAW, Walls
    DRAW = False

    # Time on current 20x20 maze
    current = {
        'DFS': timed_solver(solve_dfs),
        'Dijkstra': timed_solver(solve_dijkstra),
        'A*': timed_solver(solve_a_star),
        'DP': timed_solver(solve_dp),
        'DeadEndFill': timed_solver(solve_dead_fill)
    }
    DRAW = True
    printmaze(); draw_point(0,0,'green'); draw_point(sizex-1,sizey-1,'red')
    msg = "Current Maze Timings (20x20):\n\n" + "\n".join(
        f"  • {k:<13}: {v:.4f} s" for k, v in current.items())
    messagebox.showinfo("Current Maze Timings", msg)

    # Generalized timings
    sizes = [10, 20, 30]
    results = {k: [] for k in ['size', 'DFS', 'Dijkstra', 'A*', 'DP', 'DeadEndFill']}

    DRAW = False
    for n in sizes:
        Walls = mazegenerate(n, n)
        globals()['sizex'] = globals()['sizey'] = n
        results['size'].append(n)
        results['DFS'].append(timed_solver(solve_dfs))
        results['Dijkstra'].append(timed_solver(solve_dijkstra))
        results['A*'].append(timed_solver(solve_a_star))
        results['DP'].append(timed_solver(solve_dp))
        results['DeadEndFill'].append(timed_solver(solve_dead_fill))
    DRAW = True

    report = "Empirical Timings (in seconds)\n\n"
    for i, size in enumerate(results['size']):
        report += f"Maze {size}x{size}:\n"
        for key in ['DFS', 'Dijkstra', 'A*', 'DP', 'DeadEndFill']:
            report += f"  • {key:<13}: {results[key][i]:.4f} s\n"
        report += "\n"

    top = tk.Toplevel()
    top.title("Empirical Results")
    txt = tk.Text(top, wrap='none', width=60, height=20)
    txt.pack(expand=True, fill='both')
    ysb = ttk.Scrollbar(top, orient='vertical', command=txt.yview)
    ysb.pack(side='right', fill='y')
    txt.configure(yscrollcommand=ysb.set)
    txt.insert('1.0', report)

    plt.figure()
    for key in ['DFS', 'Dijkstra', 'A*', 'DP', 'DeadEndFill']:
        plt.plot(results['size'], results[key], marker='o', label=key)
    plt.xlabel('Maze Size (N × N)')
    plt.ylabel('Execution Time (s)')
    plt.title('Solver Execution Time vs Maze Size')
    plt.legend()
    plt.tight_layout()
    plt.show()

# ------------------ GUI ------------------
def setup_gui():
    global Walls
    root = tk.Tk(); root.title('Maze GUI')
    ttk.Button(root, text='Generate Maze', command=regen).pack(pady=5)
    sf = ttk.Frame(root); sf.pack(pady=5)
    for i, (n, f) in enumerate([
        ('DFS', solve_dfs),
        ('Dij', solve_dijkstra),
        ('A*', solve_a_star),
        ('DP', solve_dp),
        ('Dead-end', solve_dead_fill),
        ('Empirical', run_empirical_analysis)
    ]):
        ttk.Button(sf, text=n, command=f).grid(row=0, column=i, padx=2)
    root.mainloop()

def regen():
    global Walls
    Walls = mazegenerate(sizex, sizey)
    printmaze(); draw_point(0, 0, 'green'); draw_point(sizex - 1, sizey - 1, 'red')

if __name__ == '__main__':
    Walls = mazegenerate(sizex, sizey)
    setup_gui()
