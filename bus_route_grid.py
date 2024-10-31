import tkinter as tk
import heapq
import math
from tkinter import messagebox

class Location:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
    
    def distance_to(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

class Path:
    def __init__(self, from_loc, to_loc, cost, obstacle=False):
        self.from_loc = from_loc
        self.to_loc = to_loc
        self.cost = cost
        self.obstacle = obstacle

class Graph:
    def __init__(self, cost_per_distance=1.0):
        self.locations = {}
        self.paths = {}
        self.cost_per_distance = cost_per_distance

    def add_location(self, location):
        self.locations[location.name] = location

    def add_path(self, from_loc, to_loc, obstacle=False):
        distance = self.locations[from_loc].distance_to(self.locations[to_loc]) / 10  # Scale to kilometers
        cost = distance * self.cost_per_distance
        if obstacle:
            cost *= 10  # Inflate cost for obstacles to make them less desirable
        if from_loc not in self.paths:
            self.paths[from_loc] = []
        self.paths[from_loc].append(Path(from_loc, to_loc, cost, obstacle))
        # Make bidirectional
        if to_loc not in self.paths:
            self.paths[to_loc] = []
        self.paths[to_loc].append(Path(to_loc, from_loc, cost, obstacle))

    def get_neighbors(self, location_name):
        return self.paths.get(location_name, [])

    def a_star_search(self, start_name, goal_name):
        open_set = []
        heapq.heappush(open_set, (0, start_name))
        
        came_from = {}
        g_score = {location: float('inf') for location in self.locations}
        g_score[start_name] = 0
        
        f_score = {location: float('inf') for location in self.locations}
        f_score[start_name] = self.locations[start_name].distance_to(self.locations[goal_name])
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == goal_name:
                return self.reconstruct_path(came_from, current)
            
            for path in self.get_neighbors(current):
                tentative_g_score = g_score[current] + path.cost
                
                if tentative_g_score < g_score[path.to_loc]:
                    came_from[path.to_loc] = current
                    g_score[path.to_loc] = tentative_g_score
                    f_score[path.to_loc] = tentative_g_score + self.locations[path.to_loc].distance_to(self.locations[goal_name])
                    heapq.heappush(open_set, (f_score[path.to_loc], path.to_loc))
        
        return None

    def uniform_cost_search(self, start_name, goal_name):
        open_set = []
        heapq.heappush(open_set, (0, start_name))  # Priority queue initialized with start node and cost 0
        
        came_from = {}
        cost_so_far = {location: float('inf') for location in self.locations}
        cost_so_far[start_name] = 0
        
        while open_set:
            current_cost, current = heapq.heappop(open_set)

            # If we reached the goal, reconstruct the path
            if current == goal_name:
                return self.reconstruct_path(came_from, current)
            
            for path in self.get_neighbors(current):
                new_cost = cost_so_far[current] + path.cost
                
                if new_cost < cost_so_far[path.to_loc]:
                    cost_so_far[path.to_loc] = new_cost
                    priority = new_cost
                    heapq.heappush(open_set, (priority, path.to_loc))
                    came_from[path.to_loc] = current
        
        return None  # Return None if no path found

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from and came_from[current] is not None:
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]

