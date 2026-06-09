import glob
import json
import pandas as pd

files = glob.glob("results/slurm_task_*.json")

all_results = []

for f in files:
    with open(f, "r") as infile:
        all_results.extend(json.load(infile))

df = pd.DataFrame(all_results)

df.to_csv("results/combined_power.csv", index=False)

print(df.head())
