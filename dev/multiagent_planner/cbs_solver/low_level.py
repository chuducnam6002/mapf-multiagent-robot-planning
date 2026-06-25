# low_level.py
import heapq

def get_neighbors(curr, grid):
    neighbors = []
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    for dx, dy in directions:
        nx, ny = curr[0] + dx, curr[1] + dy
        if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == 0:
            neighbors.append((nx, ny)) # Luôn trả về tuple
    return neighbors

def st_astar(grid, agent_id, start, goal, constraints):
    # start và goal đã là tuple từ run_cbs.py
    start_node = (start[0], start[1], 0)
    # f_score, t_curr, curr(tuple), path
    open_list = [(heuristic(start, goal), 0, start, [start_node])]
    visited = {} 

    while open_list:
        f, t_curr, curr, path = heapq.heappop(open_list)

        if curr == goal:
            return path

        for neighbor in get_neighbors(curr, grid) + [curr]:
            t_next = t_curr + 1
            
            if is_safe(curr, neighbor, t_curr, t_next, agent_id, constraints):
                # neighbor đã là tuple, nên (neighbor, t_next) là hashable
                state = (neighbor, t_next) 
                if state not in visited or visited[state] > t_next:
                    visited[state] = t_next
                    new_path = path + [(neighbor[0], neighbor[1], t_next)]
                    heapq.heappush(open_list, (t_next + heuristic(neighbor, goal), t_next, neighbor, new_path))
    return None

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def is_safe(u, v, t1, t2, agent_id, constraints):
    # constraints là một set chứa các tuple 5 phần tử: (id, loc, t_start, t_end, type)
    for c in constraints:
        # c là tuple: (c_agent_id, c_loc, c_t_start, c_t_end, c_type)
        if c[0] == agent_id:
            # Vertex conflict: v phải bằng c[1] (loc) và t2 phải bằng c[2] (t_start)
            if c[4] == 'vertex' and v == c[1] and t2 == c[2]:
                return False
            # Edge conflict: (u, v) phải bằng c[1] (loc) và t1 phải bằng c[2] (t_start)
            if c[4] == 'edge' and (u, v) == c[1] and t1 == c[2]:
                return False
    return True