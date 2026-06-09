#!/bin/bash
#SBATCH --job-name=alopecia_power
#SBATCH --account=
#SBATCH --partition=compute
#SBATCH --output=logs/%A_%a.out
#SBATCH --error=logs/%A_%a.err
#SBATCH --array=0-20
#SBATCH --cpus-per-task=1
#SBATCH --time=05:00:00


module load bioconda

conda activate inSilicoSeq

mkdir -p results logs

python /storage/atedder/alo_sim_batch/batch_simulate.py
