# Transportation Problem Solver

A Streamlit web application for solving transportation problems using the Least Cost Cell Method and Modified Distribution (MODI) Method for minimization.

## Overview

This application provides an interactive interface to solve classical transportation problems in linear programming using two powerful algorithms:

- **Least Cost Cell Method** - for finding initial basic feasible solution
- **Modified Distribution Method (MODI)** - for optimization and optimality verification

## Features

- 📊 Interactive data input for supply and demand
- 🧮 Cost matrix visualization and editing
- 🔍 Step-by-step solution visualization
- 📈 Optimal transportation plan calculation
- 💰 Total cost computation
- 🎯 Real-time problem solving

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Steps

1. Clone or download the project files
2. Install required dependencies:

```bash
pip install streamlit pandas numpy
```

3. Run the application:

```bash
streamlit run app.py
```

## Usage Guide

### Set Problem Dimensions

- Enter the number of suppliers (sources)
- Enter the number of consumers (destinations)

### Input Data

- Fill in the supply values for each supplier
- Fill in the demand values for each consumer
- Enter the transportation cost matrix

### Solve the Problem

- Click the "Solve Transportation Problem" button
- View the step-by-step solution process
- Analyze the optimal transportation plan

### Review Results

- Initial basic feasible solution using Least Cost Method
- Optimal solution using MODI method
- Total transportation cost calculation
- Allocation matrix visualization

## Algorithm Details

### Least Cost Cell Method

- Starts with the cell having the minimum transportation cost
- Allocates as much as possible to that cell
- Eliminates satisfied rows or columns
- Repeats until all supply and demand are satisfied

### Modified Distribution Method (MODI)

- Tests the optimality of the current solution
- Calculates opportunity costs for unoccupied cells
- Identifies improving cells and creates closed loops
- Reallocates quantities to reduce total cost
