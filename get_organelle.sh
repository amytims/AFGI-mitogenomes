#!/bin/bash



module load singularity/4.1.0-nohost

singularity exec docker://quay.io/biocontainers/getorganelle:1.7.7.1--pyhdfd78af_0 \
    get_organelle_from_reads.py \
        -1 forward.fq \
        -2 reverse.fq \
        -R 10 -k 21,45,65,85,105 \
        -F animal_mt -o animal_mt_out 