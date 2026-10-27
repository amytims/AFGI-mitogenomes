# AFGI-mitogenomes

Scripts for assembling and annotating mitogenomes from AFGI short-read datasets

1. get_organelle.sh - test run of the getOrganelle program
2. megahit.sh - test run of the MEGAHIT assembly program
3. mitoannotator.py - script for automating mitogenome annotation using the MitoFish web interface

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