import os
import cv2
import json
import tkinter as tk
from tkinter import ttk, Canvas, filedialog, Listbox
from PIL import Image, ImageTk

class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Annotation App")
        self.root.geometry("1280x720")

        self.img = None
        self.output_path = None
        self.img_original = None
        self.scale_x = 1
        self.scale_y = 1
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.start_x = 0
        self.start_y = 0

        self.setup_ui()
        self.image_folder_path = None
        self.image_list = []
        self.current_image_index = None
        self.rectangles_templates = []
        self.lines = []

    def setup_ui(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        top_inner_frame = ttk.Frame(top_frame)
        top_inner_frame.pack(expand=True)

        ttk.Button(top_inner_frame, text="Open Folder", command=self.open_folder).pack(side=tk.LEFT, padx=10)
        ttk.Button(top_inner_frame, text="Wall", command=self.select_templates).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(top_inner_frame, text="SF", command=self.select_scale_line).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(top_inner_frame, text="Save", command=self.save_data).pack(side=tk.LEFT, padx=10, pady=10)

        left_frame = ttk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.image_listbox = Listbox(left_frame)
        self.image_listbox.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)

        self.canvas = Canvas(self.root, bg='gray')
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.do_pan)

    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_folder_path = folder_path
            self.image_list = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            self.image_listbox.delete(0, tk.END)
            for image_name in self.image_list:
                self.image_listbox.insert(tk.END, image_name)
                # Check if JSON file exists for each image
                json_path = os.path.splitext(os.path.join(folder_path, image_name))[0] + ".json"
                if os.path.exists(json_path):
                    self.image_listbox.itemconfig(tk.END, bg='green')

    def on_image_select(self, event):
        if self.image_listbox.curselection():
            index = self.image_listbox.curselection()[0]
            self.current_image_index = index
            image_name = self.image_list[index]
            image_path = os.path.join(self.image_folder_path, image_name)
            self.load_image(image_path)

    def load_image(self, image_path):
        self.img_original = cv2.imread(image_path)
        if self.img_original is not None:
            self.img = cv2.cvtColor(self.img_original, cv2.COLOR_BGR2RGB)
            self.zoom_factor = 1.0
            self.pan_x = 0
            self.pan_y = 0
            self.rectangles_templates = []
            self.lines = []
            self.output_path = os.path.splitext(image_path)[0] + ".json"
            self.fit_image_to_canvas()
            self.display_image()

    def fit_image_to_canvas(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width == 1 or canvas_height == 1:  # Prevent issues if canvas size is not updated yet
            self.root.update()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

        height, width, _ = self.img.shape
        scale_width = canvas_width / width
        scale_height = canvas_height / height
        self.zoom_factor = min(scale_width, scale_height)

    def resize_image(self, image, width, height):
        h, w, _ = image.shape
        self.scale_x = w / width
        self.scale_y = h / height
        resized_image = cv2.resize(image, (width, height))
        return resized_image

    def display_image(self):
        if self.img is not None:
            height, width, _ = self.img.shape
            new_width = int(width * self.zoom_factor)
            new_height = int(height * self.zoom_factor)
            resized_image = cv2.resize(self.img, (new_width, new_height))
            self.imgtk = ImageTk.PhotoImage(image=Image.fromarray(resized_image))
            self.canvas.delete("all")
            self.canvas.create_image(self.pan_x, self.pan_y, anchor=tk.NW, image=self.imgtk)
            self.redraw_shapes()

    def zoom(self, event):
        if event.delta > 0:
            self.zoom_factor *= 1.1
        elif event.delta < 0:
            self.zoom_factor /= 1.1
        self.display_image()

    def start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)
        self.start_x = event.x
        self.start_y = event.y

    def do_pan(self, event):
        self.pan_x += event.x - self.start_x
        self.pan_y += event.y - self.start_y
        self.start_x = event.x
        self.start_y = event.y
        self.display_image()

    def redraw_shapes(self):
        self.draw_existing_shapes(self.rectangles_templates, "#00FF00")
        self.draw_existing_shapes(self.lines, "#0000FF", line=True)

    def draw_existing_shapes(self, shapes, color, line=False):
        for shape in shapes:
            if line:
                self.canvas.create_line(shape[0][0] * self.zoom_factor + self.pan_x,
                                        shape[0][1] * self.zoom_factor + self.pan_y,
                                        shape[1][0] * self.zoom_factor + self.pan_x,
                                        shape[1][1] * self.zoom_factor + self.pan_y,
                                        fill=color)
            else:
                self.canvas.create_rectangle(shape[0][0] * self.zoom_factor + self.pan_x,
                                             shape[0][1] * self.zoom_factor + self.pan_y,
                                             shape[1][0] * self.zoom_factor + self.pan_x,
                                             shape[1][1] * self.zoom_factor + self.pan_y,
                                             outline=color)

    def select_templates(self):
        self.draw_rectangle("#00FF00", self.rectangles_templates)

    def select_scale_line(self):
        self.draw_line("#0000FF", self.lines)

    def draw_rectangle(self, color, rectangles):
        self.drawing = False
        self.rectangle = None

        def draw_rectangle_event(event):
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            x = int((x - self.pan_x) / self.zoom_factor)
            y = int((y - self.pan_y) / self.zoom_factor)
            if event.type == tk.EventType.ButtonPress:
                self.drawing = True
                self.rectangle = [(x, y)]
            elif event.type == tk.EventType.Motion and self.drawing:
                self.canvas.delete("temp_rect")
                self.canvas.create_rectangle(self.rectangle[0][0] * self.zoom_factor + self.pan_x,
                                             self.rectangle[0][1] * self.zoom_factor + self.pan_y,
                                             x * self.zoom_factor + self.pan_x,
                                             y * self.zoom_factor + self.pan_y,
                                             outline=color, tag="temp_rect")
            elif event.type == tk.EventType.ButtonRelease and self.drawing:
                self.drawing = False
                self.rectangle.append((x, y))
                rectangles.append(self.convert_coordinates(self.rectangle))
                self.canvas.create_rectangle(self.rectangle[0][0] * self.zoom_factor + self.pan_x,
                                             self.rectangle[0][1] * self.zoom_factor + self.pan_y,
                                             x * self.zoom_factor + self.pan_x,
                                             y * self.zoom_factor + self.pan_y,
                                             outline=color)
                self.canvas.delete("temp_rect")

        self.canvas.bind("<ButtonPress-1>", draw_rectangle_event)
        self.canvas.bind("<B1-Motion>", draw_rectangle_event)
        self.canvas.bind("<ButtonRelease-1>", draw_rectangle_event)

    def draw_line(self, color, lines):
        self.drawing = False
        self.line = None

        def draw_line_event(event):
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            x = int((x - self.pan_x) / self.zoom_factor)
            y = int((y - self.pan_y) / self.zoom_factor)
            if event.type == tk.EventType.ButtonPress:
                self.drawing = True
                self.line = [(x, y)]
            elif event.type == tk.EventType.Motion and self.drawing:
                self.canvas.delete("temp_line")
                self.canvas.create_line(self.line[0][0] * self.zoom_factor + self.pan_x,
                                        self.line[0][1] * self.zoom_factor + self.pan_y,
                                        x * self.zoom_factor + self.pan_x,
                                        y * self.zoom_factor + self.pan_y,
                                        fill=color, tag="temp_line")
            elif event.type == tk.EventType.ButtonRelease and self.drawing:
                self.drawing = False
                self.line.append((x, y))
                lines.append(self.convert_coordinates(self.line))
                self.canvas.create_line(self.line[0][0] * self.zoom_factor + self.pan_x,
                                        self.line[0][1] * self.zoom_factor + self.pan_y,
                                        x * self.zoom_factor + self.pan_x,
                                        y * self.zoom_factor + self.pan_y,
                                        fill=color)
                self.canvas.delete("temp_line")

        self.canvas.bind("<ButtonPress-1>", draw_line_event)
        self.canvas.bind("<B1-Motion>", draw_line_event)
        self.canvas.bind("<ButtonRelease-1>", draw_line_event)

    def convert_coordinates(self, coordinates):
        return [(int(x * self.scale_x), int(y * self.scale_y)) for x, y in coordinates]

    def save_data(self):
        data = {
            "wall": self.rectangles_templates,
            "line": self.lines,
        }

        with open(self.output_path, "w") as f:
            json.dump(data, f)

        # Highlight the image in the listbox as completed
        if self.current_image_index is not None:
            self.image_listbox.itemconfig(self.current_image_index, bg='green')

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()
