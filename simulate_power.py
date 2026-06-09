import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from statsmodels.formula.api import mixedlm

# =====================================================
# PILOT DATA
# =====================================================

week8 = np.array([69, 51, 82, 60, 39])
week12 = np.array([81, 89, 82, 100, 73])

progression = week12 - week8

# =====================================================
# FIT BIOLOGY
# =====================================================

mean_w8 = week8.mean()
sd_w8 = week8.std(ddof=1)

mean_prog = progression.mean()
sd_prog = progression.std(ddof=1)

# =====================================================
# GLOBAL SETTINGS
# =====================================================

ALPHA = 0.05
N_SIM = 2000

SAMPLE_SIZES = range(4, 101)

EFFECTS = [0.05, 0.20, 0.50, 0.70, 1.00]
REFERENCE_EFFECT = 0.50

penetrance_levels = [0.70, 0.83, 0.90, 1.00]

rng = np.random.default_rng(12345)

# =====================================================
# ANIMAL GENERATOR (PROGRESSION MODEL)
# =====================================================

def generate_animal(penetrance):

    # non-penetrant
    if rng.random() > penetrance:
        return np.array([0.0, 0.0])

    # week 8 severity
    w8 = rng.normal(mean_w8, sd_w8)
    w8 = np.clip(w8, 0, 100)

    # progression (disease worsening)
    prog = rng.normal(mean_prog, sd_prog)
    prog = max(0, prog)

    w12 = np.clip(w8 + prog, 0, 100)

    return np.array([w8, w12])

# =====================================================
# SIMULATE EXPERIMENT
# =====================================================

def simulate_experiment(n_per_group, treatment_effect, penetrance):

    rows = []
    animal = 0

    # ---------------- control ----------------
    for _ in range(n_per_group):
        vals = generate_animal(penetrance)

        rows.append([animal, "Control", "W8", vals[0]])
        rows.append([animal, "Control", "W12", vals[1]])
        animal += 1

    # ---------------- treatment ----------------
    for _ in range(n_per_group):
        vals = generate_animal(penetrance)

        # treatment acts on severity
        vals = vals * (1 - treatment_effect)

        rows.append([animal, "Treatment", "W8", vals[0]])
        rows.append([animal, "Treatment", "W12", vals[1]])
        animal += 1

    df = pd.DataFrame(rows, columns=["animal","group","time","hair_loss"])

    try:
        model = mixedlm(
            "hair_loss ~ group + time",
            data=df,
            groups=df["animal"]
        )

        fit = model.fit(reml=False, disp=False)

        p = fit.pvalues["group[T.Treatment]"]

        return p < ALPHA

    except:
        return False

# =====================================================
# POWER ESTIMATION
# =====================================================

def estimate_power(n, effect, penetrance):

    hits = 0

    for _ in range(N_SIM):
        if simulate_experiment(n, effect, penetrance):
            hits += 1

    return hits / N_SIM

# =====================================================
# STORE RESULTS
# =====================================================

power_curve_results = []
summary_results = []

# =====================================================
# FIGURE 1–3: POWER CURVES + SAMPLE SIZE TABLE
# =====================================================

for effect in EFFECTS:

    print("\n" + "="*60)
    print(f"Effect size = {effect:.0%}")
    print("="*60)

    n80 = None
    n90 = None

    for n in SAMPLE_SIZES:

        power = estimate_power(n, effect, 0.83)

        power_curve_results.append({
            "effect": effect,
            "n": n,
            "power": power
        })

        print(f"N={n:3d}  power={power:.3f}")

        if n80 is None and power >= 0.80:
            n80 = n

        if n90 is None and power >= 0.90:
            n90 = n
            break

    summary_results.append([effect, n80, n90])

summary = pd.DataFrame(
    summary_results,
    columns=["Effect","N_80","N_90"]
)

power_df = pd.DataFrame(power_curve_results)

# =====================================================
# FIGURE 1: POWER CURVES
# =====================================================

plt.figure(figsize=(8,6))

for effect in EFFECTS:
    subset = power_df[power_df["effect"] == effect]

    plt.plot(subset["n"], subset["power"], label=f"{effect:.0%}")

plt.axhline(0.80, linestyle="--")
plt.axhline(0.90, linestyle=":")

plt.xlabel("Animals per group")
plt.ylabel("Power")
plt.title("Power Curves (Progression Model)")
plt.legend()

plt.tight_layout()
plt.savefig("figure1_power_curves.png", dpi=300)
plt.show()

# =====================================================
# FIGURE 2: N FOR 80% POWER
# =====================================================

plt.figure(figsize=(7,5))

plt.bar(summary["Effect"].astype(str), summary["N_80"])
plt.xlabel("Treatment Effect")
plt.ylabel("N per group")
plt.title("Sample Size for 80% Power")

plt.tight_layout()
plt.savefig("figure2_n80.png", dpi=300)
plt.show()

# =====================================================
# FIGURE 3: N FOR 90% POWER
# =====================================================

plt.figure(figsize=(7,5))

plt.bar(summary["Effect"].astype(str), summary["N_90"])
plt.xlabel("Treatment Effect")
plt.ylabel("N per group")
plt.title("Sample Size for 90% Power")

plt.tight_layout()
plt.savefig("figure3_n90.png", dpi=300)
plt.show()

# =====================================================
# FIGURE 4: SIMULATED TRAJECTORIES
# =====================================================

plt.figure(figsize=(8,6))

for _ in range(50):
    vals = generate_animal(0.83)
    plt.plot([8,12], vals, alpha=0.3)

plt.xlabel("Week")
plt.ylabel("Hair loss (%)")
plt.title("Simulated Disease Trajectories")

plt.tight_layout()
plt.savefig("figure4_trajectories.png", dpi=300)
plt.show()

# =====================================================
# FIGURE 5: PENETRANCE SENSITIVITY
# =====================================================

penetrance_results = []

for p in penetrance_levels:

    n80 = None
    n90 = None

    for n in SAMPLE_SIZES:

        power = estimate_power(n, REFERENCE_EFFECT, p)

        if n80 is None and power >= 0.80:
            n80 = n

        if n90 is None and power >= 0.90:
            n90 = n
            break

    penetrance_results.append([p, n80, n90])

penetrance_df = pd.DataFrame(
    penetrance_results,
    columns=["Penetrance","N_80","N_90"]
)

plt.figure(figsize=(7,5))

plt.plot(penetrance_df["Penetrance"], penetrance_df["N_80"], marker="o", label="80%")
plt.plot(penetrance_df["Penetrance"], penetrance_df["N_90"], marker="o", label="90%")

plt.xlabel("Penetrance")
plt.ylabel("N per group")
plt.title("Penetrance Sensitivity (50% effect)")
plt.legend()

plt.tight_layout()
plt.savefig("figure5_penetrance_sensitivity.png", dpi=300)
plt.show()

# =====================================================
# FINAL OUTPUT
# =====================================================

print("\nSUMMARY TABLE")
print(summary)

print("\nPENETRANCE SENSITIVITY")
print(penetrance_df)
