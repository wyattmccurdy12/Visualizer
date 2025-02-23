document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded and parsed");
    fetchGridData();
    initializeDesmosCalculator();
});

let calculator; // Declare the calculator variable globally

/**
 * Fetches the grid data from the server and updates the display.
 *
 * This function makes a GET request to the '/get_grid' endpoint on the server.
 * Upon receiving a successful response, it parses the JSON data and calls
 * other functions to update the number grid, processed grid, kernel overlay,
 * kernel grid, and math graphic on the webpage.
 */
function fetchGridData() {
    fetch('/get_grid')
        .then(response => response.json())
        .then(data => {
            console.log("Grid data fetched", data);
            updateGridDisplay(data.number_grid, 'number-grid', data.display_mode);
            updateGridDisplay(data.processed_grid, 'processed-grid', data.display_mode);
            updateKernelOverlay(data.step_row, data.step_col, data.number_grid.length, data.kernel_size);
            updateKernelGrid(data.kernel, data.display_mode);
            updateMathGraphic(data.step_row, data.step_col, data.kernel_size, data.number_grid, data.kernel);
        });
}

/**
 * Updates the display of a grid on the webpage.
 *
 * @param {number[][]} gridData - A 2D array representing the grid data.
 * @param {string} elementId - The ID of the HTML element where the grid will be displayed.
 * @param {string} displayMode - The display mode ('numbers' or 'grayscale').
 *                              If 'numbers', the cell values are displayed as text.
 *                              If 'grayscale', the cell values are displayed as grayscale intensities.
 */
function updateGridDisplay(gridData, elementId, displayMode) {
    console.log("Updating grid display", elementId, displayMode);
    const gridElement = document.getElementById(elementId);
    gridElement.innerHTML = '';
    const gridSize = gridData.length;
    gridElement.style.gridTemplateColumns = `repeat(${gridSize}, 1fr)`;
    gridElement.style.gridTemplateRows = `repeat(${gridSize}, 1fr)`;

    gridData.forEach(row => {
        row.forEach(cell => {
            const cellElement = document.createElement('div');
            cellElement.className = 'cell';
            if (displayMode === 'numbers') {
                cellElement.textContent = cell.toFixed(2);
            } else {
                const intensity = Math.round(cell * 255);
                cellElement.style.backgroundColor = `rgb(${intensity}, ${intensity}, ${intensity})`;
            }
            gridElement.appendChild(cellElement);
        });
    });
}

/**
 * Updates the kernel overlay on the number grid.
 *
 * This function adds a blue border to the cells in the number grid that
 * correspond to the current kernel position.
 *
 * @param {number} stepRow - The current row index of the kernel.
 * @param {number} stepCol - The current column index of the kernel.
 * @param {number} gridSize - The size of the number grid.
 * @param {number} kernelSize - The size of the kernel.
 */
function updateKernelOverlay(stepRow, stepCol, gridSize, kernelSize) {
    console.log("Updating kernel overlay", stepRow, stepCol, gridSize, kernelSize);
    const gridElement = document.getElementById('number-grid');
    const halfKernel = Math.floor(kernelSize / 2);

    for (let i = 0; i < kernelSize; i++) {
        for (let j = 0; j < kernelSize; j++) {
            const cellIndex = (stepRow + i) * gridSize + (stepCol + j);
            const cellElement = gridElement.children[cellIndex];
            if (cellElement) {
                cellElement.style.border = '2px solid blue';
            }
        }
    }
}

/**
 * Updates the display of the kernel grid.
 *
 * @param {number[][]} kernel - A 2D array representing the kernel values.
 * @param {string} displayMode - The display mode ('numbers' or 'grayscale').
 */
function updateKernelGrid(kernel, displayMode) {
    console.log("Updating kernel grid", displayMode);
    const kernelGridElement = document.getElementById('kernel-grid');
    kernelGridElement.innerHTML = '';
    kernel.forEach(row => {
        row.forEach(cell => {
            const cellElement = document.createElement('div');
            cellElement.className = 'cell';
            if (displayMode === 'numbers') {
                cellElement.textContent = cell.toFixed(2);
            } else {
                const intensity = Math.round(cell * 255);
                cellElement.style.backgroundColor = `rgb(${intensity}, ${intensity}, ${intensity})`;
            }
            kernelGridElement.appendChild(cellElement);
        });
    });
}

/**
 * Updates the math graphic display with the current equation.
 *
 * @param {number} stepRow - The current row index of the kernel.
 * @param {number} stepCol - The current column index of the kernel.
 * @param {number} kernelSize - The size of the kernel.
 * @param {number[][]} numberGrid - The number grid data.
 * @param {number[][]} kernel - The kernel data.
 */
