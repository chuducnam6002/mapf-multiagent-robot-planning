# conflict_detector.py

class Conflict:
    def __init__(self, agent_i, agent_j, loc, t_start, t_end, conflict_type):
        self.agent_i = agent_i
        self.agent_j = agent_j
        self.loc = loc
        self.t_start = t_start
        self.t_end = t_end
        self.type = conflict_type

    def generate_constraints(self):
        # Trả về tuple (agent_id, constraint_tuple)
        # constraint_tuple là 1 tuple phẳng: (id, loc, start, end, type)
        return [
            (self.agent_i, (self.agent_i, self.loc, self.t_start, self.t_end, self.type)),
            (self.agent_j, (self.agent_j, self.loc, self.t_start, self.t_end, self.type))
        ]

def get_conflicts(paths):
    conflicts = []
    num_agents = len(paths)
    for i in range(num_agents):
        for j in range(i + 1, num_agents):
            path_i, path_j = paths[i], paths[j]
            max_t = max(len(path_i), len(path_j))
            for t in range(max_t):
                pos_i = path_i[t] if t < len(path_i) else path_i[-1]
                pos_j = path_j[t] if t < len(path_j) else path_j[-1]
                
                # Vertex Conflict
                if pos_i[0:2] == pos_j[0:2]:
                    conflicts.append(Conflict(i, j, pos_i[0:2], t, t, 'vertex'))
                
                # Edge Conflict
                if t > 0:
                    prev_i = path_i[t-1] if t-1 < len(path_i) else path_i[-1]
                    prev_j = path_j[t-1] if t-1 < len(path_j) else path_j[-1]
                    if pos_i[0:2] == prev_j[0:2] and pos_j[0:2] == prev_i[0:2]:
                        conflicts.append(Conflict(i, j, (prev_i[0:2], pos_i[0:2]), t-1, t, 'edge'))
    return conflicts