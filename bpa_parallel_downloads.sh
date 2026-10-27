#!/bin/bash
#SBATCH --account=pawsey1132
#SBATCH --partition=work
#SBATCH --job-name=download_files
#SBATCH --cpus-per-task=2
#SBATCH --ntasks=1
#SBATCH --time=1:00:00
#SBATCH --array=3-750%25
#SBATCH --out=afgi-mitogenomes/logs/file_download%A-%a.out

if [ "$#" -ne 3 ]; then
	echo "Usage: ${FUNCNAME[0]} <URL_FILE> <MD5SUM_FILE> <DOWNLOAD_DIR>" >&2
	return 1
fi

URL=$1
MD5=$2
DOWNLOAD_DIR=$3

mkdir -p $DOWNLOAD_DIR

i=$(cat $URL | awk -v id="${SLURM_ARRAY_TASK_ID}" 'NR==id {print $1}')

wget --header="X-CKAN-API-Key: ${BPA_APIKEY}" -P $DOWNLOAD_DIR $i

echo $(grep $(basename $i) $MD5 | cut -d" " -f1) ${DOWNLOAD_DIR}/$(basename $i) | md5sum -c