function updateMathGraphic(stepRow, stepCol, kernelSize, numberGrid, kernel) {
    console.log("Updating math graphic", stepRow, stepCol, kernelSize);
    const mathGraphicElement = document.getElementById('math-graphic');
    let equation = '';
    for (let i = 0; i < kernelSize; i++) {
        for (let j = 0; j < kernelSize; j++) {
            const number = numberGrid[stepRow + i][stepCol + j].toFixed(2);
            const kernelValue = kernel[i][j].toFixed(2);
            equation += `${number} x ${kernelValue}`;
            if (i !== kernelSize - 1 || j !== kernelSize - 1) {
                equation += ' + ';
            }
        }
    }
    mathGraphicElement.innerHTML = `Equation: ${equation}`;
}

/**
 * Updates the grid size on the server and refreshes the grid data.
 */
function updateGridSize() {
    console.log("Updating grid size");
    const gridSize = document.getElementById('grid-size').value;
    if (gridSize > 0 && gridSize <= 20) {
        fetch('/update_grid_size', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ grid_size: parseInt(gridSize) })
        }).then(fetchGridData);
    } else {
        alert("Grid size must be a positive integer and less than or equal to 20");
    }
}

/**
 * Updates the kernel size on the server and refreshes the grid data.
 */
function updateKernelSize() {
    console.log("Updating kernel size");
    const kernelSize = document.getElementById('kernel-size').value;
    if (kernelSize > 0) {
        fetch('/update_kernel_size', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ kernel_size: parseInt(kernelSize) })
        }).then(fetchGridData);
    } else {
        alert("Kernel size must be a positive integer");
    }
}

/**
 * Initializes the Desmos calculator for the equation editor.
 */
function initializeDesmosCalculator() {
    const elt = document.getElementById('calculator');
    calculator = Desmos.Calculator(elt, {
        graphpaper: false
    });

}

/**
 * Logs the current state of the Desmos calculator.
 */
function logCalculatorState() {
    const state = calculator.getState();
    console.log("Calculator state:", state);

    // Log the latex expression state -> expressions[0] -> latex
    if (state.expressions && state.expressions.list && state.expressions.list.length > 0) {
        console.log("LaTeX expression:", state.expressions.list[0].latex);
    } else {
        console.log("No expressions found.");
    }
}

/**
 * Sends the LaTeX expression to the API.
 */
function sendLatexExpression() {
    const state = calculator.getState();
    if (state.expressions && state.expressions.list && state.expressions.list.length > 0) {
        const latexExpression = state.expressions.list[0].latex;
        console.log("Sending LaTeX expression to API:", latexExpression);
        fetch('/translate_expression', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ expression: latexExpression })
        }).then(response => response.json())
          .then(data => {
              console.log("Response from API:", data);
          });
    } else {
        console.log("No expressions found to send.");
    }
}

/**
 * Processes a single step on the server and refreshes the grid data.
 */
function processStep() {
    console.log("Processing step");
    fetch('/process_step', {
        method: 'POST'
    }).then(fetchGridData);
}

/**
 * Starts or resumes the automatic processing of steps on the server.
 */
function startPlay() {
    console.log("Starting play");
    fetch('/toggle_play', {
        method: 'POST'
    }).then(response => response.json())
      .then(data => {
          if (data.playing) {
              autoProcess();
          }
      });
}

/**
 * Pauses the automatic processing of steps on the server.
 */
function pausePlay() {
    console.log("Pausing play");
    fetch('/toggle_play', {
        method: 'POST'
    }).then(response => response.json());
}

/**
 * Automatically processes steps on the server at a set interval.
 */
function autoProcess() {
    console.log("Auto processing");
    fetch('/process_step', {
        method: 'POST'
    }).then(response => response.json())
      .then(data => {
          if (data.playing) {
              setTimeout(autoProcess, 100); // Adjust delay as needed
          }
          fetchGridData();
      });
}

/**
 * Resets the grid to its default state.
 */
function resetGrid() {
    console.log("Resetting grid");
    fetch('/update_grid_size', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ grid_size: 10 }) // Reset to default grid size
    }).then(() => {
        fetch('/get_grid')
            .then(response => response.json())
            .then(data => {
                updateGridDisplay(data.number_grid, 'number-grid', data.display_mode);
                updateGridDisplay(data.processed_grid, 'processed-grid', data.display_mode);
                updateKernelOverlay(0, 0, data.number_grid.length, data.kernel_size); // Reset kernel position
                updateKernelGrid(data.kernel, data.display_mode);
                updateMathGraphic(0, 0, data.kernel_size, data.number_grid, data.kernel); // Reset math graphic
            });
    });
}

/**
 * Toggles the display mode between numbers and grayscale.
 */
function toggleDisplayMode() {
    console.log("Toggling display mode");
    fetch('/toggle_display_mode', {
        method: 'POST'
    }).then(fetchGridData);
}