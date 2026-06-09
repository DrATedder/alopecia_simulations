import numpy as np
import pandas as pd
import json
import os
from statsmodels.formula.api import mixedlm

# =====================================================
# LOAD SLURM TASK ID
# =====================================================

TASK_ID = int(os.environ.get("SLURM_ARRAY_TASK_ID", 0))

# =====================================================
# PARAMETERS
# =====================================================

week8 = np.array([69, 51, 82, 60, 39])
week12 = np.array([81, 89, 82, 100, 73])
progression = week12 - week8

mean_w8 = week8.mean()
sd_w8 = week8.std(ddof=1)

mean_prog = progression.mean()
sd_prog = progression.std(ddof=1)

ALPHA = 0.05
N_SIM = 2000

SAMPLE_SIZES = list(range(4, 101))
EFFECTS = [0.05, 0.20, 0.50, 0.70, 1.00]

PENETRANCE = 0.83

rng = np.random.default_rng(1234 + TASK_ID)

# =====================================================
# SPLIT WORK ACROSS TASKS
# =====================================================

grid = [
    (n, e)
    for n in SAMPLE_SIZES
    for e in EFFECTS
]

# each SLURM task gets every k-th item
NUM_TASKS = int(os.environ.get("SLURM_ARRAY_TASK_COUNT", 1))

my_grid = grid[TASK_ID::NUM_TASKS]

# =====================================================
# BIOLOGY
# =====================================================

def generate_animal():

    if rng.random() > PENETRANCE:
        return np.array([0.0, 0.0])

    w8 = np.clip(
        rng.normal(mean_w8, sd_w8),
        0, 100
    )

    prog = max(
        0,
        rng.normal(mean_prog, sd_prog)
    )

    w12 = np.clip(w8 + prog, 0, 100)

    return np.array([w8, w12])

# =====================================================
# SINGLE EXPERIMENT
# =====================================================

def simulate_experiment(n, effect):

    rows = []
    animal = 0

    for _ in range(n):
        v = generate_animal()
        rows.append([animal, "Control", "W8", v[0]])
        rows.append([animal, "Control", "W12", v[1]])
        animal += 1

    for _ in range(n):
        v = generate_animal()
        v = v * (1 - effect)
        rows.append([animal, "Treatment", "W8", v[0]])
        rows.append([animal, "Treatment", "W12", v[1]])
        animal += 1

    df = pd.DataFrame(rows, columns=["animal","group","time","hair_loss"])

    try:
        model = mixedlm(
            "hair_loss ~ group + time",
            data=df,
            groups=df["animal"]
        )

        fit = model.fit(reml=False, disp=False)

        return fit.pvalues["group[T.Treatment]"] < ALPHA

    except:
        return False

# =====================================================
# RUN TASK
# =====================================================

results = []

for n, e in my_grid:

    hits = 0

    for _ in range(N_SIM):

        if simulate_experiment(n, e):
            hits += 1

    power = hits / N_SIM

    results.append({
        "n": n,
        "effect": e,
        "power": power
    })

# =====================================================
# SAVE OUTPUT PER TASK
# =====================================================

out_file = f"results/slurm_task_{TASK_ID}.json"

with open(out_file, "w") as f:
    json.dump(results, f)

print(f"Saved {out_file}")
