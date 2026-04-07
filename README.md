## Overview

POAtools is a bioinformatics toolkit for parental origin analysis and gene classification scoring in genetic studies. It processes SNP data from VCF files, classifies alleles based on parental genotypes, calculates gene-level statistics, and generates visualizations. Users can follow the guidance provided in the Usage section to achieve complete analysis from raw VCF to final figures.

![workflow](https://github.com/wzxie/POAtools/blob/main/workflow.jpg)

## Dependencies

- Python 3.8+ with packages: `pandas`, `numpy`, `matplotlib`, `seaborn`
- `bcftools` (≥1.9)
- `awk` (GNU Awk ≥4.0)
- `tabix` (optional, for indexed VCF)
- `bgzip` (optional, for compression)

## Installation

### (1) Download POAtools from GitHub

```bash
git clone https://github.com/wzxie/POAtools.git
```

### (2) Run the automatic installation script

The `install.sh` script will:
- Set execute permissions for all tools
- Create a global `POAtools` command (via symlink in `~/.local/bin`)
- Add `~/.local/bin` to your `PATH` (if not already present)
- Check and install required Python dependencies (pandas, numpy, matplotlib, seaborn)
- Generate helper scripts (`setup_environment.sh`, `setup_alias.sh`, `fix_python_deps.sh`, `test_installation.sh`)
- Create an `output/` directory for results

```bash
./install.sh
```

After a successful installation, you will see:
```
✓ POAtools command is now available!
You can use: POAtools -h
```

## Example

### 1. Download example data

```bash
To be announced
```

### 2. Run POAtools

```bash
POAtools -i demo.vcf.gz -c ZR48,ZR166 -q samples.txt -1 -2 -3 -4 -genome ref.gff -O output
```

## Usage

### Quick start

```bash
Usage: POAtools [options]

Required options:
    -i, --input VCF         Input VCF file
    -c, --parents SAMPLES   Set parent samples, comma separated (e.g.: ZR48,ZR166)
    -q, --samples-file FILE Set sample list file

Other options:
    -p, --prefix PREFIX     Set output file prefix (default: "output")
    -o, --output DIR        Output directory (default: current directory)
    -1, --step1             Run step 1 (SNP density analysis)
    -2, --step2             Run step 2 (Gene classification scoring)
    -3, --step3             Run step 3 (Gene statistics calculation)
    -4, --step4             Run step 4 (Gene classification visualization)
    -genome genome.gff            Genome file for visualization (required for step 4 and run all steps)
    -High VALUE             High confidence threshold for step 4 default=0.8 (optional)
    -Medium VALUE           Medium confidence threshold for step 4 default=0.5 (optional)
    -Min VALUE              Minimum confidence threshold for step 4 default=0.4 (optional)
    -v, --visual T/F        Enable/disable visualization in step 4 (default: T)
    -h, --help              Display this help message

Examples:
    POAtools -i demo.vcf.gz -c ZR48,ZR166 -q samples.txt -1
    POAtools -i demo.vcf.gz -c ZR48,ZR166 -q samples.txt -p my_analysis -o ./results -1 -2 -3
    POAtools -i step1_output.vcf.gz -2
    POAtools -i output_gene_classification_scores.tsv -o ./output -3
    POAtools -i gene_stats_dir -genome genome.gff -4
    POAtools -i gene_stats_sample1.txt -genome genome.gff -4 -High 0.9 -Medium 0.6 -Min 0.3 -v F
    POAtools -i demo.vcf.gz -c ZR48,ZR166 -q samples.txt -genome genome.gff  # Run all steps by default

Description:
    Step 1: Process VCF file based on parent samples and sample list, generate classification results
    Step 2: Extract gene information and scores from classification results
    Step 3: Calculate gene statistics including A, B, AB, NAB, AXB scores and nonzero site counts
    Step 4: Generate comprehensive gene classification and visualization plots

Note: If no steps are specified (-1, -2, -3, -4), all steps will be run by default.

```
## Proceed in a stepwise fashion

Users may want to run each step separately, e.g., for debugging or integrating with other tools.

### (i) Step 1 – SNP density analysis

Classify each SNP based on parental genotypes.

```bash
POAtools -i input.vcf -c parent1,parent2 -q samples.txt -1 -o step1.vcf.gz
```

### (ii) Step 2 – Gene classification scoring

Extract gene‑level classification scores from Step 1 output.

```bash
POAtools -i step1.vcf.gz -2 -o gene_scores.tsv
```

### (iii) Step 3 – Gene statistics calculation

Compute per‑sample statistics (A, B, AB, NAB, AXB scores and nonzero sites).

```bash
POAtools -i gene_scores.tsv -3 -o stats/
```

### (iv) Step 4 – Visualization

Generate publication‑ready figures (chromosome facet plots, physical heatmaps, adjacent gene plots, score ratio line plots, confidence pie charts).

```bash
POAtools -i stats/gene_stats_sample.txt -genome ref.gff -4 -O visual/
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

- **Chromosome classification proportion chart** - distribution of gene categories on chromosomes.
- **Gene classification chart** – a map of gene classification plotted according to genomic coordinates.
- **Segment classification diagram** –  a continuous segment composed of merged homologous genes and intergenic regions.
- **Score ratio line chart** – ratio trends for each class along each chromosome.
- **Confidence pie chart** – proportion of high/medium/low confidence calls.

## Citing POAtools


## Contact

We hope this toolkit will be helpful for researchers working on population genetics, plant breeding, and evolutionary studies. Please use the GitHub issue tracker to report bugs or request features, or email us with any suggestions.

- Xie wenzhao: wzxie@hebtu.edu.cn
- Yang yufeng: 751878693@qq.com
