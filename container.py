import tkinter as tk
import json
class ContainerManager:
    def __init__(self, canvas, objects):
        self.canvas = canvas
        self.objects = objects
        self.container_count = 1
        self.volume_count = 1

    def create_container(self, x, y, img, name):
        image_id = self.canvas.create_image(x, y, image=img, anchor="center", tags="movable")
        obj_name = f"{name} {self.container_count if name == 'Container' else self.volume_count}"
        if name == "Container":
            self.container_count += 1
            print(self.container_count)
        elif name == "Volume":
            self.volume_count += 1
        self.objects[image_id] = {
            "name": obj_name,
            "x": x,
            "y": y,
            "image": img,
            "connections": [],
            "network": None,
            "info": "",
        }
        return image_id

    def show_info_popup(self, event):
        obj_id = self.canvas.find_closest(event.x, event.y)[0]
        container = self.objects.get(obj_id)
        if container and "Container" in container.get("name", ""):
            popup = tk.Toplevel(self.canvas)
            popup.title(f"Info for {container.get('name', 'Container')}")
            popup.geometry("400x500")
            frame = tk.Frame(popup)
            frame.pack(fill=tk.BOTH, expand=True)
            scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=canvas.yview)
            inner_frame = tk.Frame(canvas)
            canvas.create_window((0, 0), window=inner_frame, anchor='nw')

            def on_frame_configure(event):
                canvas.config(scrollregion=canvas.bbox("all"))

            inner_frame.bind("<Configure>", on_frame_configure)
            tk.Label(inner_frame, text="Container Name:").pack(pady=5)
            name_entry = tk.Entry(inner_frame, width=30)
            name_entry.insert(0, container.get("name", "Container"))
            name_entry.pack()
            tk.Label(inner_frame, text="Parent Network:").pack(pady=5)
            net_label = tk.Label(inner_frame, text=container.get("parent_network", "No Network"))
            net_label.pack()

            def update_network_label():
                net_label.config(text=container.get("parent_network", "No Network"))

            update_network_label()
            fields = {
                "Image Name": tk.Entry(inner_frame, width=30),
                "expose": tk.Entry(inner_frame, width=30)
            }
            for field, entry in fields.items():
                tk.Label(inner_frame, text=f"{field}:").pack(pady=5)
                entry.pack(pady=5)
                entry.insert(0, container.get(field.lower().replace(" ", "_"), ""))
            tk.Label(inner_frame, text="Volume Mount Paths:").pack(pady=5)
            mount_entries = {}
            for point_id, point_data in self.objects.items():
                if point_data.get("parent") == obj_id and point_data.get("connected_to"):
                    volume_id = point_data["connected_to"]
                    volume_name = self.objects[volume_id]["name"]
                    tk.Label(inner_frame, text=f"{volume_name}:").pack()
                    mount_entry = tk.Entry(inner_frame, width=30)
                    mount_entry.insert(0, point_data.get("mount_path", ""))
                    mount_entry.pack(pady=2)
                    mount_entries[volume_id] = mount_entry

            def save_info():
                container["name"] = name_entry.get().strip() or "Container"
                for field, entry in fields.items():
                    container[field.lower().replace(" ", "_")] = entry.get()

                # Collect volume information
                volumes = []
                for volume_id, entry in mount_entries.items():
                    mount_path = entry.get()
                    if mount_path:
                        volume_name = self.objects[volume_id]["name"]
                        volumes.append({"volume_name": volume_name, "mount_path": mount_path})
                        for point_id, point_data in self.objects.items():
                            if point_data.get("parent") == obj_id and point_data.get("connected_to") == volume_id:
                                point_data["mount_path"] = mount_path

                popup.destroy()
                print(container)
                # Include volume information in the extracted data
                extracted_data = {
                    'image_name': container.get('image_name', 'python:latest'),
                    'name': container.get('name'),
                    'parent_network': container.get('parent_network'),
                    'volumes': volumes  ,# Add volumes list to the data
                    'expose_port':container.get("expose")
                }
                container_name = container['name'].replace(' ', '')
                self.save_to_json(f"{container_name}.json", extracted_data)
                #self.save_to_json(f"{container.get('name')}.json", extracted_data)

            tk.Button(inner_frame, text="Save", command=save_info).pack(pady=10)

    def save_to_json(self, filename, data):
        filename1="/tmp/container/"+filename
        try:
            with open(filename1, "r") as file:
                existing_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []
        updated = False
        for i, item in enumerate(existing_data):
            if item.get("name") == data.get("name"):
                existing_data[i] = data
                updated = True
                break
        if not updated:
            existing_data.append(data)
        with open(filename1, "w") as file:
            json.dump(existing_data, file, indent=4)
