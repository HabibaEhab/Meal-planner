#Smart Weekly Diet Planner (Genetic Algorithm + GUI)

An AI-powered meal planning application that uses Genetic Algorithms to generate optimized weekly diet plans. The solution considers nutritional goals, allergen restrictions, and food diversity,all presented in a user-friendly GUI built with Tkinter and Matplotlib.

---

## Features

- **Genetic Algorithm Optimization**: Evolves 7-day meal plans (21 meals) to meet user-defined nutritional targets.
- **Fuzzy Constraint Handling**: Supports soft constraints like allergen avoidance and meal diversity.
- **Live Fitness Graphs**: Visualizes the optimization process with best and average fitness scores over generations.
- **Interactive GUI**: Built with Tkinter for inputting goals, allergens, and displaying meal plans and plots.

---

##  How It Works

1. **Generate Meals**: A synthetic database of 100+ foods across categories (`staple`, `side`, `vegetable`, `fruit`, `complement`) is created.
2. **Initialize Population**: Each individual in the population is a candidate 7-day diet plan (21 meals).
3. **Evaluate Fitness**: Each plan is scored based on:
   - Deviation from calorie, protein, fat, and sodium goals
   - Diversity of food items
4. **Genetic Operations**:
   - **Selection**: Top individuals survive.
   - **Crossover**: Children inherit meals from two parents.
   - **Mutation**: Meals are randomly replaced to maintain diversity.
5. **Early Stopping**: If the fitness stagnates, the algorithm terminates early.
