import random
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

# ---------------------- Food Database ---------------------- #
class FoodDatabase:
    def __init__(self, size=100):
        categories = ['staple', 'side', 'vegetable', 'fruit', 'complement']
        allergens = ['nuts', 'gluten', 'soy', 'dairy']
        self.foods = {cat: [
            {
                'name': f"{cat}_{i}",
                'nutrition': {
                    'calories': random.randint(50, 300),
                    'protein': random.uniform(2, 20),
                    'fat': random.uniform(1, 15),
                    'sodium': random.randint(10, 400)
                },
                'allergens': set(random.choices(allergens, k=random.randint(0, 2)))
            } for i in range(size // 5)] for cat in categories
        }

    def get_random_meal(self, allowed_allergens):
        meal = {}
        for cat, items in self.foods.items():
            valid_items = [f for f in items if not (f['allergens'] - allowed_allergens)]
            if not valid_items:
                valid_items = items  # fallback
            food = random.choice(valid_items)
            portion = random.uniform(0.5, 2.0)
            meal[cat] = food
            meal[f'portion_{cat}'] = portion
        return meal

# ---------------------- Individual Representation ---------------------- #
class Individual:
    def __init__(self, db, allowed_allergens):
        self.genes = [db.get_random_meal(allowed_allergens) for _ in range(21)]
        self.fitness = 0

    def evaluate(self, goals):
        nutrients = {'calories': 0, 'protein': 0, 'fat': 0, 'sodium': 0}
        for meal in self.genes:
            for cat in ['staple', 'side', 'vegetable', 'fruit', 'complement']:
                food = meal[cat]
                portion = meal[f'portion_{cat}']
                for k in nutrients:
                    nutrients[k] += food['nutrition'][k] * portion

        score = 0
        for k in nutrients:
            diff = abs(goals[k] - nutrients[k])
            score -= diff / goals[k]  # normalized difference

        diversity_score = len(set(f['name'] for m in self.genes for f in m.values() if isinstance(f, dict)))
        score += diversity_score * 0.01

        self.fitness = score
        return score

    def mutate(self, db, allowed_allergens, rate=0.05):
        for i in range(len(self.genes)):
            if random.random() < rate:
                self.genes[i] = db.get_random_meal(allowed_allergens)

    def crossover(self, other):
        child = Individual.__new__(Individual)
        child.genes = [random.choice([m1, m2]) for m1, m2 in zip(self.genes, other.genes)]
        return child

# ---------------------- Genetic Algorithm ---------------------- #
def genetic_algorithm(db, nutrition_goals, allowed_allergens, population_size=100, generations=100, elitism=0.1, early_stop=10):
    population = [Individual(db, allowed_allergens) for _ in range(population_size)]
    for ind in population:
        ind.evaluate(nutrition_goals)
    population.sort(key=lambda x: -x.fitness)

    best_fitness = population[0].fitness
    best_history = [best_fitness]
    avg_history = [sum(ind.fitness for ind in population) / population_size]
    stagnation = 0

    for gen in range(generations):
        next_gen = population[:int(elitism * population_size)]
        while len(next_gen) < population_size:
            parents = random.sample(population[:50], 2)
            child = parents[0].crossover(parents[1])
            child.mutate(db, allowed_allergens)
            child.evaluate(nutrition_goals)
            next_gen.append(child)

        population = sorted(next_gen, key=lambda x: -x.fitness)
        best_fitness = population[0].fitness
        best_history.append(best_fitness)
        avg_history.append(sum(ind.fitness for ind in population) / population_size)

        if abs(best_history[-1] - best_history[-2]) < 1e-3:
            stagnation += 1
            if stagnation >= early_stop:
                break
        else:
            stagnation = 0

    return population[0], best_history, avg_history

# ---------------------- GUI ---------------------- #
class DietPlannerGUI:
    def __init__(self, root):
        self.db = FoodDatabase(size=100)
        self.goals = {'calories': 14000, 'protein': 500, 'fat': 300, 'sodium': 7000}
        self.allowed_allergens = set()

        self.root = root
        self.root.title("Weekly Diet Planner - Genetic Algorithm + GUI")

        # Input frame
        input_frame = ttk.LabelFrame(root, text="User Settings")
        input_frame.pack(fill='x', padx=10, pady=5)

        self.entries = {}
        for i, k in enumerate(self.goals):
            ttk.Label(input_frame, text=k.capitalize()).grid(row=0, column=i)
            e = ttk.Entry(input_frame, width=10)
            e.insert(0, str(self.goals[k]))
            e.grid(row=1, column=i)
            self.entries[k] = e

        self.allergen_var = tk.StringVar(value='nuts,soy')
        ttk.Label(input_frame, text="Allowed Allergens").grid(row=0, column=len(self.goals))
        ttk.Entry(input_frame, textvariable=self.allergen_var, width=20).grid(row=1, column=len(self.goals))

        ttk.Button(input_frame, text="Run Optimizer", command=self.run_thread).grid(row=1, column=len(self.goals)+1)

        # Plan display
        self.plan_frame = ttk.LabelFrame(root, text="Weekly Meal Plan")
        self.plan_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.text_display = tk.Text(self.plan_frame, wrap='word', font=('Courier', 9))
        self.text_display.pack(fill='both', expand=True)

        # Plot area
        plot_frame = ttk.LabelFrame(root, text="Fitness History")
        plot_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.fig, self.ax = plt.subplots(figsize=(5, 2))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def run_thread(self):
        threading.Thread(target=self.run_optimizer, daemon=True).start()

    def run_optimizer(self):
        try:
            for k in self.goals:
                self.goals[k] = float(self.entries[k].get())
            self.allowed_allergens = set(self.allergen_var.get().split(','))
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric goals.")
            return

        self.text_display.delete(1.0, tk.END)
        self.ax.clear()
        self.canvas.draw()

        sol, best_hist, avg_hist = genetic_algorithm(
            self.db, self.goals, self.allowed_allergens,
            population_size=100, generations=150, early_stop=15, elitism=0.1)

        self.display_solution(sol)
        self.plot_history(best_hist, avg_hist)

    def display_solution(self, solution):
        output = []
        for day in range(7):
            output.append(f"\nDAY {day+1}")
            output.append("-" * 30)
            for m in range(3):
                idx = day * 3 + m
                meal = solution.genes[idx]
                output.append(f"  Meal {m+1}:")
                for cat in ['staple', 'side', 'vegetable', 'fruit', 'complement']:
                    f = meal[cat]
                    p = meal[f'portion_{cat}']
                    output.append(f"    {cat.capitalize():<12}: {f['name']} x{p:.1f}")
        self.text_display.insert(tk.END, '\n'.join(output))

    def plot_history(self, best_hist, avg_hist):
        self.ax.plot(best_hist, label='Best', color='green')
        self.ax.plot(avg_hist, label='Average', color='orange')
        self.ax.set_title("Fitness over Generations")
        self.ax.set_xlabel("Generation")
        self.ax.set_ylabel("Fitness")
        self.ax.legend()
        self.canvas.draw()

if __name__ == '__main__':
    root = tk.Tk()
    app = DietPlannerGUI(root)
    root.mainloop()
