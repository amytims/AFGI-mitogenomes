# AFGI-mitogenomes

Scripts for assembling and annotating mitogenomes from AFGI short-read datasets

1. bpa_parallel_downloads.sh - downloads multiple files off BPA data portal in parallel
2. mitoannotator.py - script for automating mitogenome annotation using the MitoFish web interface
3. megahit.sh - test run of the MEGAHIT assembly program
4. get_organelle.sh - test run of the getOrganelle program


## bpa_parallel_downloads.sh

The default script you get when you put multiple files into your BPA data portal cart downloads files one at a time, which is time-consuming if you're downloading a huge number of pop-gen files. This script speeds up the process by running the downloads in batches. The function takes three inputs: a url file (found in /tmp/...urls.txt in the .gz file you get from BPA), an md5sum file (/tmp/...md5sum.txt), and a file path to the directory where you want your downloads to go. 

### Usage

```bash
sbatch bpa_parallel_downloads.sh urls.txt md5sum.txt /path/to/download/dir
```

## mitoannotator.py

[MitoFish](https://mitofish.aori.u-tokyo.ac.jp/) is a great resource, offering fish-specific mitogenome annotation through its [MitoAnnotator](https://mitofish.aori.u-tokyo.ac.jp/annotation/input) interface. However, it can only [be accessed via web interface](https://pmc.ncbi.nlm.nih.gov/articles/PMC3808866/), which slows down researchers who have a backlog of many fishy mitogenomes to annotate and upload to NCBI. This script automates the process of accessing the web interface and downloading the annotation files, making it possible to iterate over multiple mitogenomes without having to manually copy-paste everything.

>[!WARNING]
>Trying to click the 'Annotate!' button with JavaScript seems to cause an error on the webpage so we're doing a regular click - this means the button and the window need to be visible. Don't minimise the window or it'll break :(

Set up python venv and install requirements with:

```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r requirements.txt
```

### Usage

Run the script over all mitogenome assemblies in a directory with:

```bash
for file in mt_dir/*; do 
    echo "Running loop on $file"
    python3 mitoannotator.py -f $file
done
```

#### Full Usage:

```
usage: mitoannotator.py [-h] -f FASTA [-d DOWNLOAD_DIR]

Run a target fasta (compressed or uncompressed) through the MitoAnnotator process on MitoFish

options:
  -h, --help            show this help message and exit
  -f FASTA, --fasta FASTA
                        path to input fasta file
  -d DOWNLOAD_DIR, --download_dir DOWNLOAD_DIR
                        path to download parent directory. Files will be saved in download_dir/fasta/
```

## megahit.sh

Array script for running fastp and megahit on a whole bunch of paired shortread datasets.


## get_organelle.sh

Test script for running getOrganelle on a paired shortread dataset. Decided not to continue with this program as it's more memory intensive than megahit