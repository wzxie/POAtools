#!/bin/bash

# POAtools - Step 1: SNP Density Analysis

if [[ $# -ne 5 ]]; then
    echo "Error: Step 1 script requires 5 parameters"
    echo "Usage: $0 <input_vcf> <sample_file> <parent1> <parent2> <output_file>"
    exit 1
fi

INPUT_VCF="$1"
SAMPLE_FILE="$2"
PARENT1="$3"
PARENT2="$4"
OUTPUT_FILE="$5"

echo "  Input VCF: $INPUT_VCF"
echo "  Sample file: $SAMPLE_FILE"
echo "  Parent 1: $PARENT1"
echo "  Parent 2: $PARENT2"
echo "  Output file: $OUTPUT_FILE"

if [[ ! -f "$INPUT_VCF" ]]; then
    echo "Error: Input VCF file does not exist: $INPUT_VCF"
    exit 1
fi

if [[ ! -f "$SAMPLE_FILE" ]]; then
    echo "Error: Sample list file does not exist: $SAMPLE_FILE"
    exit 1
fi

# Use awk to process VCF file
zcat "$INPUT_VCF" | awk -v parent1="$PARENT1" -v parent2="$PARENT2" '
BEGIN {
    # Read sample list file
    sample_file = "'"$SAMPLE_FILE"'";
    while ((getline sample_name < sample_file) > 0) {
        samples[sample_name] = 1;
    }
    close(sample_file);
    
    # Set output field separator
    OFS = "\t";
}

# Process header line
/^#CHROM/ {
    # Extract all sample names
    split($0, header_fields, "\t");
    sample_count = 0;
    
    # Find parent sample column indices
    for (i = 10; i <= NF; i++) {
        sample_name = header_fields[i];
        if (sample_name == parent1) parent1_idx = i;
        if (sample_name == parent2) parent2_idx = i;
        
        # Record sample indices to process (exclude parents)
        if (sample_name in samples && sample_name != parent1 && sample_name != parent2) {
            sample_indices[++sample_count] = i;
            sample_names[i] = sample_name;
        }
    }
    
    # Print new header
    printf "%s", "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT";
    for (i = 1; i <= sample_count; i++) {
        idx = sample_indices[i];
        printf "\t%s", sample_names[idx];
    }
    printf "\n";
    next;
}

# Print other annotation lines
/^#/ {
    print;
    next;
}

# Process variant lines
{
    # Extract parent genotypes
    parent1_gt = $(parent1_idx);
    parent2_gt = $(parent2_idx);
    
    # Standardize genotypes, replace | with /
    gsub(/\|/, "/", parent1_gt);
    gsub(/\|/, "/", parent2_gt);
    
    # Extract genotype part (content before colon)
    split(parent1_gt, parent1_arr, ":");
    parent1_gt = parent1_arr[1];
    split(parent2_gt, parent2_arr, ":");
    parent2_gt = parent2_arr[1];
    
    # Initialize result string
    result = "";
    
    # Process each selected sample (excluding parents)
    for (i = 1; i <= length(sample_indices); i++) {
        idx = sample_indices[i];
        sample_name = sample_names[idx];
        sample_gt_full = $(idx);
        
        # Standardize sample genotype
        gsub(/\|/, "/", sample_gt_full);
        split(sample_gt_full, sample_arr, ":");
        sample_gt = sample_arr[1];
        
        # If parent samples are missing, output Unknown
        if (parent1_gt == "./." || parent2_gt == "./.") {
            result = result "Unknown\t";
            continue;
        }
        
        # Determine output based on parent and sample genotypes
        if (parent1_gt == "0/0" && parent2_gt == "0/0") {
            if (sample_gt == "0/0") {
                result = result "AB(2)\t";
            } else if (sample_gt == "0/1") {
                result = result "AB(1)\t";
            } else if (sample_gt == "1/1") {
                result = result "NAB(2)\t";
            } else {
                result = result "Unknown\t";
            }
        } else if (parent1_gt == "0/0" && parent2_gt == "0/1") {
            if (sample_gt == "0/0") {
                result = result "A(2)\t";
            } else if (sample_gt == "0/1") {
                result = result "B(2)\t";
            } else if (sample_gt == "1/1") {
                result = result "B(1)\t";
            } else {
                result = result "Unknown\t";
            }
        } else if (parent1_gt == "0/0" && parent2_gt == "1/1") {
            if (sample_gt == "0/0") {
                result = result "A(2)\t";
            } else if (sample_gt == "0/1") {
                result = result "AXB(2)\t";
            } else if (sample_gt == "1/1") {
                result = result "B(2)\t";
            } else {
                result = result "Unknown\t";
            }
        } else if (parent1_gt == "0/1" && parent2_gt == "0/0") {
            if (sample_gt == "0/0") {
                result = result "B(2)\t";
            } else if (sample_gt == "0/1") {
                result = result "A(2)\t";
            } else if (sample_gt == "1/1") {
                result = result "A(1)\t";
            } else {
                result = result "Unknown\t";
            }
        } else if (parent1_gt == "0/1" && parent2_gt == "0/1") {
            if (sample_gt == "0/0") {
                result = result "AXB(2)\t";
            } else if (sample_gt == "0/1") {
                result = result "AB(2)\t";
            } else if (sample_gt == "1/1") {
                result = result "AXB(2)\t";
            } else {
                result = result "Unknown\t";
            }
        } else if (parent1_gt == "0/1" && parent2_gt == "1/1") {
            if (sample_gt == "0/0") {
                result = result "A(1)\t";
            } else if (sample_gt == "0/1") {
                result = result "A(2)\t";
            } else if (sample_gt == "1/1") {
                result = result "B(2)\t";
            } else {
                result = result "Unknown\t";
            }
        } else if (parent1_gt == "1/1" && parent2_gt == "0/0") {
            if (sample_gt == "0/0") {
                result = result "B(2)\t";
            } else if (sample_gt == "0/1") {
                result = result "AXB(2)\t";
            } else if (sample_gt == "1/1") {
                result = result "A(2)\t";
            } else {
                result = result "Unknown\t";
            }
        } else if (parent1_gt == "1/1" && parent2_gt == "0/1") {
            if (sample_gt == "0/0") {
                result = result "B(1)\t";
            } else if (sample_gt == "0/1") {
                result = result "B(2)\t";
            } else if (sample_gt == "1/1") {
                result = result "A(2)\t";
            } else {
                result = result "Unknown\t";
            }
        } else if (parent1_gt == "1/1" && parent2_gt == "1/1") {
            if (sample_gt == "0/0") {
                result = result "NAB(2)\t";
            } else if (sample_gt == "0/1") {
                result = result "AB(1)\t";
            } else if (sample_gt == "1/1") {
                result = result "AB(2)\t";
            } else {
                result = result "Unknown\t";
            }
        } else {
            result = result "Unknown\t";
        }
    }
    
    # Remove trailing tab
    sub(/\t$/, "", result);
    
    # Output result
    print $1, $2, $3, $4, $5, $6, $7, $8, $9, result;
}' | gzip > "$OUTPUT_FILE"

exit_code=$?
if [[ $exit_code -eq 0 ]]; then
    echo "  Step 1 completed: Successfully generated $OUTPUT_FILE"
else
    echo "  Step 1 failed: Exit code $exit_code"
fi

exit $exit_code