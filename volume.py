import tkinter as tk
import json
class VolumeManager:
    def __init__(self, canvas, objects):
        self.canvas = canvas
        self.objects = objects
        self.volume_count = 1

    def create_volume(self, x, y, img):
        volume_id = self.canvas.create_image(x, y, image=img, anchor="center", tags="movable")
        volume_name = f"Volume {self.volume_count}"
        self.volume_count += 1

        self.objects[volume_id] = {
            "name": volume_name,
            "x": x,
            "y": y,
            "image": img,
            "connections": [],
            "info": "",
        }

        self.canvas.tag_bind(volume_id, "<Double-Button-1>", self.show_info_popup)
        return volume_id

    def show_info_popup(self, event):
        volume_id = self.canvas.find_closest(event.x, event.y)[0]
        volume = self.objects.get(volume_id)

        if volume:
            popup = tk.Toplevel(self.canvas)
            popup.title(f"Info for {volume.get('name', 'Volume')}")
            popup.geometry("300x200")

            tk.Label(popup, text="Volume Name:").pack(pady=5)
            name_entry = tk.Entry(popup, width=30)
            name_entry.insert(0, volume.get("name", "Volume"))
            name_entry.pack()

            def save_info():
                volume["name"] = name_entry.get().strip() or "Volume"
                volume_name = volume['name'].replace(' ', '')
                self.save_to_json(f"{volume_name}.json", volume_name)
                #self.save_to_json(f"{volume.get('name')}.json", volume['name'])
                popup.destroy()

            tk.Button(popup, text="Save", command=save_info).pack(pady=10)
    def save_to_json(self, filename, data):
        filename1="/tmp/volume/"+filename
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
