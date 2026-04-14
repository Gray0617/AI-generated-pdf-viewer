import tkinter as tk
from tkinter import filedialog, messagebox
from pdf2image import convert_from_path
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import sys

class PDFViewer:
    """
    A GUI-based PDF viewer with zoom, pan, and navigation features.
    Supports drag-and-drop PDF loading, mouse wheel zoom, and scrollbars for panning.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Reader")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Menu bar with File options
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_pdf)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

        # Frame to contain canvas and horizontal scrollbar
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for rendering PDF pages
        self.canvas = tk.Canvas(self.frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_resize)  # Handle window resize
        self.canvas.bind("<MouseWheel>", self.on_zoom)   # Handle zoom
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)  # Start drag
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)     # Drag motion
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_release)  # End drag
        self.canvas.drop_target_register(DND_FILES)      # Enable drag-and-drop
        self.canvas.dnd_bind('<<Drop>>', self.on_drop)   # Bind drop event

        # No scrollbars, using drag panning instead

        # Navigation frame at bottom
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.prev_button = tk.Button(nav_frame, text="Previous", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.page_label = tk.Label(nav_frame, text="Page: 0 / 0")
        self.page_label.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(nav_frame, text="Next", command=self.next_page)
        self.next_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # Initialize state variables
        self.images = []          # List of PIL images for PDF pages
        self.current_page = 0     # Current page index
        self.photo = None         # Tkinter PhotoImage for canvas
        self.zoom_factor = 1.0    # Current zoom level
        self.offset_x = 0         # X offset for panning
        self.offset_y = 0         # Y offset for panning
        self.drag_start_x = 0     # Drag start X position
        self.drag_start_y = 0     # Drag start Y position
        self.is_dragging = False  # Drag state flag

    def open_pdf(self):
        """Open file dialog to select and load a PDF file."""
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):
        """Load PDF from file path, convert to images, and display first page."""
        try:
            self.images = convert_from_path(file_path)  # Convert PDF pages to PIL images
            self.current_page = 0
            self.zoom_factor = 1.0  # Reset zoom
            self.display_page()
            # Center the image
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            self.offset_x = (canvas_w - self.photo.width()) // 2
            self.offset_y = (canvas_h - self.photo.height()) // 2
            self.display_page()  # Redisplay with centered offset
            self.update_buttons()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF: {e}")

    def display_page(self):
        """Render the current page on the canvas with current zoom."""
        if self.images:
            image = self.images[self.current_page]
            img_width, img_height = image.size
            new_width = int(img_width * self.zoom_factor)
            new_height = int(img_height * self.zoom_factor)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)
            self.canvas.delete("all")
            self.canvas.create_image(self.offset_x, self.offset_y, anchor=tk.NW, image=self.photo)
            self.page_label.config(text=f"Page: {self.current_page + 1} / {len(self.images)}")

    def prev_page(self):
        """Navigate to previous page if available."""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()
            # Center the image
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            self.offset_x = (canvas_w - self.photo.width()) // 2
            self.offset_y = (canvas_h - self.photo.height()) // 2
            self.display_page()
            self.update_buttons()

    def next_page(self):
        """Navigate to next page if available."""
        if self.current_page < len(self.images) - 1:
            self.current_page += 1
            self.display_page()
            # Center the image
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            self.offset_x = (canvas_w - self.photo.width()) // 2
            self.offset_y = (canvas_h - self.photo.height()) // 2
            self.display_page()
            self.update_buttons()

    def on_resize(self, event):
        """Handle window resize by redisplaying the page."""
        if self.images:
            self.display_page()
            # Center if image fits in new canvas size
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            if self.photo.width() <= canvas_w:
                self.offset_x = (canvas_w - self.photo.width()) // 2
            if self.photo.height() <= canvas_h:
                self.offset_y = (canvas_h - self.photo.height()) // 2
            self.display_page()

    def on_zoom(self, event):
        """Handle mouse wheel zoom, centering on mouse cursor."""
        if self.images:
            # Get mouse position relative to canvas
            mouse_x = event.x
            mouse_y = event.y
            # Get current image size
            img_width, img_height = self.images[self.current_page].size
            old_zoom = self.zoom_factor
            # Adjust zoom factor
            delta = event.delta
            if delta > 0:
                self.zoom_factor *= 1.1
            else:
                self.zoom_factor /= 1.1
            self.zoom_factor = max(0.1, min(self.zoom_factor, 5.0))  # Clamp zoom
            # Calculate position in original image
            img_x = (mouse_x - self.offset_x) / old_zoom
            img_y = (mouse_y - self.offset_y) / old_zoom
            # Redisplay (this centers the image)
            self.display_page()
            # Adjust offset to keep mouse position
            new_img_x = img_x * self.zoom_factor
            new_img_y = img_y * self.zoom_factor
            self.offset_x = mouse_x - new_img_x
            self.offset_y = mouse_y - new_img_y
            # Center if image fits in canvas
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            if self.photo.width() <= canvas_w:
                self.offset_x = (canvas_w - self.photo.width()) // 2
            if self.photo.height() <= canvas_h:
                self.offset_y = (canvas_h - self.photo.height()) // 2
            # Redisplay with adjusted offset
            self.display_page()

    def on_drag_start(self, event):
        """Start dragging the image."""
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag_motion(self, event):
        """Handle drag motion to pan the image."""
        if self.is_dragging and self.photo:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            image_w = self.photo.width()
            image_h = self.photo.height()
            # Only allow horizontal drag if image is wider than canvas
            if image_w > canvas_w:
                self.offset_x += dx
                self.offset_x = max(canvas_w - image_w, min(0, self.offset_x))
            else:
                self.offset_x = max(0, min(canvas_w - image_w, self.offset_x))
            # Only allow vertical drag if image is taller than canvas
            if image_h > canvas_h:
                self.offset_y += dy
                self.offset_y = max(canvas_h - image_h, min(0, self.offset_y))
            else:
                self.offset_y = max(0, min(canvas_h - image_h, self.offset_y))
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.display_page()

    def on_drag_release(self, event):
        """End dragging."""
        self.is_dragging = False

    def on_drop(self, event):
        """Handle drag-and-drop of PDF files."""
        file_path = event.data.strip('{}')  # Clean path
        if file_path.lower().endswith('.pdf'):
            self.load_pdf(file_path)
        else:
            messagebox.showwarning("Warning", "Please drop a PDF file.")

    def update_buttons(self):
        """Enable/disable navigation buttons based on current page."""
        self.prev_button.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_page < len(self.images) - 1 else tk.DISABLED)

def main():
    """Main entry point: Create TkinterDnD root and start the PDF viewer."""
    root = TkinterDnD.Tk()
    app = PDFViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()