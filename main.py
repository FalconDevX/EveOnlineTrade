from collections import defaultdict
import pandas as pd
import heapq

file_path = "systems_data.csv"

df = pd.read_csv(file_path)

systems_names = df["solarSystemID"].dropna().astype(int).tolist()
security_dict = df.set_index("solarSystemID")["security"].to_dict()

def name_to_id(name):
    for _, row in df.iterrows():
        if row["solarSystemName"] == name:
            return int(row["solarSystemID"])
    return None

def id_to_name(id):
    for _, row in df.iterrows():
        if int(row["solarSystemID"]) == id:
            return row["solarSystemName"]
    return None

#building graph based on jumps between systems
def build_graph(jumps):
    graph = defaultdict(list)
    for start, end, cost in jumps:
        graph[start].append((end, cost))
        graph[end].append((start, cost)) 
    return graph

#returning color based on security status
def get_security_color(security_status):
    if security_status >= 0.9:
        return "\033[94m"  # blue
    elif security_status >= 0.7:
        return "\033[96m"  # Cyan
    elif security_status >= 0.5:
        return "\033[92m"  # green
    elif security_status >= 0.3:
        return "\033[93m"  # yellow
    elif security_status >= 0.1:
        return "\033[91m"  # orange
    elif security_status == 0.0:
        return "\033[31m"  # red
    else:
        return "\033[35m"  # dark red (purple)

#generating route type basen on security status
def generate_route_type(type):    
    jumps = []

    for _, row in df.iterrows():
        from_system = row["fromSolarSystemID"]
        to_system = row["toSolarSystemID"]

        from_system_security = security_dict.get(from_system, 0.5)  
        to_system_security = security_dict.get(to_system, 0.5)

        if type == "security":
            weight = 1 / max(from_system_security + to_system_security, 0.0001)  
        elif type == "shortest":
            weight = 1  
        elif type == "less_safe":
            weight = 1 / max(2 - from_system_security - to_system_security, 0.0001)  

        if from_system in systems_names and to_system in systems_names:
            jumps.append((from_system, to_system, weight))

    graph = build_graph(jumps)
    return graph

# Dijsktra algorithm
def dijkstra(graph, start, end):
    queue = []
    heapq.heappush(queue, (0, start))

    distances = {node: float('inf') for node in graph}
    distances[start] = 0

    previous_nodes = {}  

    while queue:
        curr_dist, curr_node = heapq.heappop(queue)

        if curr_node == end:
            path = []
            while curr_node is not None:
                path.append(curr_node)
                curr_node = previous_nodes.get(curr_node)
            return list(reversed(path)), distances[end]

        if curr_dist > distances[curr_node]:
            continue

        for neighbour, weight in graph[curr_node]:
            distance = curr_dist + weight

            if distance < distances[neighbour]:
                distances[neighbour] = distance
                previous_nodes[neighbour] = curr_node
                heapq.heappush(queue, (distance, neighbour))

    return None, float('inf')

#User interation
system_A = input("Provide starting system: ")
system_A = name_to_id(system_A)

system_B = input("Provide destination system: ")
system_B = name_to_id(system_B)

route_type = input("Provide route type (security, shortest, less_safe): ")

if system_A is None or system_B is None:
    print("System not found!")
else:
    shortest_path, shortest_distance = dijkstra(generate_route_type(route_type), system_A, system_B)

    if shortest_distance == float('inf'):
        print("Ścieżka nie została znaleziona.")
    else:
        print(f"Trasa z {id_to_name(system_A)} do {id_to_name(system_B)}:")
        system_counter = 0
        for system in shortest_path:
            security = security_dict.get(system, 0.0)  
            color = get_security_color(security)  
            security_formatted = f"{security:.2f}"


            print(f"{color}{id_to_name(system)} ({security_formatted})\033[0m -> ", end=" ")
        print()
        print("Total jumps:", len(shortest_path) - 1)