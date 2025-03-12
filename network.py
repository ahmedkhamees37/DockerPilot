import tkinter as tk
import json
class NetworkManager:
    def __init__(self, canvas, objects, networks):
        self.canvas = canvas
        self.objects = objects
        self.networks = networks
        self.network_count = 1

    def create_network(self, x, y):
        net_id = self.canvas.create_rectangle(x, y, x + 150, y + 100, fill="lightgreen", tags="network")
        self.objects[net_id] = {
            "name": f"Network {self.network_count}",
            "x": x,
            "y": y,
            "width": 150,
            "height": 100,
            "objects": [],
            "info": {"address": ""},
        }
        self.networks.append(net_id)
        self.network_count += 1
        return net_id

    def show_network_info_popup(self, event):
        net_id = self.canvas.find_closest(event.x, event.y)[0]
        network = self.objects.get(net_id)
        if network:
            popup = tk.Toplevel(self.canvas)
            popup.title("Network Information")
            popup.geometry("300x250")
            tk.Label(popup, text="Network Name:").pack(pady=5)
            name_entry = tk.Entry(popup, width=30)
            name_entry.insert(0, network.get("name", f"Network {self.network_count}"))
            name_entry.pack()
            tk.Label(popup, text="subnet").pack(pady=5)
            ip_entry = tk.Entry(popup, width=30)
            ip_entry.insert(0, network["info"].get("address", ""))
            ip_entry.pack()

            def save_network_info():
                network["name"] = name_entry.get().strip() or f"Network {self.network_count}"
                network["info"]["address"] = ip_entry.get().strip()
                self.canvas.itemconfig(network["name"], text=network["name"])
                extract_data = {'subnet': network["info"]["address"], 'name': network["name"]}
                network_name = network['name'].replace(' ', '')
                self.save_to_json(f"{network_name}.json", extract_data)
                #self.save_to_json(f"{network.get('name')}.json", extract_data)
                popup.destroy()

            tk.Button(popup, text="Save", command=save_network_info).pack(pady=10)

    def save_to_json(self, filename, data):
        filename1="/tmp/network/"+filename
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
            json.dump(existing_data, file, indent=5)
