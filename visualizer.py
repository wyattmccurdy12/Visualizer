import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageProcessorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Image Processing GUI")
        master.geometry("1200x800")

        self.image = None
        self.processed_image = None
        self.kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        self.kernel_size = 3
        self.step_row = 0
        self.step_col = 0
        self.playing = False

        self.create_widgets()

    def create_widgets(self):
        # Kernel Input
        self.kernel_frame = tk.Frame(self.master)
        self.kernel_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        self.kernel_entries = []
        for i in range(3):
            row_entries = []
            for j in range(3):
                entry = tk.Entry(self.kernel_frame, width=5)
                entry.insert(0, str(self.kernel[i, j]))
                entry.grid(row=i, column=j, padx=5, pady=5)
                row_entries.append(entry)
            self.kernel_entries.append(row_entries)

        # Expression Input
        self.expression_label = tk.Label(self.master, text="Kernel Expression:")
        self.expression_label.grid(row=4, column=0, padx=5, pady=5)
        self.expression_entry = tk.Entry(self.master, width=30)
        self.expression_entry.grid(row=4, column=1, padx=5, pady=5)
        self.expression_entry.insert(0, "lambda x, y: 1 if (x-1)**2 + (y-1)**2 < 1 else 0")  # Example

        # Buttons
        self.load_button = tk.Button(self.master, text="Load Image", command=self.load_image)
        self.load_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.process_button = tk.Button(self.master, text="Process Step", command=self.process_step)
        self.process_button.grid(row=2, column=0, padx=5, pady=5)
        self.play_button = tk.Button(self.master, text="Play", command=self.toggle_play)
        self.play_button.grid(row=2, column=1, padx=5, pady=5)
        self.apply_expression_button = tk.Button(self.master, text="Apply Expression", command=self.apply_expression)
        self.apply_expression_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Grids (Canvases)
        self.left_grid = tk.Canvas(self.master, width=400, height=400, bg='white')
        self.left_grid.grid(row=3, column=0, padx=5, pady=5)
        self.right_grid = tk.Canvas(self.master, width=400, height=400, bg='white')
        self.right_grid.grid(row=3, column=1, padx=5, pady=5)

    def load_image(self):
        filepath = filedialog.askopenfilename(
            title="Select Image", filetypes=(("Image files", "*.jpg;*.jpeg;*.png"),)
        )
        if filepath:
            try:
                self.image = np.array(Image.open(filepath).convert('L'))  # Load as grayscale
                self.processed_image = np.zeros_like(self.image, dtype=np.float32)
                self.step_row = 0
                self.step_col = 0
                self.update_image_display()
            except Exception as e:
                print(f"Error loading image: {e}")

    def update_image_display(self):
        if self.image is None:
            return

        img = Image.fromarray(self.image)
        img = img.resize((400, 400), Image.LANCZOS)
        self.img_tk = ImageTk.PhotoImage(image=img)
        self.left_grid.create_image(0, 0, anchor=tk.NW, image=self.img_tk)

        self.update_processed_grid()
        self.update_kernel_overlay()

    def update_processed_grid(self):
        if self.processed_image is None:
            return

        # Scale processed image for display (min-max scaling)
        min_val = np.min(self.processed_image)
        max_val = np.max(self.processed_image)
        scaled_image = (self.processed_image - min_val) / (max_val - min_val) * 255
        scaled_image = scaled_image.astype(np.uint8)

        processed_img = Image.fromarray(scaled_image)
        processed_img = processed_img.resize((400, 400), Image.LANCZOS)
        self.processed_img_tk = ImageTk.PhotoImage(image=processed_img)
        self.right_grid.create_image(0, 0, anchor=tk.NW, image=self.processed_img_tk)

    def get_kernel_values(self):
        try:
            kernel = np.zeros((3, 3), dtype=np.float32)
            for i in range(3):
                for j in range(3):
                    kernel[i, j] = float(self.kernel_entries[i][j].get())
            return kernel
        except ValueError:
            print("Invalid kernel values. Using default kernel.")
            return np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])

    def apply_expression(self):
        expression_str = self.expression_entry.get()
        try:
            # Evaluate the expression string to create a lambda function
            kernel_func = eval(expression_str)
            # Create the kernel using np.fromfunction
            self.kernel = np.fromfunction(kernel_func, (3, 3))
            # Update the kernel entries in the GUI
            for i in range(3):
                for j in range(3):
                    self.kernel_entries[i][j].delete(0, tk.END)
                    self.kernel_entries[i][j].insert(0, str(self.kernel[i, j]))
            print("Kernel updated from expression.")
        except Exception as e:
            print(f"Error applying expression: {e}")
            self.kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]) # Reset to default kernel

    def process_step(self):
        if self.image is None:
            return

        kernel = self.get_kernel_values()
        kernel_size = kernel.shape[0]
        half_kernel = kernel_size // 2

        rows, cols = self.image.shape

        if self.step_row < rows - kernel_size + 1:
            if self.step_col < cols - kernel_size + 1:
                roi = self.image[self.step_row:self.step_row + kernel_size, self.step_col:self.step_col + kernel_size].astype(np.float32)
                self.processed_image[self.step_row + half_kernel, self.step_col + half_kernel] = np.sum(roi * kernel)
                self.step_col += 1
            else:
                self.step_col = 0
                self.step_row += 1
        else:
            self.playing = False
            self.play_button.config(text="Play")
            self.step_row = 0
            self.step_col = 0

        self.update_processed_grid()
        self.update_kernel_overlay()

    def update_kernel_overlay(self):
        if self.image is None:
            return

        cell_size = 400 / self.image.shape[1]  # Dynamic cell size
        self.left_grid.delete("kernel")

        kernel_size = self.kernel.shape[0]
        half_kernel = kernel_size // 2

        if self.step_row < self.image.shape[0] - kernel_size + 1 and self.step_col < self.image.shape[1] - kernel_size + 1:
            for i in range(kernel_size):
                for j in range(kernel_size):
                    x0 = (self.step_col + j) * cell_size
                    y0 = (self.step_row + i) * cell_size
                    x1 = x0 + cell_size
                    y1 = y0 + cell_size
                    self.left_grid.create_rectangle(x0, y0, x1, y1, outline='blue', width=2, tags="kernel")

    def toggle_play(self):
        self.playing = not self.playing
        if self.playing:
            self.play_button.config(text="Pause")
            self.auto_process()
        else:
            self.play_button.config(text="Play")

    def auto_process(self):
        if self.playing:
            self.process_step()
            self.master.after(50, self.auto_process)  # Adjust delay as needed

root = tk.Tk()
gui = ImageProcessorGUI(root)
root.mainloop()