#!/bin/bash
#SBATCH --job-name=get-organelle
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=16
#SBATCH --ntasks=1
#SBATCH --mem=28g
#SBATCH --out=afgi-mitogenomes/logs/get-organelle_%j.out


module load singularity/4.1.0-nohost

singularity exec docker://quay.io/biocontainers/getorganelle:1.7.7.1--pyhdfd78af_0 \
    get_organelle_config.py -a animal_mt \
    --config-dir /software/projects/pawsey1132/atims/.GetOrganelle

singularity exec docker://quay.io/biocontainers/getorganelle:1.7.7.1--pyhdfd78af_0 \
    get_organelle_from_reads.py \
        -1 reads/trim/617773_FISH_BRF_23NK3CLT4_TCATCCGAAA-AGTGGGTTGA_S375_R1_001.trim_pe.fastq \
        -2 reads/trim/617773_FISH_BRF_23NK3CLT4_TCATCCGAAA-AGTGGGTTGA_S375_R2_001.trim_pe.fastq \
        -R 10 -k 21,45,65,85,105 -t 16 \
        --config-dir /software/projects/pawsey1132/atims/.GetOrganelle \
        -F animal_mt -o test_out --continue