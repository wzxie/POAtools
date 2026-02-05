## Overview
﻿
**POAtools** is a comprehensive bioinformatics toolkit for parental origin analysis and gene classification scoring in genetic studies. It provides a complete four-step pipeline for analyzing SNP data and generating publication-quality visualizations.

## ✨ Features

- **Complete Analysis Pipeline**: Four integrated steps from raw VCF to visualization
- **Multi-format Support**: Handles VCF, VCF.gz, GFF, and various output formats
- **R-style Visualizations**: Python implementation replicating R plotting aesthetics
- **Batch Processing**: Process multiple samples automatically
- **Cross-platform**: Works on Linux, macOS, and Windows Subsystem for Linux (WSL)
- **Containerized**: Ready-to-use Docker images available
- **User-friendly**: Simple command-line interface with comprehensive help

## 🚀 Quick Start

### One-line Installation
```bash
# Install POAtools in one command
curl -sSL https://raw.githubusercontent.com/yourusername/poatools/main/scripts/install.sh | bash
Standard Installation
bash
# Clone and install
git clone https://github.com/yourusername/poatools.git
cd poatools
./scripts/install.sh
Alternative Methods
bash
# Use Docker
docker run -v $(pwd):/data ghcr.io/yourusername/poatools:latest --help

# Use Conda
conda env create -f scripts/conda/environment.yml
conda activate poatools
📖 Documentation
📘 User Manual - Complete user guide

🎓 Tutorial - Step-by-step tutorial with examples

❓ FAQ - Frequently asked questions

🔧 Troubleshooting - Common issues and solutions

📊 Examples - Example data and scripts

🛠️ Usage Examples
Complete Pipeline
bash
# Run all four steps
poatools -i input.vcf.gz -c parent1,parent2 -q samples.txt -1 -2 -3 -4

# Or step by step
poatools -i input.vcf.gz -c parent1,parent2 -q samples.txt -1 -o step1.vcf.gz
poatools -i step1.vcf.gz -2 -o gene_scores.tsv
poatools -i gene_scores.tsv -3 -o stats_output/
poatools -i stats_output/gene_stats_sample.txt -genome reference.gff -4 -O visual_output/
Quick Analysis
bash
# Simple analysis with defaults
poatools -i sample.vcf -c ZR48,ZR166

# With custom thresholds
poatools -i sample.vcf.gz -c parent1,parent2 -High 0.85 -Medium 0.6 -Min 0.3
📁 Output Structure
text
output/
├── step1_output.vcf.gz           # Step 1: SNP density analysis
├── gene_classification_scores.tsv # Step 2: Gene classification scores
├── gene_stats_sample1.txt        # Step 3: Gene statistics
├── gene_stats_sample2.txt
└── visualization/               # Step 4: Visualizations
    ├── chromosome_facet_all_confidence.pdf
    ├── physical_heatmap_high_confidence.pdf
    ├── adjacent_gene_medium_confidence.pdf
    ├── score_ratio_all_confidence.pdf
    └── analysis_summary.txt
🔧 System Requirements
Minimum
Linux, macOS, or WSL

Python 3.8+

4GB RAM, 10GB disk space

Recommended
8GB+ RAM for large datasets

Multi-core CPU for faster processing

GPU for accelerated visualizations (optional)

Dependencies
Essential: bcftools, awk, python3

Python packages: pandas, numpy, matplotlib, seaborn

Optional: tabix, bgzip, docker

📚 Citation
If you use POAtools in your research, please cite:

bibtex
@software{poatools2024,
  author = {Your Name and Contributors},
  title = {POAtools: Parental Origin Analysis Toolkit},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/yourusername/poatools},
  version = {4.0.0},
  doi = {10.5281/zenodo.XXXXXXX}
}
🤝 Contributing
We welcome contributions! Please see our Contributing Guidelines for details.

Fork the repository

Create a feature branch

Make your changes

Submit a pull request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🆘 Support
GitHub Issues - Bug reports and feature requests

Discussions - Questions and community support

Wiki - Additional documentation

🙏 Acknowledgments
We thank the following projects and communities:

BCFtools for VCF processing

The Python scientific stack (NumPy, Pandas, Matplotlib, Seaborn)

The bioinformatics community for valuable feedback and testing

All contributors and users of POAtools
