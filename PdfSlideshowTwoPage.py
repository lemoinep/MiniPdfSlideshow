import fitz  # PyMuPDF
import tkinter as tk
from PIL import Image, ImageTk
import argparse
import time


class PDFSlideshow(tk.Tk):
    def __init__(self, pdf_path):
        super().__init__()

        self.title("PDF Slideshow Two Page")
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

        self.double_page_count = (self.page_count + 1) // 2

        self.current_double_index = 0
        self.slider_changing = False

        self.main_frame = tk.Frame(self, bg=bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_frame, width=canvas_width, height=canvas_height,
                                bg="black", highlightthickness=0)
        self.canvas.pack(pady=40)
        self.canvas.pack_configure(anchor='center')

        self.slider = tk.Scale(self.main_frame, from_=0, to=self.double_page_count - 1,
                               orient=tk.HORIZONTAL, command=self.on_slider_move,
                               length=canvas_width, bg="#333333", fg="white",
                               troughcolor="#555555", highlightthickness=0)
        self.slider.pack(padx=0, pady=0)
        self.slider.pack_configure(anchor='center')

        self.bind("<Button-1>", self.next_double_page)  
        self.bind("<Button-3>", self.prev_double_page)  
        self.bind("<Escape>", lambda e: self.destroy())  
        
        self.bind("<space>", self.next_double_page)

        self.bind_all("<MouseWheel>", self.on_mouse_wheel)    
        self.bind_all("<Button-4>", self.on_mouse_wheel)       
        self.bind_all("<Button-5>", self.on_mouse_wheel)        

        self.photo_images = [] 

        self.clock_label = tk.Label(self, bg="#333333", fg="white", font=("Helvetica", 10))
        self.clock_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        self.after(100, lambda: self.show_double_page(self.current_double_index))
        self.update_clock()

    def render_page(self, page_index):
        page = self.doc.load_page(page_index)
        zoom = 2
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        return img

    def show_double_page(self, double_index):
        page1_index = double_index * 2
        page2_index = page1_index + 1

        img1 = self.render_page(page1_index)
        img2 = self.render_page(page2_index) if page2_index < self.page_count else None

        canvas_width = int(self.canvas['width'])
        canvas_height = int(self.canvas['height'])

        half_width = canvas_width // 2

        def resize_img(img, max_w, max_h):
            img_ratio = img.width / img.height
            canvas_ratio = max_w / max_h
            if img_ratio > canvas_ratio:
                new_w = max_w
                new_h = int(max_w / img_ratio)
            else:
                new_h = max_h
                new_w = int(max_h * img_ratio)
            return img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        img1_resized = resize_img(img1, half_width, canvas_height)
        if img2 is not None:
            img2_resized = resize_img(img2, half_width, canvas_height)
        else:
            img2_resized = None

        self.photo_images = []
        photo1 = ImageTk.PhotoImage(img1_resized)
        self.photo_images.append(photo1)
        if img2_resized:
            photo2 = ImageTk.PhotoImage(img2_resized)
            self.photo_images.append(photo2)

        self.canvas.delete("all")
        
        e = 52       
        e = (canvas_width/2 - img1_resized.width) / 2 - 5

        x1 = half_width // 2 + e
        y1 = canvas_height // 2
        self.canvas.create_image(x1, y1, image=photo1, anchor="center")

        if img2_resized:
            x2 = half_width + half_width // 2 - e 
            y2 = canvas_height // 2
            self.canvas.create_image(x2, y2, image=photo2, anchor="center")

        self.slider_changing = True
        self.slider.set(double_index)
        self.slider_changing = False

        self.current_double_index = double_index

    def next_double_page(self, event=None):
        if self.current_double_index < self.double_page_count - 1:
            self.show_double_page(self.current_double_index + 1)

    def prev_double_page(self, event=None):
        if self.current_double_index > 0:
            self.show_double_page(self.current_double_index - 1)

    def on_slider_move(self, val):
        if self.slider_changing:
            return
        double_index = int(float(val))
        if double_index != self.current_double_index:
            self.show_double_page(double_index)

    def on_mouse_wheel(self, event):
        delta = 0
        if event.num == 4:
            delta = 1
        elif event.num == 5:
            delta = -1
        elif hasattr(event, 'delta'):
            delta = event.delta

        if delta > 0:
            self.prev_double_page()
        elif delta < 0:
            self.next_double_page()

    def update_clock(self):
        current_time = time.strftime('%H:%M:%S')
        self.clock_label.config(text=current_time)
        self.after(1000, self.update_clock)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF-SLIDESHOW-TWO-PAGE")
    parser.add_argument("--Path", type=str, default=None, help="Path to the folder containing file")
    parser.add_argument("--Name", type=str, default=None, help="File Name")
    args = parser.parse_args()
    path=args.Path
    name=args.Name
    pdf_file = path+"/"+name
    app = PDFSlideshow(pdf_file)
    app.mainloop()
