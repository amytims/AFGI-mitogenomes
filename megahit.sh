#!/bin/bash
#SBATCH --job-name=get-organelle
#SBATCH --time=6:00:00
#SBATCH --cpus-per-task=48
#SBATCH --ntasks=1
#SBATCH --mem=72g
#SBATCH --output=logs/fastp.%j.out

module load singularity/4.1.0-nohost

RAW_READS_DIR="reads/raw/"
TRIM_DIR="reads/trim/"

mkdir -p ${TRIM_DIR}

# testing - only look at first R1 read file
# in array jobs, use id="${SLURM_ARRAY_TASK_ID}"
RAW_R1=$(ls ${RAW_READS_DIR}/*_R1_* | awk -v id="1" 'NR==id {print $1}')
RAW_R2=$(echo ${RAW_R1} | sed -r 's/_R1/_R2/g')

echo $RAW_R1
echo $RAW_R2

singularity exec docker://quay.io/biocontainers/fastp:1.4.0--h43da1c4_0 \
	fastp \
	--in1 "$RAW_R1" \
	--in2 "$RAW_R2" \
	--out1 "${TRIM_DIR}/$(basename --suffix=.fastq.gz $RAW_R1).fastp.fastq.gz" \
	--out2 "${TRIM_DIR}/$(basename --suffix=.fastq.gz $RAW_R2).fastp.fastq.gz" \
	--trim_poly_g \
	--dedup \
	--thread 48 \
	--html "${TRIM_DIR}/$(basename --suffix=.fastq.gz $RAW_R1)_fastp_report.html" \
	--json "${TRIM_DIR}/$(basename --suffix=.fastq.gz $RAW_R1)_fastp_report.json"

singularity exec docker://quay.io/biocontainers/megahit:1.2.9--haf24da9_8 \
	megahit \
	-1 "${TRIM_DIR}/$(basename --suffix=.fastq.gz $RAW_R1).fastp.fastq.gz" \
	-2 "${TRIM_DIR}/$(basename --suffix=.fastq.gz $RAW_R2).fastp.fastq.gz" \
	--presets meta-sensitive \
	--min-contig-len 500 \
	-t 48 \
	-o "megahit/$(basename --suffix=.fastq.gz $RAW_R1)_megahit"
