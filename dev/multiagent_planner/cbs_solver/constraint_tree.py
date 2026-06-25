# constraint_tree.py

class CTNode:
    def __init__(self, constraints=None, paths=None, cost=0):
        """
        constraints: Tập hợp các ràng buộc, mỗi ràng buộc là một dict hoặc tuple:
                     {'agent_id': int, 'loc': (x, y), 't_start': int, 't_end': int, 'type': str}
        paths: Danh sách các lộ trình của các agent.
        cost: Tổng chi phí của các lộ trình (thường là tổng thời gian đến đích).
        """
        self.constraints = constraints if constraints is not None else set()
        self.paths = paths if paths is not None else []
        self.cost = cost

    def __lt__(self, other):
        """
        Hàm so sánh để Priority Queue (trong High-Level search) 
        có thể sắp xếp các node theo cost tăng dần.
        """
        return self.cost < other.cost

    def add_constraint(self, new_constraint):
        """Thêm một ràng buộc mới vào node."""
        self.constraints.add(new_constraint)