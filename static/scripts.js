document.addEventListener('DOMContentLoaded', () => {
    fetchGridData();
});

function fetchGridData() {
    fetch('/get_grid')
        .then(response => response.json())
        .then(data => {
            updateGridDisplay(data.number_grid, 'number-grid', data.display_mode);
            updateGridDisplay(data.processed_grid, 'processed-grid', data.display_mode);
            updateKernelOverlay(data.step_row, data.step_col, data.number_grid.length, data.kernel_size);
            updateKernelGrid(data.kernel, data.display_mode);
            updateMathGraphic(data.step_row, data.step_col, data.kernel_size, data.number_grid, data.kernel);
        });
}

function updateGridDisplay(gridData, elementId, displayMode) {
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

function updateKernelOverlay(stepRow, stepCol, gridSize, kernelSize) {
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

function updateKernelGrid(kernel, displayMode) {
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

function updateMathGraphic(stepRow, stepCol, kernelSize, numberGrid, kernel) {
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

function updateGridSize() {
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

function updateKernelSize() {
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

function applyExpression() {
    const expression = document.getElementById('expression').value;
    fetch('/apply_expression', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ expression: expression })
    }).then(fetchGridData);
}

function processStep() {
    fetch('/process_step', {
        method: 'POST'
    }).then(fetchGridData);
}

function togglePlay() {
    fetch('/toggle_play', {
        method: 'POST'
    }).then(response => response.json())
      .then(data => {
          if (data.playing) {
              autoProcess();
          }
      });
}

function autoProcess() {
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

function resetGrid() {
    fetch('/update_grid_size', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ grid_size: 10 }) // Reset to default grid size
    }).then(fetchGridData);
}

function toggleDisplayMode() {
    fetch('/toggle_display_mode', {
        method: 'POST'
    }).then(fetchGridData);
}
