## Overview

**POAtools** is a comprehensive bioinformatics toolkit for parental origin analysis and gene classification scoring in genetic studies. It provides a complete four-step pipeline for analyzing SNP data and generating publication-quality visualizations with R-style aesthetics implemented in Python.

## ✨ Features

- **Complete Analysis Pipeline**: Four integrated steps from raw VCF to visualization
- **Multi-format Support**: Handles VCF, VCF.gz, GFF, and various output formats
- **R-style Visualizations**: Python implementation replicating R plotting aesthetics
- **Batch Processing**: Process multiple samples automatically
- **Cross-platform**: Works on Linux, macOS, and Windows Subsystem for Linux (WSL)
- **Containerized**: Ready-to-use Docker images available
- **User-friendly**: Simple command-line interface with comprehensive help
- **Reproducible**: Complete R script replication in Python

## 🚀 Quick Installation

### One-line Installation (Recommended)
```bash
# Install POAtools in one command
curl -sSL https://raw.githubusercontent.com/yourusername/poatools/main/scripts/install.sh | bash
```

### Standard Installation
```bash
# Clone and install
git clone https://github.com/yourusername/poatools.git
cd poatools
./scripts/install.sh
```

### Alternative Installation Methods

#### Docker Installation
```bash
# Pull and run Docker image
docker run -v $(pwd):/data ghcr.io/yourusername/poatools:latest --help

# Or build locally
docker build -t poatools .
docker run -v $(pwd):/data poatools -h
```

#### Conda Installation
```bash
# Create conda environment
conda env create -f scripts/conda/environment.yml
conda activate poatools
```

#### Virtual Environment Installation
```bash
# Create isolated Python environment
./scripts/install.sh --venv
```

## 📖 Documentation

- [📘 User Manual](docs/manual.md) - Complete user guide and reference
- [🎓 Step-by-Step Tutorial](docs/tutorial.md) - Detailed tutorial with example data
- [❓ FAQ](docs/faq.md) - Frequently asked questions
- [🔧 Troubleshooting](docs/troubleshooting.md) - Common issues and solutions
- [📊 Examples](examples/) - Example data and scripts for quick start
- [📝 API Reference](docs/api_reference.md) - Detailed function documentation

## 🛠️ Usage Examples

### Complete Pipeline (All Steps)
```bash
# Run all four steps in one command
poatools -i input.vcf.gz -c parent1,parent2 -q samples.txt -1 -2 -3 -4

# Specify output directory
poatools -i input.vcf.gz -c ZR48,ZR166 -q samples.txt -1 -2 -3 -4 -o ./output/
```

### Step-by-Step Analysis
```bash
# Step 1: SNP density analysis
poatools -i sample.vcf.gz -c parent1,parent2 -q samples.txt -1 -o step1_output.vcf.gz

# Step 2: Gene classification scoring
poatools -i step1_output.vcf.gz -2 -o gene_scores.tsv

# Step 3: Gene statistics calculation
poatools -i gene_scores.tsv -3 -o stats_output/

# Step 4: Visualization (R-style)
poatools -i stats_output/gene_stats_sample.txt -genome reference.gff -4 -O visual_output/
```

### Quick Analysis with Defaults
```bash
# Simple analysis with default parameters
poatools -i sample.vcf -c ZR48,ZR166

# With custom confidence thresholds
poatools -i sample.vcf.gz -c parent1,parent2 -High 0.85 -Medium 0.6 -Min 0.3

# Batch process all samples in a directory
poatools -i stats_directory/ -genome reference.gff -4 -batch -O batch_output/
```

### Common Options
```bash
# Show help and all options
poatools --help

# Show version
poatools --version

# Test installation
poatools --test
```

## 📁 Input/Output Structure

### Input Files
```
input/
├── sample.vcf.gz              # Input VCF file (can be gzipped)
├── samples.txt               # Sample list file (one sample per line)
└── reference.gff             # Reference genome annotation (GFF format)
```

### Output Files (Complete Pipeline)
```
output/
├── step1_output.vcf.gz           # Step 1: SNP density analysis
├── gene_classification_scores.tsv # Step 2: Gene classification scores
├── stats_output/                 # Step 3: Gene statistics
│   ├── gene_stats_sample1.txt
│   ├── gene_stats_sample2.txt
│   └── summary_report.txt
└── visualization/               # Step 4: Visualizations
    ├── chromosome_facet_all_confidence.pdf
    ├── physical_heatmap_high_confidence.pdf
    ├── adjacent_gene_medium_confidence.pdf
    ├── score_ratio_all_confidence.pdf
    ├── confidence_pie.pdf
    ├── analysis_summary.txt
    ├── gff_based_gene_classification.csv
    └── gene_intervals_all_confidence.csv
```

## 🔧 System Requirements

### Minimum Requirements
- **Operating System**: Linux, macOS, or WSL2 (Windows Subsystem for Linux)
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM
- **Storage**: 10GB free disk space
- **CPU**: 2+ cores recommended

### Recommended for Large Datasets
- **Memory**: 16GB+ RAM
- **CPU**: 8+ cores
- **Storage**: 50GB+ free disk space
- **GPU**: Optional for accelerated visualizations

### Required Dependencies
- **Essential Tools**: `bcftools`, `awk`, `python3`
- **Python Packages**: `pandas`, `numpy`, `matplotlib`, `seaborn`
- **Optional Tools**: `tabix`, `bgzip`, `docker`

## 📚 Step-by-Step Guide

