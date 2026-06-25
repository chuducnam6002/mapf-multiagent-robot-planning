# generate_dataset_runner.py
import csv
import random
import os
from dev.warehouses.warehouse_loader import WorldInfo
from dev.multiagent_planner.cbs_solver.solver import cbs_solve, get_conflicts

# Các hàm hỗ trợ tính toán chỉ số
def soc(paths):
    return sum(len(p) - 1 for p in paths)

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def run_and_log(warehouse_path, output_csv, shuffle_goals=False, force_bottleneck=True):
    if not os.path.exists(warehouse_path):
        print(f"Lỗi: Không tìm thấy file {warehouse_path}")
        return
        
    world = WorldInfo.from_yaml(warehouse_path)
    grid = world.world_grid
    station_set = {tuple(s) for s in world.station_zones}
    
    num_homes = len(world.robot_home_zones)
    num_stations = len(world.station_zones)
    actual_robots = min(num_homes, num_stations, 24)
    
    if actual_robots == 0:
        print("Lỗi: Không đủ dữ liệu robot/trạm để chạy!")
        return

    starts = world.robot_home_zones[:actual_robots]
    goals = [world.station_zones[i % num_stations] for i in range(actual_robots)] if force_bottleneck else world.station_zones[:actual_robots]
    
    print(f"\n--- Đang chạy CBS cho {actual_robots} robot ---")
    paths = cbs_solve(grid, starts, goals)
    if not paths:
        print("Lỗi: CBS không tìm được lộ trình!")
        return

    # 1. SOC ANALYSIS
    print(f"\n===== COST ANALYSIS =====")
    print(f"FINAL SOC (Sum of Costs): {soc(paths)}")

    # 2. PATH LENGTH & DETOUR ANALYSIS
    lens = [len(p) for p in paths]
    total_detour = 0
    print(f"\n===== DETOUR ANALYSIS =====")
    for i, path in enumerate(paths):
        shortest = manhattan(starts[i], goals[i])
        actual = len(path) - 1
        detour = actual - shortest
        total_detour += detour
        print(f"Agent {i}: Shortest={shortest}, Actual={actual}, Detour={detour}")
    print(f"TOTAL DETOUR: {total_detour}")

    # 3. GOAL WAITS
    goal_waits = 0
    for path in paths:
        goal = path[-1]
        idx = len(path) - 1
        while idx > 0 and path[idx-1] == goal:
            goal_waits += 1
            idx -= 1
    print(f"GOAL WAITS: {goal_waits}")

    # 4. Ghi CSV
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestep", "Agent_ID", "Position_X", "Position_Y", "Action_Status"])
        
        # Tìm thời điểm kết thúc lâu nhất để đảm bảo tất cả robot đều có dữ liệu đến cùng một timestep
        max_t = max(len(path) for path in paths)
        
        for agent_id, path in enumerate(paths):
            goal = tuple(goals[agent_id])
            for t in range(max_t):
                # Nếu t vượt quá độ dài path, robot đứng yên tại vị trí cuối cùng
                if t < len(path):
                    pos = path[t]
                    xy = (pos[0], pos[1])
                    
                    # Xác định trạng thái
                    is_waiting = (t + 1 < len(path) and xy == (path[t+1][0], path[t+1][1]))
                    
                    if xy == goal and xy in station_set:
                        status = 2 # Đã tới đích/Đang làm việc
                    elif is_waiting:
                        status = 1 # Đang chờ (nằm trong lộ trình)
                    else:
                        status = 0 # Đang di chuyển
                else:
                    # Trường hợp robot đã tới đích từ lâu (t >= len(path))
                    xy = (path[-1][0], path[-1][1])
                    status = 2 # Giữ trạng thái hoàn thành
                
                writer.writerow([t, agent_id, xy[0], xy[1], status])

    print(f"\nAudit hoàn tất. Dữ liệu đã lưu tại: {output_csv}")

if __name__ == "__main__":
    run_and_log(
        warehouse_path="dev/warehouses/warehouse_100_robots.yaml", 
        output_csv="logs/audit_results.csv", 
        force_bottleneck=True
    )