class App:
    def __init__(self, root, graph):
        self.root = root
        self.root.title("Bus Station Route Finder")
        self.graph = graph
        self.start = None
        self.goal = None
        self.path_lines = []  # Store the line IDs for the current path

        # Create map canvas
        self.canvas = tk.Canvas(root, width=1000, height=600, bg="white")
        self.canvas.pack()

        # Load background image
        self.background_image = tk.PhotoImage(file="map_its.png")  # Adjust the path to your image
        self.canvas.create_image(0, 0, anchor="nw", image=self.background_image)

        self.grid_size = 3
        self.cell_size = 3  # Each cell in pixels (adjust this based on your scaling)
        # self.draw_grid()
        self.place_stations_and_stops()
        self.draw_streets()

        # Highlighted cell variables
        self.highlighted_cell = None
        self.highlighted_cell_coords = None

        # User controls
        tk.Label(root, text="Select Start Point:").pack(side="left")
        self.start_var = tk.StringVar(root)
        self.start_var.set("Bus Station 1")
        tk.OptionMenu(root, self.start_var, *self.graph.locations.keys()).pack(side="left")

        tk.Label(root, text="Select Goal Point:").pack(side="left")
        self.goal_var = tk.StringVar(root)
        self.goal_var.set("Bus Station 1")
        tk.OptionMenu(root, self.goal_var, *[loc for loc in graph.locations if "Bus Station" in loc]).pack(side="left")

        self.algorithm_var = tk.StringVar(value="A*")
        tk.Radiobutton(root, text="A*", variable=self.algorithm_var, value="A*").pack(side="left")
        tk.Radiobutton(root, text="Uniform Cost Search", variable=self.algorithm_var, value="Uniform Cost Search").pack(side="left")

        tk.Button(root, text="Find Route", command=self.find_path).pack(side="left")

        # Add mouse click event to highlight grid cell
        self.canvas.bind("<Button-1>", self.highlight_cell)

        # Label to show coordinates
        self.coord_label = tk.Label(root, text="")
        self.coord_label.pack(side="bottom")

    def draw_grid(self):
        # Define grid dimensions
        grid_width = 1000  # in meters
        grid_height = 1600  # in meters
        cell_size = 1  # in meters

        # Calculate the number of cells in each direction
        num_cols = grid_width // cell_size
        num_rows = grid_height // cell_size

        # Draw grid (you can also adjust the colors as needed)
        for i in range(num_cols + 1):
            x = i * (self.cell_size)  # Scale the cell size to your canvas
            self.canvas.create_line(x, 0, x, 600, fill="lightgray")
        for i in range(num_rows + 1):
            y = i * (self.cell_size)  # Scale the cell size to your canvas
            self.canvas.create_line(0, y, 1000, y, fill="lightgray")

    def place_stations_and_stops(self):
        locations = [
            ("Bus Station 1", 1, 1),
            ("Bus Stop 1", 1, 2),
        ]
        for name, x, y in locations:
            x_coord, y_coord = x * self.cell_size, y * self.cell_size
            self.graph.add_location(Location(name, x_coord, y_coord))
            color = "green" if "Bus Station" in name else "orange"
            self.canvas.create_oval(x_coord - 5, y_coord - 5, x_coord + 5, y_coord + 5, fill=color)
            self.canvas.create_text(x_coord, y_coord - 10, text=name, font=("Arial", 10))

    def draw_streets(self):
        paths = [
            ("Bus Station 1", "Bus Stop 1"),
        ]
        for from_loc, to_loc, *obstacle in paths:
            obstacle = obstacle[0] if obstacle else False
            self.graph.add_path(from_loc, to_loc, obstacle)
            from_coords = (self.graph.locations[from_loc].x, self.graph.locations[from_loc].y)
            to_coords = (self.graph.locations[to_loc].x, self.graph.locations[to_loc].y)
            color = "red" if obstacle else "black"
            self.canvas.create_line(from_coords, to_coords, fill=color, width=2)

    def highlight_cell(self, event):
        # Clear previous highlight
        if self.highlighted_cell:
            self.canvas.delete(self.highlighted_cell)

        # Calculate grid cell based on click coordinates
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        # Highlight the cell
        x0 = x * self.cell_size
        y0 = y * self.cell_size
        x1 = (x + 1) * self.cell_size
        y1 = (y + 1) * self.cell_size
        self.highlighted_cell = self.canvas.create_rectangle(x0, y0, x1, y1, outline="white", width=2)
        
        # Store the coordinates and update label
        self.highlighted_cell_coords = (x, y)
        self.coord_label.config(text=f"Selected Cell: ({x}, {y})")

    def find_path(self):
        # Clear previous path lines
        for line_id in self.path_lines:
            self.canvas.delete(line_id)
        self.path_lines.clear()

        start = self.start_var.get()
        goal = self.goal_var.get()
        algorithm = self.algorithm_var.get()
        
        if algorithm == "A*":
            path = self.graph.a_star_search(start, goal)
        elif algorithm == "Uniform Cost Search":
            path = self.graph.uniform_cost_search(start, goal)
        
        if path:
            total_distance = 0
            for i in range(len(path) - 1):
                from_loc = self.graph.locations[path[i]]
                to_loc = self.graph.locations[path[i + 1]]
                distance = from_loc.distance_to(to_loc) / 100  # Calculate distance in km
                total_distance += distance
                # Draw and store the line ID for the current path segment
                line_id = self.canvas.create_line(from_loc.x, from_loc.y, to_loc.x, to_loc.y, fill="blue", width=3)
                self.path_lines.append(line_id)
            total_cost = total_distance * 2000
            messagebox.showinfo("Route Finder", f"Distance: {total_distance:.2f} km\nCost: Rp{total_cost:.0f}")
        else:
            messagebox.showinfo("Route Finder", "No path found")


root = tk.Tk()
graph = Graph(cost_per_distance=5)
app = App(root, graph)
root.mainloop()
