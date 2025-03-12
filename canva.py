import uuid
from state import StateManager
from network import NetworkManager
from container import ContainerManager
from volume import VolumeManager  # Import the VolumeManager class

class CanvasManager:
    def __init__(self, root, canvas):
        self.root = root
        self.canvas = canvas
        self.state_manager = StateManager()
        self.objects = {}
        self.connections = {}
        self.networks = []
        self.selected_item = None
        self.start_point = None
        self.resizing = None
        self.network_manager = NetworkManager(canvas, self.objects, self.networks)
        self.container_manager = ContainerManager(canvas, self.objects)
        self.volume_manager = VolumeManager(canvas, self.objects)  # Initialize VolumeManager

    def start_drag(self, event, name, img):
        x, y = 250, 150
        if name == "Network":
            net_id = self.network_manager.create_network(x, y)
            self.add_resize_handles(net_id, x, y, x + 150, y + 100)
            self.canvas.tag_bind(net_id, "<Double-Button-1>", self.network_manager.show_network_info_popup)
        elif name == "Volume":
            volume_id = self.volume_manager.create_volume(x, y, img)
            self.add_connection_points(volume_id, x, y, name)
            self.canvas.tag_bind(volume_id, "<Double-Button-1>", self.volume_manager.show_info_popup)
        else:
            image_id = self.container_manager.create_container(x, y, img, name)
            self.add_connection_points(image_id, x, y, name)
        self.save_state()

    def add_resize_handles(self, net_id, x1, y1, x2, y2):
        handles = []
        handle_size = 4
        corners = [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]
        for cx, cy in corners:
            handle = self.canvas.create_rectangle(cx - handle_size, cy - handle_size,
                                                  cx + handle_size, cy + handle_size,
                                                  fill="black", tags="resize")
            handles.append(handle)
            self.canvas.tag_bind(handle, "<Button-1>", lambda event, h=handle, n=net_id: self.start_resize(event, h, n))
        self.objects[net_id]["handles"] = handles

    def start_resize(self, event, handle, net_id):
        self.resizing = (handle, net_id)
        self.canvas.bind("<B1-Motion>", self.resize_network)
        self.canvas.bind("<ButtonRelease-1>", self.stop_resize)

    def update_handles(self, net_id, x1, y1, x2, y2):
        handle_size = 4
        corners = [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]
        for i, (cx, cy) in enumerate(corners):
            self.canvas.coords(self.objects[net_id]["handles"][i],
                               cx - handle_size, cy - handle_size,
                               cx + handle_size, cy + handle_size)

    def resize_network(self, event):
        if self.resizing:
            handle, net_id = self.resizing
            x, y = event.x, event.y
            x1, y1, x2, y2 = self.canvas.coords(net_id)

            if handle == self.objects[net_id]["handles"][0]:  # Top-left
                x1, y1 = x, y
            elif handle == self.objects[net_id]["handles"][1]:  # Top-right
                x2, y1 = x, y
            elif handle == self.objects[net_id]["handles"][2]:  # Bottom-left
                x1, y2 = x, y
            elif handle == self.objects[net_id]["handles"][3]:  # Bottom-right
                x2, y2 = x, y

            if abs(x2 - x1) < 20 or abs(y2 - y1) < 20:
                return

            self.canvas.coords(net_id, x1, y1, x2, y2)
            self.update_handles(net_id, x1, y1, x2, y2)

    def update_lines(self, obj_id):
        for conn_id, (start, end, line) in self.connections.items():
            if start == obj_id or end == obj_id:
                start_coords = self.canvas.coords(start)
                end_coords = self.canvas.coords(end)

                if len(start_coords) == 4 and len(end_coords) == 4:
                    x1, y1 = (start_coords[0] + start_coords[2]) / 2, (start_coords[1] + start_coords[3]) / 2
                    x2, y2 = (end_coords[0] + end_coords[2]) / 2, (end_coords[1] + end_coords[3]) / 2

                    self.canvas.coords(line, x1, y1, x2, y2)

    def stop_resize(self, event):
        self.resizing = None
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.save_state()

    def add_connection_points(self, image_id, x, y, obj_name):
        connection_points = [
            (x - 25, y - 25), (x + 25, y - 25),
            (x - 25, y + 25), (x + 25, y + 25),
        ]
        for cx, cy in connection_points:
            point_id = self.canvas.create_oval(cx - 4, cy - 4, cx + 5, cy + 5, fill="blue", tags="point")
            self.objects[point_id] = {"parent": image_id, "type": obj_name, "connected_to": None}
        text_id = self.canvas.create_text(x, y + 40, text=obj_name, font=("Arial", 10), tags="label")
        self.objects[text_id] = {"parent": image_id, "type": "label"}
        self.canvas.tag_bind(image_id, "<Button-1>", self.select_object)
        self.canvas.tag_bind(image_id, "<Double-Button-1>", self.container_manager.show_info_popup)
        for point_id in self.objects:
            if self.objects[point_id].get("parent") == image_id:
                self.canvas.tag_bind(point_id, "<Button-1>", self.start_connection)

    def select_object(self, event):
        self.selected_item = self.canvas.find_closest(event.x, event.y)[0]
        x1, y1 = self.canvas.coords(self.selected_item)
        self.offset_x = event.x - x1
        self.offset_y = event.y - y1
        self.canvas.bind("<B1-Motion>", self.move_object)
        self.canvas.bind("<ButtonRelease-1>", self.release_object)

    def move_object(self, event):
        if self.selected_item and self.selected_item in self.objects:
            obj_data = self.objects[self.selected_item]
            new_x = event.x - self.offset_x
            new_y = event.y - self.offset_y
            dx = new_x - obj_data["x"]
            dy = new_y - obj_data["y"]

            self.canvas.move(self.selected_item, dx, dy)

            for obj_id, data in self.objects.items():
                if isinstance(data, dict) and data.get("parent") == self.selected_item:
                    self.canvas.move(obj_id, dx, dy)

            obj_data["x"] = new_x
            obj_data["y"] = new_y

            self.update_lines(self.selected_item)

    def release_object(self, event):
            if self.selected_item in self.objects:
                obj_data = self.objects[self.selected_item]
                x, y = obj_data["x"], obj_data["y"]

                # Check network membership only for containers
                if "Container" in obj_data["name"]:
                    inside_network = False
                    for net_id in self.networks:
                        x1, y1, x2, y2 = self.canvas.coords(net_id)
                        if x1 < x < x2 and y1 < y < y2:
                            inside_network = True
                            if obj_data.get("network") != net_id:
                                obj_data["network"] = net_id
                                self.objects[net_id]["objects"].append(self.selected_item)
                                obj_data["parent_network"] = self.objects[net_id]["name"]
                            break
                    if not inside_network and obj_data.get("network") is not None:
                        net_id = obj_data["network"]
                        self.objects[net_id]["objects"].remove(self.selected_item)
                        obj_data["network"] = None
                        obj_data["parent_network"] = ""

            self.selected_item = None
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            self.save_state()

    def start_connection(self, event):
        point_id = self.canvas.find_closest(event.x, event.y)[0]
        if self.start_point is None:
            self.start_point = point_id
        else:
            end_point = point_id
            if self.start_point == end_point:
                self.start_point = None
                return
            start_parent = self.objects[self.start_point].get("parent")
            end_parent = self.objects[end_point].get("parent")
            if start_parent and end_parent:
                start_name = self.objects[start_parent]["name"]
                end_name = self.objects[end_parent]["name"]
                if "Container" in start_name and "Volume" in end_name:
                    self.objects[self.start_point]["connected_to"] = end_parent
                    self.objects[end_point]["connected_to"] = start_parent
                elif "Container" in end_name and "Volume" in start_name:
                    self.objects[self.start_point]["connected_to"] = start_parent
                    self.objects[end_point]["connected_to"] = end_parent
            x1, y1 = self.canvas.coords(self.start_point)[:2]
            x2, y2 = self.canvas.coords(end_point)[:2]
            line_id = self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)
            self.connections[uuid.uuid4()] = (self.start_point, end_point, line_id)
            self.start_point = None

    def save_state(self):
        state = {
            "objects": self.objects.copy(),
            "connections": self.connections.copy(),
            "networks": self.networks.copy(),
        }
        self.state_manager.save_state(state)

    def undo(self):
        state = self.state_manager.undo()
        if state:
            self.restore_state(state)

    def redo(self):
        state = self.state_manager.redo()
        if state:
            self.restore_state(state)

    def restore_state(self, state):
        self.objects = state["objects"].copy()
        self.connections = state["connections"].copy()
        self.networks = state["networks"].copy()
        self.redraw_canvas()

    def redraw_canvas(self):
        self.canvas.delete("all")
        for obj_id, data in self.objects.items():
            if data["name"] == "Network":
                self.canvas.create_rectangle(
                    data["x"], data["y"],
                    data["x"] + data["width"], data["y"] + data["height"],
                    fill="lightgreen", tags="network"
                )
                self.add_resize_handles(
                    obj_id, data["x"], data["y"],
                    data["x"] + data["width"], data["y"] + data["height"]
                )
            else:
                self.canvas.create_image(
                    data["x"], data["y"],
                    image=data["image"], anchor="center", tags="movable"
                )
                self.canvas.create_text(
                    data["x"], data["y"] + 40,
                    text=data["name"], font=("Arial", 10), tags="label"
                )
                connection_points = [
                    (data["x"] - 25, data["y"] - 25),
                    (data["x"] + 25, data["y"] - 25),
                    (data["x"] - 25, data["y"] + 25),
                    (data["x"] + 25, data["y"] + 25),
                ]
                for cx, cy in connection_points:
                    point_id = self.canvas.create_oval(
                        cx - 5, cy - 5, cx + 5, cy + 5,
                        fill="red", tags="point"
                    )
                    self.objects[point_id] = {
                        "parent": obj_id,
                        "type": data["name"],
                        "connected_to": None
                    }
        for conn_id, (start, end, line) in self.connections.items():
            x1, y1 = self.canvas.coords(start)[:2]
            x2, y2 = self.canvas.coords(end)[:2]
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill="blue", width=2, tags="connection"
            )
