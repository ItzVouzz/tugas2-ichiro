from rally_navigator.route import find_route, find_route_dfs
from rally_navigator.grid import GridMap, Cell
from rally_wasit.stage import generate_stage

print("| Seed | Panjang BFS | Panjang DFS | Dikunjungi BFS | Dikunjungi DFS |")
print("|---|---|---|---|---|")

for seed in range(1, 11):
    stage = generate_stage(seed)
    
    start_cell = Cell(stage.start[0], stage.start[1])
    finish_cell = Cell(stage.finish[0], stage.finish[1])
    
    grid = GridMap(stage.width, stage.height, stage.rocks, start_cell, finish_cell)

    route_bfs, visited_bfs = find_route(grid)
    route_dfs, visited_dfs = find_route_dfs(grid)

    panjang_bfs = len(route_bfs) - 1 if route_bfs else 0
    panjang_dfs = len(route_dfs) - 1 if route_dfs else 0

    print(f"| {seed} | {panjang_bfs} | {panjang_dfs} | {visited_bfs} | {visited_dfs} |")