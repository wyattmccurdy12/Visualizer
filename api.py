from flask import Flask, request, jsonify, render_template
import numpy as np

app = Flask(__name__)

# Initialize global variables
grid_size = 10  # Default grid size set to 10
number_grid = np.zeros((grid_size, grid_size))
number_grid[:, grid_size // 2] = 1  # Vertical stripe of white on a black background
processed_grid = np.zeros_like(number_grid, dtype=np.float32)
kernel_size = 3
kernel = np.ones((kernel_size, kernel_size))  # Default kernel
step_row = 0
step_col = 0
playing = False
display_mode = "numbers"  # Default display mode

@app.route('/update_grid_size', methods=['POST'])
def update_grid_size():
    """
    Updates the grid size based on the user's input.

    This endpoint expects a JSON payload with a 'grid_size' field.
    It updates the global grid_size, number_grid, and processed_grid variables.

    Returns:
        JSON response with a success message and the updated grid size, or an error message.
    """
    global grid_size, number_grid, processed_grid
    data = request.json
    new_grid_size = data.get('grid_size', grid_size)
    if 0 < new_grid_size <= 20:  # Limit grid size to a maximum of 20
        grid_size = new_grid_size
        number_grid = np.zeros((grid_size, grid_size))
        number_grid[:, grid_size // 2] = 1  # Vertical stripe of white on a black background
        processed_grid = np.zeros_like(number_grid, dtype=np.float32)
        return jsonify({"message": "Grid size updated", "grid_size": grid_size}), 200
    else:
        return jsonify({"error": "Grid size must be a positive integer and less than or equal to 20"}), 400

@app.route('/update_kernel_size', methods=['POST'])
def update_kernel_size():
    """
    Updates the kernel size based on the user's input.

    This endpoint expects a JSON payload with a 'kernel_size' field.
    It updates the global kernel_size and kernel variables.

    Returns:
        JSON response with a success message and the updated kernel size, or an error message.
    """
    global kernel_size, kernel
    data = request.json
    new_kernel_size = data.get('kernel_size', kernel_size)
    if new_kernel_size > 0:
        kernel_size = new_kernel_size
        kernel = np.ones((kernel_size, kernel_size))  # Reset kernel to ones
        return jsonify({"message": "Kernel size updated", "kernel_size": kernel_size}), 200
    else:
        return jsonify({"error": "Kernel size must be a positive integer"}), 400

@app.route('/apply_expression', methods=['POST'])
def apply_expression():
    """
    Applies a mathematical expression to generate a new kernel.

    This endpoint expects a JSON payload with an 'expression' field.
    It evaluates the expression to create a new kernel.

    Returns:
        JSON response with a success message and the updated kernel, or an error message.
    """
    global kernel
    data = request.json
    expression_str = data.get('expression')
    try:
        if "lambda" not in expression_str:
            expression_str = "lambda x, y: " + expression_str
        kernel_func = eval(expression_str)
        kernel = np.fromfunction(kernel_func, (kernel_size, kernel_size))
        return jsonify({"message": "Kernel updated from expression", "kernel": kernel.tolist()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
def translate_expression(expression):
    """
    This is a helper function. It takes in a markup string representing a mathematical expression and 
    turns it into a python expression that can be interpreted as part of a python lambda function.
    
    Args:
        expression (str): The markup string representing the mathematical expression.
        
    Returns:
        str: The translated Python expression.
    """
    # Example translation rules (you can expand this as needed)
    translation_rules = {
        '^': '**',  # Replace caret with double asterisk for exponentiation
        'e^': 'exp'
    }
    
    # Apply translation rules
    for key, value in translation_rules.items():
        expression = expression.replace(key, value)
    
    return expression


@app.route('/process_step', methods=['POST'])
def process_step():
    """
    Processes a single step of the kernel convolution on the number grid.

    This endpoint updates the processed_grid based on the current kernel position.

    Returns:
        JSON response with the updated processed grid, step row, step column, and playing status.
    """
    global step_row, step_col, playing, processed_grid
    half_kernel = kernel_size // 2
    rows, cols = number_grid.shape

    if step_row < rows - kernel_size + 1:
        if step_col < cols - kernel_size:
            roi = number_grid[step_row:step_row + kernel_size, step_col:step_col + kernel_size].astype(np.float32)
            processed_grid[step_row + half_kernel, step_col + half_kernel] = np.sum(roi * kernel)
            step_col += 1
        else:
            step_col = 0
            step_row += 1
    else:
        playing = False
        step_row = 0
        step_col = 0

    return jsonify({"processed_grid": processed_grid.tolist(), "step_row": step_row, "step_col": step_col, "playing": playing}), 200

@app.route('/toggle_play', methods=['POST'])
def toggle_play():
    """
    Toggles the playing status of the kernel convolution process.

    This endpoint switches the playing status between True and False.

    Returns:
        JSON response with the updated playing status.
    """
    global playing
    playing = not playing
    return jsonify({"playing": playing}), 200

@app.route('/toggle_display_mode', methods=['POST'])
def toggle_display_mode():
    """
    Toggles the display mode between 'numbers' and 'grayscale'.

    This endpoint switches the display mode for the number grid.

    Returns:
        JSON response with the updated display mode.
    """
    global display_mode
    display_mode = "grayscale" if display_mode == "numbers" else "numbers"
    return jsonify({"display_mode": display_mode}), 200

@app.route('/get_grid', methods=['GET'])
def get_grid():
    """
    Retrieves the current state of the number grid and processed grid.

    This endpoint returns the number grid, processed grid, kernel size, display mode, and kernel.

    Returns:
        JSON response with the current grid data and settings.
    """
    return jsonify({
        "number_grid": number_grid.tolist(),
        "processed_grid": processed_grid.tolist(),
        "step_row": step_row,
        "step_col": step_col,
        "kernel_size": kernel_size,
        "display_mode": display_mode,
        "kernel": kernel.tolist()
    }), 200

@app.route('/')
def index():
    """
    Renders the main HTML page.

    This endpoint serves the index.html file.

    Returns:
        Rendered HTML template for the main page.
    """
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)