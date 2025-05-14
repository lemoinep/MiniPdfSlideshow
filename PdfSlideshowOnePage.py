# Author(s): Dr. Patrick Lemoine

import fitz  # PyMuPDF
import tkinter as tk
from PIL import Image, ImageTk
import argparse
import time


class PDFSlideshow(tk.Tk):
    def __init__(self, pdf_path):
        super().__init__()

        self.title("PDF Slideshow")
        self.attributes("-fullscreen", True)  
        bg_color = "#2f2f2f" 
        self.configure(bg=bg_color)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        scale_factor = 0.88
        canvas_width = int(screen_width * scale_factor)
        canvas_height = int(screen_height * scale_factor)

        self.doc = fitz.open(pdf_path)
        self.page_count = self.doc.page_count
        self.current_page_index = 0
        self.slider_changing = False

        self.main_frame = tk.Frame(self, bg=bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_frame, width=canvas_width, height=canvas_height,
                                bg="black", highlightthickness=0)
        self.canvas.pack(pady=40)
        self.canvas.pack_configure(anchor='center')

        self.slider = tk.Scale(self.main_frame, from_=0, to=self.page_count - 1,
                               orient=tk.HORIZONTAL, command=self.on_slider_move,
                               length=canvas_width, bg="#333333", fg="white",
                               troughcolor="#555555", highlightthickness=0)
        self.slider.pack(padx=0, pady=0)
        self.slider.pack_configure(anchor='center')


        self.bind("<Button-1>", self.next_page)  
        self.bind("<Button-3>", self.prev_page)  
        self.bind("<Escape>", lambda e: self.destroy())  
        self.bind("<space>", self.next_page)

        self.bind_all("<MouseWheel>", self.on_mouse_wheel)     
        self.bind_all("<Button-4>", self.on_mouse_wheel)       
        self.bind_all("<Button-5>", self.on_mouse_wheel)        

        self.photo_image = None

        self.clock_label = tk.Label(self, bg="#333333", fg="white", font=("Helvetica", 10))
        self.clock_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        self.after(100, lambda: self.show_page(self.current_page_index))

        self.update_clock()

    def render_page(self, page_index):
        page = self.doc.load_page(page_index)
        zoom = 2 
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        return img

    def show_page(self, page_index):
        img = self.render_page(page_index)
        canvas_width = int(self.canvas['width'])
        canvas_height = int(self.canvas['height'])
        img_ratio = img.width / img.height
        canvas_ratio = canvas_width / canvas_height

        if img_ratio > canvas_ratio:
            new_w = canvas_width
            new_h = int(canvas_width / img_ratio)
        else:
            new_h = canvas_height
            new_w = int(canvas_height * img_ratio)

        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        self.canvas.create_image(canvas_width // 2, canvas_height // 2,
                                 image=self.photo_image, anchor="center")

        self.slider_changing = True
        self.slider.set(page_index)
        self.slider_changing = False

        self.current_page_index = page_index

    def next_page(self, event=None):
        if self.current_page_index < self.page_count - 1:
            self.show_page(self.current_page_index + 1)

    def prev_page(self, event=None):
        if self.current_page_index > 0:
            self.show_page(self.current_page_index - 1)

    def on_slider_move(self, val):
        if self.slider_changing:
            return
        page_index = int(float(val))
        if page_index != self.current_page_index:
            self.show_page(page_index)

    def on_mouse_wheel(self, event):
        delta = 0
        if event.num == 4:
            delta = 1
        elif event.num == 5:
            delta = -1
        elif hasattr(event, 'delta'):
            delta = event.delta

        if delta > 0:
            self.prev_page()
        elif delta < 0:
            self.next_page()

    def update_clock(self):
        current_time = time.strftime('%H:%M:%S')
        self.clock_label.config(text=current_time)
        self.after(1000, self.update_clock)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF-SLIDESHOW")
    parser.add_argument("--Path", type=str, default=None, help="Path to the folder containing file")
    parser.add_argument("--Name", type=str, default=None, help="File Name")
    args = parser.parse_args()
    path=args.Path
    name=args.Name
    pdf_file = path+"/"+name
    app = PDFSlideshow(pdf_file)
    app.mainloop()
