import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD


class MinimalWhiteUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Converter & Resizer")
        self.root.geometry("900x600")
        self.root.configure(bg="#f7f7f7")

        self.selected_files = []

        self.build_ui()

    def build_ui(self):
        # Sidebar
        sidebar = tk.Frame(self.root, bg="white", width=230, relief="raised", bd=1)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="Image Tool",
                font=("Segoe UI", 18, "bold"),
                bg="white", fg="#333").pack(pady=20)
        
        # Drag & Drop Area
        self.drop_area = tk.Label(self.root,
                                text="Drag & Drop Images Here",
                                bg="#ffffff",
                                fg="#666",
                                relief="solid", bd=1,
                                font=("Segoe UI", 12),
                                width=40, height=4)

        self.drop_area.place(x=260, y=20)


        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.drop_handler)

        ttk.Button(sidebar, text="Select Images", command=self.select_images).pack(pady=10, padx=20, fill="x")
        ttk.Button(sidebar, text="Convert & Resize", command=self.process_images).pack(pady=10, padx=20, fill="x")

        # Options Card
        options_card = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        options_card.place(x=260, y=100, width=600, height=200)

        tk.Label(options_card, text="Options",
                font=("Segoe UI", 16, "bold"),
                bg="white", fg="#444").pack(pady=10)

        form_frame = tk.Frame(options_card, bg="white")
        form_frame.pack()

        # Output Format
        tk.Label(form_frame, text="Output Format:",
                font=("Segoe UI", 11),
                bg="white").grid(row=0, column=0, sticky="w", pady=5)

        self.format_var = ttk.Combobox(form_frame, values=["jpg", "png", "webp"], width=12)
        self.format_var.current(0)
        self.format_var.grid(row=0, column=1, padx=15)

        # Width
        tk.Label(form_frame, text="Width:",
                font=("Segoe UI", 11),
                bg="white").grid(row=1, column=0, sticky="w", pady=5)

        self.width_entry = ttk.Entry(form_frame, width=15)
        self.width_entry.grid(row=1, column=1)

        # Height
        tk.Label(form_frame, text="Height:",
                font=("Segoe UI", 11),
                bg="white").grid(row=2, column=0, sticky="w", pady=5)

        self.height_entry = ttk.Entry(form_frame, width=15)
        self.height_entry.grid(row=2, column=1)

        # Quality
        tk.Label(form_frame, text="Quality (1-100):",
                font=("Segoe UI", 11),
                bg="white").grid(row=3, column=0, sticky="w", pady=5)

        self.quality_slider = ttk.Scale(form_frame, from_=1, to=100)
        self.quality_slider.set(85)
        self.quality_slider.grid(row=3, column=1, pady=5)

        # Preview Card
        preview_card = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        preview_card.place(x=260, y=320, width=600, height=250)

        tk.Label(preview_card, text="Preview",
                font=("Segoe UI", 16, "bold"),
                bg="white", fg="#444").pack(pady=10)

        self.preview_label = tk.Label(preview_card, bg="white")
        self.preview_label.pack()

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=550, mode="determinate")
        self.progress.place(x=260, y=580)

    # Select Images
    def select_images(self):
        self.selected_files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp")]
        )
        if not self.selected_files:
            return

        self.show_preview(self.selected_files[0])
        messagebox.showinfo("Selected", f"{len(self.selected_files)} images selected!")

    # handle Drag and Drop files
    def drop_handler(self, event):
        # Get file paths from event
        files = self.root.splitlist(event.data)

        # Filter valid image files
        image_files = [
            f for f in files
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
        ]

        if not image_files:
            messagebox.showerror("Error", "No valid image files dropped!")
            return
        
        self.selected_files = image_files
        self.show_preview(self.selected_files[0])

        messagebox.showinfo("Dropped", f"{len(image_files)} images loaded!")

    # Image Preview
    def show_preview(self, file_path):
        img = Image.open(file_path)
        img.thumbnail((250, 250))
        self.preview_img = ImageTk.PhotoImage(img)
        self.preview_label.config(image=self.preview_img)

    # Image Processing
    def process_images(self):
        if not self.selected_files:
            messagebox.showerror("Error", "No images selected!")
            return

        output_folder = filedialog.askdirectory(title="Select Output Folder")
        if not output_folder:
            return

        new_width = self.width_entry.get()
        new_height = self.height_entry.get()
        quality = int(self.quality_slider.get())
        fmt = self.format_var.get()

        # Convert width/height safely
        try:
            new_width = int(new_width) if new_width else None
            new_height = int(new_height) if new_height else None
        except:
            messagebox.showerror("Error", "Width/Height must be numbers!")
            return

        self.progress["maximum"] = len(self.selected_files)
        self.progress["value"] = 0

        for file in self.selected_files:
            try:
                img = Image.open(file)

                # Resize logic
                if new_width and new_height:
                    img = img.resize((new_width, new_height))
                elif new_width:
                    ratio = new_width / img.width
                    img = img.resize((new_width, int(img.height * ratio)))
                elif new_height:
                    ratio = new_height / img.height
                    img = img.resize((int(img.width * ratio), new_height))

                filename = os.path.basename(file)
                new_name = os.path.splitext(filename)[0] + "." + fmt
                save_path = os.path.join(output_folder, new_name)

                # Convert for JPG/JPEG
                if fmt.lower() == "jpg":
                    img = img.convert("RGB")
                    format_for_pillow = "JPEG"
                else:
                    format_for_pillow = fmt.upper()

                # Save image
                img.save(save_path, format=format_for_pillow, quality=quality)


            except Exception as e:
                print("Error:", e)

            self.progress["value"] += 1
            self.root.update_idletasks()

        messagebox.showinfo("Success", "Images processed successfully!")

root = TkinterDnD.Tk()
app = MinimalWhiteUI(root)
root.mainloop()
