## Overview

POAtools is a comprehensive bioinformatics toolkit for **parental origin analysis** and **gene classification scoring** in genetic studies. It processes SNP data from VCF files, classifies alleles based on parental genotypes, calculates gene-level statistics, and generates publication‑quality visualizations. Users can follow the guidance provided in the **Usage** section to achieve complete analysis from raw VCF to final figures.

## Dependencies

- **Python 3.8+** with packages: `pandas`, `numpy`, `matplotlib`, `seaborn`
- `bcftools` (≥1.9)
- `awk` (GNU Awk ≥4.0)
- `tabix` (optional, for indexed VCF)
- `bgzip` (optional, for compression)

## Installation

Run the following commands to install POAtools and its dependencies.

### (1) Download POAtools from GitHub

```bash
git clone https://github.com/yourusername/poatools.git
cd poatools
chmod 755 bin/* scripts/*.sh
export PATH=$(pwd)/bin:$PATH
```

### (2) Install dependencies

#### a. Install with conda / mamba (recommended)

```bash
mamba create -y -n poatools python=3.9
mamba activate poatools
mamba install -c conda-forge -c bioconda bcftools pandas numpy matplotlib seaborn -y
```

#### b. Install with pip (Python packages only)

```bash
pip3 install --user pandas numpy matplotlib seaborn
```

#### c. Install system tools (if missing)

```bash
# Ubuntu/Debian
sudo apt-get install bcftools gawk tabix

# RHEL/CentOS
sudo yum install bcftools gawk
```

### (3) Test installation

```bash
poatools --help
python3 bin/check_python_deps.py
```

## Example

### 1. Download example data

```bash
wget https://zenodo.org/record/xxxxxxx/files/demo.vcf.gz
wget https://zenodo.org/record/xxxxxxx/files/samples.txt
wget https://zenodo.org/record/xxxxxxx/files/ref.gff
```

### 2. Run POAtools

```bash
poatools -i demo.vcf.gz -c ZR48,ZR166 -q samples.txt -1 -2 -3 -4 -genome ref.gff -O output/ &> poatools.log
```

## Usage

### Quick start

```bash
Usage: poatools -i <input.vcf> -c <parent1,parent2> -q <sample_list> [options]
```

**Input/Output options:**
```
-i        input VCF file (can be .vcf or .vcf.gz)
-c        comma‑separated parent names (e.g., parent1,parent2)
-q        sample list file (one sample per line)
-genome   reference genome annotation (GFF3) for Step 4
-O        output directory (default: ./output)
```

**Step selection (run one or more):**
```
-1        run Step 1: SNP density analysis
-2        run Step 2: gene classification scoring
-3        run Step 3: gene statistics calculation
-4        run Step 4: R‑style visualization
```

**Filter and polish options:**
```
-High     high confidence threshold (default: 0.8)
-Medium   medium confidence threshold (default: 0.5)
-Min      minimum ratio threshold (default: 0.4)
```

**General options:**
```
-t        number of threads (default: 1)
-v, --version  show version
-h, --help     show help information
```

See more information at [https://github.com/yourusername/poatools](https://github.com/yourusername/poatools)

## Proceed in a stepwise fashion

Users may want to run each step separately, e.g., for debugging or integrating with other tools.

### (i) Step 1 – SNP density analysis

Classify each SNP based on parental genotypes.

```bash
poatools -i input.vcf -c parent1,parent2 -q samples.txt -1 -o step1.vcf.gz
```

### (ii) Step 2 – Gene classification scoring

Extract gene‑level classification scores from Step 1 output.

```bash
poatools -i step1.vcf.gz -2 -o gene_scores.tsv
```

### (iii) Step 3 – Gene statistics calculation

Compute per‑sample statistics (A, B, AB, NAB, AXB scores and nonzero sites).

```bash
poatools -i gene_scores.tsv -3 -o stats/
```

### (iv) Step 4 – Visualization

Generate publication‑ready figures (chromosome facet plots, physical heatmaps, adjacent gene plots, score ratio line plots, confidence pie charts).

```bash
poatools -i stats/gene_stats_sample.txt -genome ref.gff -4 -O visual/
```

## Inputs and Outputs

### Input files

**VCF file** (can be gzipped)
```
#CHROM  POS   ID   REF   ALT   QUAL   FILTER   INFO   FORMAT   Sample1   Sample2
chr1    1000  .    A     G     60     .        .      GT:DP    0/0:10    0/1:12
...
```

**Sample list file** (one sample per line)
```
Sample1
Sample2
```

**GFF3 annotation file**
```
##gff-version 3
chr1    .       gene    1000    2000    .    +    .    ID=Gene1
```

### Output files

* `step1_output.vcf.gz`               – classified VCF with SNP categories
* `gene_classification_scores.tsv`    – gene‑level scores (Gene, Sample, Classification, Score)
* `stats/gene_stats_<sample>.txt`     – per‑sample gene statistics (A, B, AB, NAB, AXB, nonzero sites)
* `visualization/chromosome_facet_*.pdf` – bar plots of gene counts per chromosome
* `visualization/physical_heatmap_*.pdf` – gene classification along physical positions
* `visualization/adjacent_gene_*.pdf`    – merged gene region classification
* `visualization/score_ratio_*.pdf`      – score ratio line plots across chromosomes
* `visualization/confidence_pie.pdf`     – pie charts for confidence levels
* `visualization/analysis_summary.txt`   – textual summary of results

## Visual outputs

- **Chromosome facet plot** – distribution of gene classes across chromosomes.
- **Physical heatmap** – classification of genes plotted by genomic coordinates.
- **Adjacent gene plot** – continuous segments of merged same‑class genes and intergenic regions.
- **Score ratio line plot** – ratio trends for each class along each chromosome.
- **Confidence pie charts** – proportion of high/medium/low confidence calls.

## Citing POAtools

If you use POAtools in your research, please cite:

> Your Name, et al. (2024). POAtools: Parental Origin Analysis and Gene Classification Scoring Toolkit. *Journal Name*, Volume(Issue), pages. DOI:XXXXXX

BibTeX entry:
```bibtex
@software{poatools2024,
  author = {Your Name and Contributors},
  title = {POAtools: Parental Origin Analysis Toolkit},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/yourusername/poatools},
  version = {4.0.0},
  doi = {10.5281/zenodo.XXXXXXX}
}
```

## Contact

We hope this toolkit will be helpful for researchers working on population genetics, plant breeding, and evolutionary studies. Please use the GitHub issue tracker to report bugs or request features, or email us with any suggestions.

- Your Name: your.email@example.com
- Project homepage: [https://github.com/yourusername/poatools](https://github.com/yourusername/poatools)
- Issues: [https://github.com/yourusername/poatools/issues](https://github.com/yourusername/poatools/issues)

---

**POAtools Development Team** | *Last update: April 2025* | *Version 4.0.0*
