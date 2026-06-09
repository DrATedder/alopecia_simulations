import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results/combined_power.csv")

for effect in sorted(df["effect"].unique()):

    sub = df[df["effect"] == effect]
    agg = sub.groupby("n")["power"].mean().reset_index()

    plt.plot(agg["n"], agg["power"], label=f"{effect:.0%}")

plt.axhline(0.8, linestyle="--")
plt.axhline(0.9, linestyle=":")

plt.xlabel("N per group")
plt.ylabel("Power")
plt.legend()
plt.title("SLURM-Distributed Power Simulation")

plt.show()
