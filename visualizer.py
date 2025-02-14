import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import random

class ImageProcessorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Image Processing GUI")
        master.geometry("1200x800")

        self.processed_image = None
        self.kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        self.kernel_size = 3
        self.step_row = 0
        self.step_col = 0
        self.playing = False
        self.display_width = 500  # Set the display width
        self.display_height = 500  # Set the display height
        self.grid_size = 20
        self.number_grid = np.random.rand(self.grid_size, self.grid_size)  # Initialize number grid with values between 0 and 1
        self.processed_grid = np.zeros_like(self.number_grid, dtype=np.float32)
        self.display_mode = "numbers"  # Default display mode

        self.create_widgets()

    def create_widgets(self):
        # Grid Size Input
        self.grid_size_label = tk.Label(self.master, text="Grid Size:")
        self.grid_size_label.grid(row=6, column=0, padx=5, pady=5)
        self.grid_size_entry = tk.Entry(self.master, width=10)
        self.grid_size_entry.grid(row=6, column=1, padx=5, pady=5)
        self.grid_size_entry.insert(0, str(self.grid_size))  # Default value
        self.update_grid_button = tk.Button(self.master, text="Update Grid", command=self.update_grid_size)
        self.update_grid_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

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
        self.expression_entry.insert(0, "1 if (x-1)**2 + (y-1)**2 < 1 else 0")  # Example

        # Buttons
        self.process_button = tk.Button(self.master, text="Process Step", command=self.process_step)
        self.process_button.grid(row=2, column=0, padx=5, pady=5)
        self.play_button = tk.Button(self.master, text="Play", command=self.toggle_play)
        self.play_button.grid(row=2, column=1, padx=5, pady=5)
        self.apply_expression_button = tk.Button(self.master, text="Apply Expression", command=self.apply_expression)
        self.apply_expression_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Display Mode Button
        self.toggle_display_button = tk.Button(self.master, text="Toggle Display", command=self.toggle_display_mode)
        self.toggle_display_button.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

        # Grids (Canvases)
        self.left_grid = tk.Canvas(self.master, width=self.display_width, height=self.display_height, bg='white', highlightthickness=0)
        self.left_grid.grid(row=3, column=0, padx=5, pady=5)
        self.right_grid = tk.Canvas(self.master, width=self.display_width, height=self.display_height, bg='white', highlightthickness=0)
        self.right_grid.grid(row=3, column=1, padx=5, pady=5)

        self.draw_grid(self.left_grid)
        self.draw_grid(self.right_grid)
        self.update_display()

    def draw_grid(self, canvas):
        canvas.delete("grid_line")  # Clear old grid lines
        for i in range(self.grid_size + 1):
            # Vertical lines
            x = i * (self.display_width / self.grid_size)
            canvas.create_line(x, 0, x, self.display_height, fill="black", tags="grid_line")
            # Horizontal lines
            y = i * (self.display_height / self.grid_size)
            canvas.create_line(0, y, self.display_width, y, fill="black", tags="grid_line")

    def update_number_display(self):
        self.left_grid.delete("number_value")  # Remove previous numbers
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                number = self.number_grid[i, j]
                x1 = j * (self.display_width / self.grid_size)
                y1 = i * (self.display_height / self.grid_size)
                x2 = x1 + (self.display_width / self.grid_size)
                y2 = y1 + (self.display_height / self.grid_size)
                self.left_grid.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text=str(number),
                    fill="blue",  # Choose a color that stands out
                    tags="number_value"
                )

    def update_grayscale_display(self):
        self.left_grid.delete("grayscale_value")  # Remove previous grayscale values
        cell_width = self.display_width / self.grid_size
        cell_height = self.display_height / self.grid_size

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                intensity = int(self.number_grid[i, j] * 255)  # Scale to 0-255
                hex_color = '#%02x%02x%02x' % (intensity, intensity, intensity)  # Create hex color string
                x1 = j * cell_width
                y1 = i * cell_height
                x2 = x1 + cell_width
                y2 = y1 + cell_height
                self.left_grid.create_rectangle(x1, y1, x2, y2, fill=hex_color, outline="", tags="grayscale_value")

    def update_processed_display(self):
        self.right_grid.delete("processed_value")
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                number = self.processed_grid[i, j]
                x1 = j * (self.display_width / self.grid_size)
                y1 = i * (self.display_height / self.grid_size)
                x2 = x1 + (self.display_width / self.grid_size)
                y2 = y1 + (self.display_height / self.grid_size)
                self.right_grid.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text=str(number),
                    fill="red",  # Choose a color that stands out
                    tags="processed_value"
                )

    def update_display(self):
        if self.display_mode == "numbers":
            self.update_number_display()
        else:
            self.update_grayscale_display()
        self.update_kernel_overlay()

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
            # Modify the expression to include lambda x, y:
            if "lambda" not in expression_str:
                expression_str = "lambda x, y: " + expression_str
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
        kernel = self.get_kernel_values()
        kernel_size = kernel.shape[0]
        half_kernel = kernel_size // 2

        rows, cols = self.number_grid.shape

        # Initialize processed_image if it's None
        if self.processed_image is None:
            self.processed_image = np.zeros_like(self.number_grid, dtype=np.float32)

        if self.step_row < rows - kernel_size + 1:
            if self.step_col < cols - kernel_size + 1:
                roi = self.number_grid[self.step_row:self.step_row + kernel_size, self.step_col:self.step_col + kernel_size].astype(np.float32)
                self.processed_grid[self.step_row + half_kernel, self.step_col + half_kernel] = np.sum(roi * kernel)
                self.step_col += 1
            else:
                self.step_col = 0
                self.step_row += 1
        else:
            self.playing = False
            self.play_button.config(text="Play")
            self.step_row = 0
            self.step_col = 0

        self.update_processed_display()
        self.update_kernel_overlay()

    def update_kernel_overlay(self):
        cell_size = self.display_width / self.grid_size  # Dynamic cell size
        self.left_grid.delete("kernel")

        kernel_size = self.kernel.shape[0]
        half_kernel = kernel_size // 2

        if self.step_row < self.number_grid.shape[0] - kernel_size + 1 and self.step_col < self.number_grid.shape[1] - kernel_size + 1:
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

    def update_grid_size(self):
        try:
            new_grid_size = int(self.grid_size_entry.get())
            if new_grid_size > 0:
                self.grid_size = new_grid_size
                self.number_grid = np.random.rand(self.grid_size, self.grid_size)  # Generate new random grid
                self.processed_grid = np.zeros_like(self.number_grid, dtype=np.float32)
                self.draw_grid(self.left_grid)
                self.draw_grid(self.right_grid)
                self.update_display()
            else:
                print("Grid size must be a positive integer.")
        except ValueError:
            print("Invalid grid size. Please enter an integer.")

    def toggle_display_mode(self):
        if self.display_mode == "numbers":
            self.display_mode = "grayscale"
        else:
            self.display_mode = "numbers"
        self.update_display()

root = tk.Tk()
gui = ImageProcessorGUI(root)
root.mainloop()