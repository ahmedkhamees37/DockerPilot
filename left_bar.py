
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
class LeftBar:
    def __init__(self, root, app):
        self.app = app
        self.frame = tk.Frame(root, width=150, bg="lightgray")
        self.frame.pack(side="left", fill="y")

        # Load images for draggable objects
        try:
            self.container_img = ImageTk.PhotoImage(Image.open("container.png").resize((50, 50)))
            self.volume_img = ImageTk.PhotoImage(Image.open("volume.png").resize((50, 50)))
        except FileNotFoundError:
            messagebox.showerror("Error", "Image files (container.png, volume.png) not found!")
            root.destroy()
            return

        # Add draggable buttons to the sidebar
        self.create_draggable_button("Container", "lightblue", self.container_img)
        self.create_draggable_button("Volume", "lightcoral", self.volume_img)
        self.create_draggable_button("Network", "lightgreen", None)  # Network is a rectangle, no image

    def create_draggable_button(self, name, color, img):
        """Creates a draggable button in the sidebar."""
        btn = tk.Button(self.frame, text=name, bg=color)
        btn.pack(pady=10, fill="x")
        btn.bind("<ButtonPress-1>", lambda event, n=name, i=img: self.app.canvas_manager.start_drag(event, n, i))

