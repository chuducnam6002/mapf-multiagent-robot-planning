import numpy as np
import yaml
from dev.multiagent_planner.cbs_solver.solver import cbs_solve
from dev.multiagent_planner.visualizer import Visualizer
import csv

def load_warehouse_optimized(yaml_path, num_robots=4):
    with open(yaml_path, 'r', encoding='utf-8-sig') as f: 
        data = yaml.safe_load(f)
    
    grid_raw = np.array(data['grid'])
    grid = (grid_raw == 1).astype(int)
    
    robot_locs = np.argwhere(grid_raw == 2)
    station_locs = np.argwhere(grid_raw == 4)

    print(f"Số robot tìm thấy: {len(robot_locs)}, Số trạm tìm thấy: {len(station_locs)}")
    
    # Tính số lượng robot tối đa có thể chạy dựa trên dữ liệu map thực tế
    actual_count = min(len(robot_locs), len(station_locs), num_robots)
    
    if actual_count == 0:
        print("LỖI: Không tìm thấy Robot (2) hoặc Trạm (4) trên bản đồ!")
        return None, None, None, None

    starts = [tuple(loc) for loc in robot_locs[:actual_count]]
    goals = [tuple(loc) for loc in station_locs[:actual_count]]
    
    print(f"Hệ thống đã nhận diện: {actual_count} robot và {actual_count} trạm.")
    return grid, starts, goals, set(tuple(loc) for loc in station_locs)

def save_to_csv(paths, goals, station_set, output_file="logs/final_audit.csv"):
    max_t = max(len(p) for p in paths)
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestep", "Agent_ID", "Position_X", "Position_Y", "Action_Status"])
        
        for agent_id, path in enumerate(paths):
            goal = tuple(goals[agent_id])
            for t in range(max_t):
                # Nếu robot đã đến đích, giữ nguyên vị trí cuối cùng
                pos = path[t] if t < len(path) else path[-1]
                xy = (pos[0], pos[1])
                
                # Logic xác định trạng thái
                if xy == goal and xy in station_set:
                    status = 2 # Finished/Working
                elif t + 1 < len(path) and xy == (path[t+1][0], path[t+1][1]):
                    status = 1 # Waiting
                else:
                    status = 0 # Moving
                
                writer.writerow([t, agent_id, xy[0], xy[1], status])
    print(f"Dữ liệu đã xuất ra: {output_file}")

if __name__ == "__main__":
    yaml_file = "dev/warehouses/warehouse_100_robots.yaml"
    grid, starts, goals, station_set = load_warehouse_optimized(yaml_file, num_robots=60)
    
    print(f"Đang chạy CBS với {len(starts)} robot...")
    paths = cbs_solve(grid, starts, goals)
    
    if paths:
        print("Tìm thấy lộ trình thành công!")
        # Xuất dữ liệu đã đồng bộ
        save_to_csv(paths, goals, station_set)
        # Hiển thị visual
        visualizer = Visualizer(grid, starts, goals, paths)
        visualizer.show()
    else:
        print("CBS không tìm được lời giải trong không gian này.")