### Step 1: SNP Density Analysis
Processes VCF files and classifies SNPs based on parental genotypes:
- Input: VCF file + parent information
- Output: Classified VCF with SNP categories
- Command: `poatools -i input.vcf -c parent1,parent2 -q samples.txt -1`

### Step 2: Gene Classification Scoring
Extracts gene-level scores from Step 1 output:
- Input: Step 1 VCF output
- Output: Gene classification scores (TSV format)
- Command: `poatools -i step1_output.vcf -2`

### Step 3: Gene Statistics Calculation
Calculates comprehensive gene statistics:
- Input: Gene classification scores from Step 2
- Output: Per-sample gene statistics files
- Command: `poatools -i gene_scores.tsv -3`

### Step 4: R-style Visualization
Generates publication-quality visualizations:
- Input: Gene statistics + GFF annotation
- Output: PDF visualizations and summary reports
- Command: `poatools -i gene_stats.txt -genome reference.gff -4`

## 🐳 Docker Usage

### Quick Start with Docker
```bash
# Run POAtools in Docker container
docker run -v $(pwd):/data ghcr.io/yourusername/poatools:latest \
  -i /data/input.vcf.gz -c parent1,parent2 -q /data/samples.txt -1 -2 -3 -4

# Interactive Docker shell
docker run -it -v $(pwd):/data ghcr.io/yourusername/poatools:latest bash
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  poatools:
    image: ghcr.io/yourusername/poatools:latest
    volumes:
      - ./data:/data
      - ./output:/output
    command: -i /data/input.vcf.gz -c parent1,parent2 -q /data/samples.txt -1 -2 -3 -4 -O /output/
```

## 📊 Output Visualization Examples

POAtools generates several types of visualizations:

1. **Chromosome Facet Plots**: Gene classification distribution by chromosome
2. **Physical Heatmaps**: Gene classification along physical positions
3. **Adjacent Gene Plots**: Merged gene regions with same classification
4. **Score Ratio Line Plots**: Score ratios across genomic positions
5. **Confidence Pie Charts**: Gene classification by confidence level

All visualizations are generated as PDF files with publication-quality formatting.

## 📝 Citation

If you use POAtools in your research, please cite:

```bibtex
@software{poatools2024,
  author = {Your Name and Contributors},
  title = {POAtools: Parental Origin Analysis Toolkit},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/WZXIE/poatools},
  version = {4.0.0},
  doi = {10.5281/zenodo.XXXXXXX}
}
```

Or use the following citation format:

> Author Name et al. (2024). POAtools: Parental Origin Analysis Toolkit. Version 4.0.0. https://github.com/yourusername/poatools

## 🤝 Contributing

We welcome contributions from the community! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on how to:

1. **Report Issues**: Use our [issue tracker](https://github.com/yourusername/poatools/issues)
2. **Request Features**: Submit feature requests via GitHub issues
3. **Submit Pull Requests**: Follow our development workflow
4. **Improve Documentation**: Help enhance our documentation

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/poatools.git
cd poatools

# Set up development environment
./scripts/setup_dev.sh

# Run tests
./tests/run_tests.sh
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 POAtools Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 🆘 Support & Community

- **GitHub Issues**: [Bug reports and feature requests](https://github.com/yourusername/poatools/issues)
- **Discussions**: [Questions and community support](https://github.com/yourusername/poatools/discussions)
- **Wiki**: [Additional documentation and tutorials](https://github.com/yourusername/poatools/wiki)
- **Email**: team@poatools.org (for sensitive or private matters)

### Troubleshooting Common Issues

#### Installation Issues
```bash
# If Python dependencies fail to install
./scripts/install.sh --venv  # Use virtual environment
./scripts/install.sh --conda # Use conda
./scripts/install.sh --docker # Use Docker
```

#### Permission Issues
```bash
# If you get permission errors
chmod +x scripts/*.sh bin/*.py bin/*.sh
```

#### Dependencies Missing
```bash
# Install missing system dependencies
# For Ubuntu/Debian:
sudo apt-get install bcftools python3-pip

# For RHEL/CentOS:
sudo yum install bcftools python3-pip
```

## 🙏 Acknowledgments

We thank the following projects and communities for their inspiration and support:

- **BCFtools Team** for the excellent VCF processing tools
- **Python Scientific Stack** (NumPy, Pandas, Matplotlib, Seaborn) for data analysis capabilities
- **R Community** for visualization inspiration
- **All Contributors** who have helped improve POAtools
- **Users Worldwide** for valuable feedback and testing

### Special Thanks
- The bioinformatics community for continuous support
- Open-source software maintainers
- Academic researchers who have tested and validated POAtools

## 📞 Contact

- **Project Lead**: Your Name (your.email@example.com)
- **Technical Support**: support@poatools.org
- **Twitter**: [@POAtools](https://twitter.com/POAtools) (if applicable)
- **Mailing List**: poatools-users@googlegroups.com (if applicable)

---

**POAtools Development Team** | [GitHub](https://github.com/yourusername/poatools) | [Documentation](docs/) | [Issues](https://github.com/yourusername/poatools/issues)

*Last Updated: October 2024* | *Version: 4.0.0*

---

## 🔄 Updates and Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and updates.

### Recent Updates (v4.0.0)
- Complete rewrite of installation system
- Added Docker and Conda support
- Enhanced visualizations and performance
- Improved error handling and user experience
- Comprehensive test suite and documentation

### Future Roadmap
- Web interface development
- Additional visualization types
- Cloud deployment options
- Integration with popular bioinformatics platforms
- Machine learning enhancements

---

**⭐ If you find POAtools useful, please consider starring our repository on GitHub!**
