import os
import glob
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from canva import CanvasManager
import json
import subprocess
import yaml
class DragDropApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Docker_on_Hand")
        self.root.geometry("800x600")

        # Remove JSON files on start
        self.clear_json_files()

        # Top bar setup
        self.top_bar = tk.Frame(root, height=50, bg="gray")
        self.top_bar.pack(side="top", fill="x")

        # Load images for start and stop buttons
        try:
            start_img = Image.open("start.png").resize((30, 30))
            stop_img = Image.open("stop.png").resize((30, 30))
            self.start_img = ImageTk.PhotoImage(start_img)
            self.stop_img = ImageTk.PhotoImage(stop_img)
        except FileNotFoundError:
            messagebox.showerror("Error", "Image files (start.png, stop.png) not found!")
            self.root.destroy()
            return

        # Add start and stop buttons
        self.btn_stop = tk.Button(self.top_bar, image=self.stop_img, command=lambda: self.show_message("Stop"))
        self.btn_stop.pack(side="right", padx=10, pady=5)
        self.btn_start = tk.Button(self.top_bar, image=self.start_img, command=lambda: self.show_message("Start"))
        self.btn_start.pack(side="right", padx=10, pady=5)

        # Left sidebar setup
        self.left_bar = tk.Frame(root, width=150, bg="lightgray")
        self.left_bar.pack(side="left", fill="y")

        # Canvas setup
        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(expand=True, fill="both")
        self.canvas_manager = CanvasManager(root, self.canvas)

        # Load images for draggable items
        try:
            self.container_img = ImageTk.PhotoImage(Image.open("container.png").resize((50, 50)))
            self.volume_img = ImageTk.PhotoImage(Image.open("volume.png").resize((50, 50)))
        except FileNotFoundError:
            messagebox.showerror("Error", "Image files (container.png, volume.png) not found!")
            self.root.destroy()
            return

        # Create draggable buttons
        self.create_draggable_button("Container", "lightblue", self.container_img)
        self.create_draggable_button("Volume", "lightcoral", self.volume_img)
        self.create_draggable_button("Network", "lightgreen", None)

    def create_draggable_button(self, name, color, img):
        btn = tk.Button(self.left_bar, text=name, bg=color)
        btn.pack(pady=10, fill="x")
        btn.bind("<ButtonPress-1>", lambda event, n=name, i=img: self.canvas_manager.start_drag(event, n, i))

    def show_message(self, value):
          # Print message when the "Start" button is clicked
            print("click start")

            # Network
            def get_network():
                dict1 = {}
                cmd = f'ls  /tmp/network | wc -l'
                count = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                for i in range(1, int(count.stdout.split()[0]) + 1):
                    with open(f"/tmp/network/Network{i}.json", "r") as file:
                        data = json.load(file)[0]
                    network_name = data["name"]
                    subnet = data["subnet"]
                    cmd = f'docker network ls | cut -d" " -f4 | grep -c ^{network_name}$'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if int(result.stdout.split()[0]) > 0:
                        dict1.update({network_name: {"external": "true"}})
                    else:
                        dict1.update({network_name: {"driver": "bridge", "ipam": {"config": [{"subnet": subnet}]}}})
                return dict1

            # Volumes
            def get_volume():
                cmd = f'ls /tmp/volume | wc -l'
                count = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                dict1 = {}
                for i in range(1, int(count.stdout.split()[0]) + 1):
                    with open(f"/tmp/volume/Volume{i}.json", "r") as file:
                        data = json.load(file)[0]
                    volume_name = data["name"]
                    cmd = f'docker volume ls | cut -d" " -f6 | grep -c "^{volume_name}$"'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if int(result.stdout.split()[0]) > 0:
                        dict1.update({volume_name: {"external": "true"}})
                    else:
                        dict1.update({volume_name: {}})
                return dict1

            # Services
            def get_service():
                dict1 = {}
                cmd = f'ls /tmp/container | wc -l'
                count = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                for i in range(1, int(count.stdout.split()[0]) + 1):
                    with open(f"/tmp/container/Container{i}.json", "r") as file:
                        data = json.load(file)[0]
                    image_name = data["image_name"]
                    service_name = data["name"]
                    container_name = data["name"]
                    network_name = data["parent_network"]
                    port_list = data["expose_port"]
                    volumes_list = []
                    for vol in data["volumes"]:
                        volume_name = vol["volume_name"]
                        mount_point = vol["mount_path"]
                        volumes_list.append(f"{volume_name}:{mount_point}")
                    cmd = f"docker ps -a | awk '{{print $NF}}' | grep -c '^{container_name}$'"
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if int(result.stdout.split()[0]) > 0:
                        dict1.update({
                            service_name: {
                                "image": image_name,
                                "container_name": container_name + ".2",
                                "networks": [network_name],
                                "volumes": volumes_list,
                                "ports": [port_list]
                            }
                        })
                    else:
                        dict1.update({
                            service_name: {
                                "image": image_name,
                                "container_name": container_name,
                                "networks": [network_name],
                                "volumes": volumes_list,
                                "ports": [port_list]
                            }
                        })
                return dict1

            networks = get_network()
            volumes = get_volume()
            services = get_service()

            compose = {
                "services": services,
                "networks": networks,
                "volumes": volumes
            }

            with open("compose.yml", "w") as file:
                yaml.dump(compose, file, sort_keys=False)
            print("Docker Compose file generated successfully: compose.yml")

            result = subprocess.run("docker-compose -f compose.yml up", shell=True, capture_output=True, text=True)
            print("Containers run successfully")


    def clear_json_files(self):
        # Directories to clear
        path = "/tmp"
        directories = [f"{path}/container", f"{path}/volume", f"{path}/network"]

        for directory in directories:
            # Find all JSON files in the directory
            files = glob.glob(os.path.join(directory, "*.json"))
            for file in files:
                try:
                    os.remove(file)
                    print(f"Removed {file}")
                except Exception as e:
                    print(f"Error removing {file}: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DragDropApp(root)
    root.mainloop()
