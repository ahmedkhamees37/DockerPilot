import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class TopBar:
    def __init__(self, root, app):
        self.app = app
        self.frame = tk.Frame(root, height=50, bg="gray")
        self.frame.pack(side="top", fill="x")

        # Load images for buttons
        try:
            start_img = Image.open("start.png").resize((30, 30))
            stop_img = Image.open("stop.png").resize((30, 30))
            self.start_img = ImageTk.PhotoImage(start_img)
            self.stop_img = ImageTk.PhotoImage(stop_img)
        except FileNotFoundError:
            messagebox.showerror("Error", "Image files (start.png, stop.png) not found!")
            root.destroy()
            return

        # Add buttons to the top bar
        self.btn_stop = tk.Button(self.frame, image=self.stop_img, command=lambda: self.app.show_message("Stop"))
        self.btn_stop.pack(side="right", padx=10, pady=5)

        self.btn_start = tk.Button(self.frame, image=self.start_img, command=self.app.run_code)
        self.btn_start.pack(side="right", padx=10, pady=5)

