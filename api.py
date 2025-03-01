from flask import Flask, request, jsonify, render_template
import numpy as np
import sympy as sp
from latex2sympy2 import latex2sympy as lts

class VisualizerApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.grid_size = 10  # Default grid size set to 10
        self.number_grid = np.zeros((self.grid_size, self.grid_size))
        self.number_grid[:, self.grid_size // 2] = 1  # Vertical stripe of white on a black background
        self.processed_grid = np.zeros_like(self.number_grid, dtype=np.float32)
        self.kernel_size = 3
        self.kernel = np.ones((self.kernel_size, self.kernel_size))  # Default kernel
        self.step_row = 0
        self.step_col = 0
        self.playing = False
        self.display_mode = "numbers"  # Default display mode
        self.setup_routes()

    def setup_routes(self):
        self.app.add_url_rule('/update_grid_size', 'update_grid_size', self.update_grid_size, methods=['POST'])
        self.app.add_url_rule('/update_kernel_size', 'update_kernel_size', self.update_kernel_size, methods=['POST'])
        self.app.add_url_rule('/apply_expression', 'apply_expression', self.apply_expression, methods=['POST'])
        self.app.add_url_rule('/translate_expression', 'translate_expression', self.translate_expression, methods=['POST'])
        self.app.add_url_rule('/process_step', 'process_step', self.process_step, methods=['POST'])
        self.app.add_url_rule('/toggle_play', 'toggle_play', self.toggle_play, methods=['POST'])
        self.app.add_url_rule('/toggle_display_mode', 'toggle_display_mode', self.toggle_display_mode, methods=['POST'])
        self.app.add_url_rule('/get_grid', 'get_grid', self.get_grid, methods=['GET'])
        self.app.add_url_rule('/latex_to_kernel', 'latex_to_kernel', self.latex_to_kernel_endpoint, methods=['POST'])
        self.app.add_url_rule('/', 'index', self.index)

    def update_grid_size(self):
        data = request.json
        new_grid_size = data.get('grid_size', self.grid_size)
        if 0 < new_grid_size <= 20:  # Limit grid size to a maximum of 20
            self.grid_size = new_grid_size
            self.number_grid = np.zeros((self.grid_size, self.grid_size))
            self.number_grid[:, self.grid_size // 2] = 1  # Vertical stripe of white on a black background
            self.processed_grid = np.zeros_like(self.number_grid, dtype=np.float32)
            return jsonify({"message": "Grid size updated", "grid_size": self.grid_size}), 200
        else:
            return jsonify({"error": "Grid size must be a positive integer and less than or equal to 20"}), 400

    def update_kernel_size(self):
        data = request.json
        new_kernel_size = data.get('kernel_size', self.kernel_size)
        if new_kernel_size > 0:
            self.kernel_size = new_kernel_size
            self.kernel = np.ones((self.kernel_size, self.kernel_size))  # Reset kernel to ones
            return jsonify({"message": "Kernel size updated", "kernel_size": self.kernel_size}), 200
        else:
            return jsonify({"error": "Kernel size must be a positive integer"}), 400

    def apply_expression(self):
        data = request.json
        expression_str = data.get('expression')
        try:
            self.kernel_from_expression(expression_str)
            return jsonify({"message": "Kernel updated from expression", "kernel": self.kernel.tolist()}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def translate_expression(self):
        data = request.json
        expression = data.get('expression')
        try:
            sympy_expr = lts(expression)
            sympy_expr_str = str(sympy_expr)
            return jsonify({"translated_expression": sympy_expr_str}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def kernel_from_expression(self, expression):
        if "lambda" not in expression:
            expression = "lambda x, y: " + expression
        kernel_func = eval(expression)
        self.kernel = np.fromfunction(kernel_func, (self.kernel_size, self.kernel_size))

    def latex_to_kernel(self, latex_expression):
        # try:
        sympy_expr = lts(latex_expression)
        sympy_expr_str = str(sympy_expr)
        self.kernel_from_expression(sympy_expr_str)
        return {"kernel": self.kernel.tolist()}
        # except Exception as e:
            # return {"error": str(e)}

    def latex_to_kernel_endpoint(self):
        data = request.json
        latex_expression = data.get('expression')
        result = self.latex_to_kernel(latex_expression)
        return jsonify(result)

    def process_step(self):
        half_kernel = self.kernel_size // 2
        rows, cols = self.number_grid.shape

        if self.step_row < rows - self.kernel_size + 1:
            if self.step_col < cols - self.kernel_size:
                roi = self.number_grid[self.step_row:self.step_row + self.kernel_size, self.step_col:self.step_col + self.kernel_size].astype(np.float32)
                self.processed_grid[self.step_row + half_kernel, self.step_col + half_kernel] = np.sum(roi * self.kernel)
                self.step_col += 1
            else:
                self.step_col = 0
                self.step_row += 1
        else:
            self.playing = False
            self.step_row = 0
            self.step_col = 0

        return jsonify({"processed_grid": self.processed_grid.tolist(), "step_row": self.step_row, "step_col": self.step_col, "playing": self.playing}), 200

    def toggle_play(self):
        self.playing = not self.playing
        return jsonify({"playing": self.playing}), 200

    def toggle_display_mode(self):
        self.display_mode = "grayscale" if self.display_mode == "numbers" else "numbers"
        return jsonify({"display_mode": self.display_mode}), 200

    def get_grid(self):
        return jsonify({
            "number_grid": self.number_grid.tolist(),
            "processed_grid": self.processed_grid.tolist(),
            "step_row": self.step_row,
            "step_col": self.step_col,
            "kernel_size": self.kernel_size,
            "display_mode": self.display_mode,
            "kernel": self.kernel.tolist()
        }), 200

    def index(self):
        return render_template('index.html')

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    visualizer_app = VisualizerApp()
    visualizer_app.run()