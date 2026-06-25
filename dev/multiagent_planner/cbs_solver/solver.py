import heapq
from dev.multiagent_planner.cbs_solver.constraint_tree import CTNode
from dev.multiagent_planner.cbs_solver.low_level import st_astar
from dev.multiagent_planner.cbs_solver.conflict_detector import get_conflicts

def cbs_solve(grid, starts, goals):
    # 1. Khởi tạo root paths
    root_paths = [st_astar(grid, i, starts[i], goals[i], set()) for i in range(len(starts))]
    if any(p is None for p in root_paths): 
        return None 

    root = CTNode(constraints=set(), paths=root_paths, cost=sum(len(p) for p in root_paths))
    open_list = [root]
    
    expanded = 0
    while open_list:
        expanded += 1
        P = heapq.heappop(open_list)
        conflicts = get_conflicts(P.paths)
        
        # Nếu hết conflict -> Kết thúc
        if not conflicts:
            return P.paths
        
        # Lấy conflict đầu tiên
        conflict = conflicts[0]
        # [AUDIT] Log loại conflict đang giải quyết
        # print(f"[CBS-Node {expanded}] Type: {conflict.type}, Loc: {conflict.loc}")
        
        constraints_list = conflict.generate_constraints()
        for agent_id, constraint_tuple in constraints_list:
            if constraint_tuple in P.constraints:
                continue
                
            new_constraints = P.constraints.copy()
            new_constraints.add(constraint_tuple)
            
            # Replan cho agent bị ràng buộc
            path = st_astar(grid, agent_id, starts[agent_id], goals[agent_id], new_constraints)
            
            if path:
                # [AUDIT] Đo lường sự thay đổi của lộ trình (Detour)
                old_len = len(P.paths[agent_id])
                new_len = len(path)
                
                new_paths = list(P.paths)
                new_paths[agent_id] = path
                new_cost = sum(len(p) for p in new_paths)
                
                heapq.heappush(open_list, CTNode(new_constraints, new_paths, new_cost))
                
                # In log nếu bạn cần theo dõi mức độ "hy sinh" quãng đường
                # print(f"  -> Replan Agent {agent_id}: {old_len} -> {new_len} steps")
                
    return None