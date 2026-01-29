#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
POAtools - Step 4: Gene Classification Visualization (Python Version)
Complete Python implementation that exactly replicates R script functionality
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import re
import warnings
warnings.filterwarnings('ignore')

class ExactRReplication:
    def __init__(self, high_threshold=0.8, medium_threshold=0.5, min_threshold=0.4, visual=True):
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold
        self.min_threshold = min_threshold
        self.visual = visual
        self.chromosome_lengths = {}
        
    def read_gff_data(self, gff_file):
        """Exactly replicate R's GFF reading functionality"""
        print(f"Reading GFF file: {gff_file}")
        
        gff_data = []
        
        # Read chromosome lengths from header (replicating R's behavior)
        with open(gff_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('##sequence-region'):
                    parts = line.strip().split()
                    if len(parts) >= 4:
                        chrom = parts[1]
                        length = int(parts[3])
                        self.chromosome_lengths[chrom] = length
                
                if line.startswith('#'):
                    continue
                
                parts = line.strip().split('\t')
                if len(parts) < 9:
                    continue
                
                # Only process gene features (exactly like R)
                if parts[2] != 'gene':
                    continue
                
                seqname = parts[0]
                feature_type = parts[2]
                start = int(parts[3])
                end = int(parts[4])
                strand = parts[6]
                attributes = parts[8]
                
                # Parse attributes exactly like R
                gene_id = None
                for attr in attributes.split(';'):
                    if 'ID=' in attr:
                        gene_id = attr.split('=')[1]
                        break
                    elif 'gene_id=' in attr:
                        gene_id = attr.split('=')[1]
                        break
                    elif 'Name=' in attr:
                        gene_id = attr.split('=')[1]
                        break
                
                if gene_id:
                    gff_data.append({
                        'Gene': gene_id,
                        'Chromosome': seqname,
                        'Start': start,
                        'End': end,
                        'Length': end - start + 1,
                        'Strand': strand
                    })
        
        gff_df = pd.DataFrame(gff_data)
        print(f"  Found {len(gff_df)} genes in GFF file")
        print(f"  Found {len(self.chromosome_lengths)} chromosome lengths")
        
        return gff_df
    
    def check_and_resolve_overlaps(self, data):
        """Exactly replicate R's overlap resolution logic"""
        
        resolved_data = data.copy()
        
        for chrom in resolved_data['Chromosome'].unique():
            chr_data = resolved_data[resolved_data['Chromosome'] == chrom].sort_values('Start')
            
            if len(chr_data) < 2:
                continue
            
            i = 0
            while i < len(chr_data) - 1:
                row_i = chr_data.iloc[i]
                row_i1 = chr_data.iloc[i+1]
                
                if row_i['End'] >= row_i1['Start']:
                    
                    if row_i['Primary_Class'] == row_i1['Primary_Class']:
                        # Merge overlapping genes with same classification
                        new_end = max(row_i['End'], row_i1['End'])
                        resolved_data.loc[resolved_data['Gene'] == row_i['Gene'], 'End'] = new_end
                        
                        # Remove the second gene
                        resolved_data = resolved_data[resolved_data['Gene'] != row_i1['Gene']]
                        
                        # Refresh chromosome data
                        chr_data = resolved_data[resolved_data['Chromosome'] == chrom].sort_values('Start')
                    else:
                        # Adjust end position for different classifications
                        resolved_data.loc[resolved_data['Gene'] == row_i['Gene'], 'End'] = row_i1['Start'] - 1
                        i += 1
                else:
                    i += 1
        
        return resolved_data
    
    def create_gene_intervals(self, data):
        """Exactly replicate R's gene interval creation logic"""
        intervals_list = []
        
        for chrom in data['Chromosome'].unique():
            chr_data = data[data['Chromosome'] == chrom].sort_values('Start')
            
            if len(chr_data) == 0:
                continue
            
            # Create initial intervals (gene regions only)
            gene_intervals = pd.DataFrame({
                'Chromosome': chrom,
                'Start': chr_data['Start'].values,
                'End': chr_data['End'].values,
                'Primary_Class': chr_data['Primary_Class'].astype(str).values
            })
            
            # Merge overlapping and adjacent same-class segments
            merged_intervals = pd.DataFrame(columns=['Chromosome', 'Start', 'End', 'Primary_Class'])
            
            if len(gene_intervals) > 0:
                gene_intervals = gene_intervals.sort_values('Start')
                
                current_start = gene_intervals['Start'].iloc[0]
                current_end = gene_intervals['End'].iloc[0]
                current_class = gene_intervals['Primary_Class'].iloc[0]
                
                for i in range(1, len(gene_intervals)):
                    row = gene_intervals.iloc[i]
                    if (row['Primary_Class'] == current_class and 
                        row['Start'] <= current_end + 1):
                        current_end = max(current_end, row['End'])
                    else:
                        merged_intervals = pd.concat([merged_intervals, pd.DataFrame({
                            'Chromosome': [chrom],
                            'Start': [current_start],
                            'End': [current_end],
                            'Primary_Class': [current_class]
                        })], ignore_index=True)
                        current_start = row['Start']
                        current_end = row['End']
                        current_class = row['Primary_Class']
                
                merged_intervals = pd.concat([merged_intervals, pd.DataFrame({
                    'Chromosome': [chrom],
                    'Start': [current_start],
                    'End': [current_end],
                    'Primary_Class': [current_class]
                })], ignore_index=True)
            
            # Add intergenic regions
            final_intervals = pd.DataFrame(columns=['Chromosome', 'Start', 'End', 'Primary_Class'])
            
            # Add region before first gene
            if len(merged_intervals) > 0 and merged_intervals['Start'].iloc[0] > 1:
                final_intervals = pd.concat([final_intervals, pd.DataFrame({
                    'Chromosome': [chrom],
                    'Start': [1],
                    'End': [merged_intervals['Start'].iloc[0] - 1],
                    'Primary_Class': ['Intergenic']
                })], ignore_index=True)
            
            # Add merged gene regions and intergenic regions
            for i in range(len(merged_intervals)):
                # Add current gene region
                final_intervals = pd.concat([final_intervals, pd.DataFrame({
                    'Chromosome': [chrom],
                    'Start': [merged_intervals['Start'].iloc[i]],
                    'End': [merged_intervals['End'].iloc[i]],
                    'Primary_Class': [merged_intervals['Primary_Class'].iloc[i]]
                })], ignore_index=True)
                
                # Add intergenic region if exists
                if i < len(merged_intervals) - 1:
                    gap_start = merged_intervals['End'].iloc[i] + 1
                    gap_end = merged_intervals['Start'].iloc[i+1] - 1
                    
                    if gap_start <= gap_end:
                        final_intervals = pd.concat([final_intervals, pd.DataFrame({
                            'Chromosome': [chrom],
                            'Start': [gap_start],
                            'End': [gap_end],
                            'Primary_Class': [merged_intervals['Primary_Class'].iloc[i]]
                        })], ignore_index=True)
            
            # Add region after last gene
            if chrom in self.chromosome_lengths and len(merged_intervals) > 0:
                chr_length = self.chromosome_lengths[chrom]
                last_gene_end = merged_intervals['End'].iloc[-1]
                if last_gene_end < chr_length:
                    final_intervals = pd.concat([final_intervals, pd.DataFrame({
                        'Chromosome': [chrom],
                        'Start': [last_gene_end + 1],
                        'End': [chr_length],
                        'Primary_Class': ['Intergenic']
                    })], ignore_index=True)
            
            # Final merge of all adjacent same-class segments
            if len(final_intervals) > 0:
                fully_merged = pd.DataFrame(columns=['Chromosome', 'Start', 'End', 'Primary_Class'])
                
                current_final_start = final_intervals['Start'].iloc[0]
                current_final_end = final_intervals['End'].iloc[0]
                current_final_class = final_intervals['Primary_Class'].iloc[0]
                
                for j in range(1, len(final_intervals)):
                    row = final_intervals.iloc[j]
                    if (row['Primary_Class'] == current_final_class and 
                        row['Start'] == current_final_end + 1):
                        current_final_end = row['End']
                    else:
                        fully_merged = pd.concat([fully_merged, pd.DataFrame({
                            'Chromosome': [chrom],
                            'Start': [current_final_start],
                            'End': [current_final_end],
                            'Primary_Class': [current_final_class]
                        })], ignore_index=True)
                        current_final_start = row['Start']
                        current_final_end = row['End']
                        current_final_class = row['Primary_Class']
                
                fully_merged = pd.concat([fully_merged, pd.DataFrame({
                    'Chromosome': [chrom],
                    'Start': [current_final_start],
                    'End': [current_final_end],
                    'Primary_Class': [current_final_class]
                })], ignore_index=True)
                
                intervals_list.append(fully_merged)
        
        # Combine intervals from all chromosomes
        if intervals_list:
            all_intervals = pd.concat(intervals_list, ignore_index=True)
            all_intervals['Center'] = (all_intervals['Start'] + all_intervals['End']) / 2
            all_intervals['Length'] = all_intervals['End'] - all_intervals['Start'] + 1
            return all_intervals
        else:
            return pd.DataFrame(columns=['Chromosome', 'Start', 'End', 'Primary_Class', 'Center', 'Length'])
    
    def process_data(self, stats_file, gff_file):
        """Exactly replicate R's data processing logic"""
        print("Processing data...")
        
        # Read gene stats data (exactly like R)
        if stats_file.endswith('.txt'):
            data = pd.read_csv(stats_file, sep='\t')
        else:
            data = pd.read_csv(stats_file)
        
        print(f"  Loaded {len(data)} genes from stats file")
        
        # Read GFF data
        gff_df = self.read_gff_data(gff_file)
        
        # Merge with GFF information (left_join equivalent)
        data_processed = pd.merge(data, gff_df, on='Gene', how='left')
        
        # Calculate total score and ratios (exactly like R)
        data_processed['Total_Score'] = (data_processed['A'] + data_processed['B'] + 
                                        data_processed['AB'] + data_processed['NAB'] + 
                                        data_processed['AXB'])
        
        # Calculate ratios and handle division by zero (exactly like R)
        for score_type in ['A', 'B', 'AB', 'NAB', 'AXB']:
            ratio_col = f'{score_type}_ratio'
            data_processed[ratio_col] = data_processed[score_type] / data_processed['Total_Score']
            data_processed[ratio_col] = data_processed[ratio_col].fillna(0)
        
        # Sort by chromosome and start position (exactly like R)
        data_processed = data_processed.sort_values(['Chromosome', 'Start'])
        
        # Check for unmatched genes (exactly like R)
        unmatched_genes = data_processed[data_processed['Start'].isna()]['Gene']
        if len(unmatched_genes) > 0:
            print(f"Warning: {len(unmatched_genes)} genes could not be matched in GFF file")
            print("These genes will be excluded from physical position-based analysis")
        
        return data_processed
    
    def classify_genes(self, data):
        """Exactly replicate R's gene classification logic"""
        print("Classifying genes...")
        
        # Find maximum ratio for each gene (exactly like R)
        ratio_cols = ['A_ratio', 'B_ratio', 'AB_ratio', 'NAB_ratio', 'AXB_ratio']
        data['Max_Ratio'] = data[ratio_cols].max(axis=1)
        
        # Determine primary classification (exactly like R's case_when logic)
        def get_primary_class(row):
            max_ratio = row['Max_Ratio']
            
            # If max ratio < min_threshold, classify as NAB (Mixed in R is mapped to NAB)
            if max_ratio < self.min_threshold:
                return 'NAB'
            
            # Find the class with maximum ratio
            ratios = {
                'A': row['A_ratio'],
                'B': row['B_ratio'],
                'AB': row['AB_ratio'],
                'NAB': row['NAB_ratio'],
                'AXB': row['AXB_ratio']
            }
            
            return max(ratios.items(), key=lambda x: x[1])[0]
        
        data['Primary_Class'] = data.apply(get_primary_class, axis=1)
        
        # Determine confidence level (exactly like R's case_when logic)
        def get_confidence(row):
            max_ratio = row['Max_Ratio']
            if max_ratio > self.high_threshold:
                return 'High'
            elif max_ratio > self.medium_threshold:
                return 'Medium'
            else:
                return 'Low'
        
        data['Confidence'] = data.apply(get_confidence, axis=1)
        data['Composite_Class'] = data['Primary_Class'] + '_' + data['Confidence']
        
        # Calculate center position (exactly like R)
        data['Center'] = data.apply(
            lambda row: (row['Start'] + row['End']) / 2 if pd.notna(row['Start']) else np.nan, 
            axis=1
        )
        
        # Set chromosome order as factor (like in R)
        def chrom_sort_key(x):
            numbers = re.findall(r'\d+', x)
            letters = re.findall(r'[ABD]', x)
            num = int(numbers[0]) if numbers else float('inf')
            letter = letters[0] if letters else ''
            return (num, letter)
        
        chrom_order = sorted(data['Chromosome'].dropna().unique(), key=chrom_sort_key)
        data['Chromosome'] = pd.Categorical(data['Chromosome'], categories=chrom_order, ordered=True)
        
        return data
    
    def create_chromosome_facet_plot(self, data, confidence_description):
        """Exactly replicate R's chromosome facet plot"""
        class_counts = data.groupby(['Chromosome', 'Primary_Class']).size().reset_index(name='Count')
        
        # Get unique chromosomes
        chromosomes = sorted(data['Chromosome'].dropna().unique())
        
        # Set up color palette 
        colors = {
            'A': '#66c2a5', 
            'B': '#e78ac3', 
            'AB': '#fc8d62', 
            'NAB': '#a6d854', 
            'AXB': '#8da0cb'
        }
        
        classes = sorted(data['Primary_Class'].unique())
        
        color_dict = {}
        for cls in classes:
            if cls in colors:
                color_dict[cls] = colors[cls]
            else:
                color_dict[cls] = '#999999'
        
        # Create figure with subplots for each chromosome
        n_chromosomes = len(chromosomes)
        n_cols = min(4, n_chromosomes)
        n_rows = (n_chromosomes + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 3*n_rows))
        if n_rows == 1 and n_cols == 1:
            axes = np.array([axes])
        axes = axes.flatten()
        
        for idx, chrom in enumerate(chromosomes):
            if idx < len(axes):
                ax = axes[idx]
                chrom_data = class_counts[class_counts['Chromosome'] == chrom]
                
                # Create bars for each class
                bar_positions = np.arange(len(classes))
                for i, cls in enumerate(classes):
                    count = chrom_data[chrom_data['Primary_Class'] == cls]['Count'].values
                    height = count[0] if len(count) > 0 else 0
                    ax.bar(bar_positions[i], height, color=color_dict[cls], label=cls if idx == 0 else "")
                
                ax.set_xlabel(f'{chrom}')
                if idx % n_cols == 0:
                    ax.set_ylabel('Gene Count')
                ax.set_xticks(bar_positions)
                ax.set_xticklabels(classes, rotation=45)
                ax.grid(axis='y', alpha=0.3)
        
        # Hide empty subplots
        for idx in range(len(chromosomes), len(axes)):
            axes[idx].set_visible(False)
        
        plt.suptitle(f'Gene Classification Distribution by Chromosome ({confidence_description})', 
                    fontsize=16, y=0.98)
        plt.tight_layout(rect=[0, 0, 0.9, 0.95])
        
        return fig
    
    def create_physical_heatmap(self, data, confidence_description):
        """Exactly replicate R's physical heatmap"""
        # Filter valid data
        valid_data = data[data['Start'].notna()].copy()
        
        if valid_data.empty:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'No valid physical position data', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title(f'Gene Classification by Physical Position ({confidence_description})')
            return fig
        
        # Set up colors (exact Set2 colors from R)
        colors = {
            'A': '#66c2a5', 
            'B': '#e78ac3', 
            'AB': '#fc8d62', 
            'NAB': '#a6d854', 
            'AXB': '#8da0cb'
        }
        
        # Create figure
        chromosomes = sorted(valid_data['Chromosome'].unique())
        n_chromosomes = len(chromosomes)
        fig, axes = plt.subplots(n_chromosomes, 1, figsize=(20, 1 * n_chromosomes + 1))
        if n_chromosomes == 1:
            axes = [axes]
        
        for idx, chrom in enumerate(chromosomes):
            ax = axes[idx]
            chrom_data = valid_data[valid_data['Chromosome'] == chrom]
            
            y_pos = 0
            for _, gene in chrom_data.iterrows():
                color = colors.get(gene['Primary_Class'], '#999999')
                width = (gene['End'] - gene['Start']) / 1e6  # Convert to Mb
                start_mb = gene['Start'] / 1e6
                
                # Create rectangle for gene (exactly like R's geom_tile)
                rect = plt.Rectangle((start_mb, y_pos), width, 1, 
                                   facecolor=color, alpha=0.7, edgecolor='none')
                ax.add_patch(rect)
            
            ax.set_ylabel(f'Chr{chrom}')
            ax.set_xlim(0, valid_data['End'].max() / 1e6)
            ax.set_ylim(0, 1)
            ax.set_yticks([0.4])
            ax.set_yticklabels([f'Chr{chrom}'])
            ax.grid(axis='x', alpha=0.3)
            
            if idx == n_chromosomes - 1:
                ax.set_xlabel('Physical Position (Mb)')
        
        plt.suptitle(f'Gene Classification by Physical Position ({confidence_description})', 
                    fontsize=16, y=0.95)
        plt.tight_layout(rect=[0, 0, 0.95, 0.95])
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=color, label=cls) 
                         for cls, color in colors.items()]
        fig.legend(handles=legend_elements, loc='upper right', 
                  bbox_to_anchor=(0.98, 0.98))
        
        return fig
    
    def create_adjacent_gene_plot(self, data, confidence_description):
        """Exactly replicate R's adjacent gene region plot"""
        intervals_data = self.create_gene_intervals(data)
        
        if intervals_data.empty:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'No adjacent gene region data', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title(f'Adjacent Gene Region Classification ({confidence_description})')
            return fig
        
        # Filter out intergenic regions (exactly like R)
        gene_intervals = intervals_data[intervals_data['Primary_Class'] != 'Intergenic']
        
        if gene_intervals.empty:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'No gene region data', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title(f'Adjacent Gene Region Classification ({confidence_description})')
            return fig
        
        # Set up colors (exact Set2 colors from R)
        colors = {
            'A': '#66c2a5', 
            'B': '#e78ac3', 
            'AB': '#fc8d62', 
            'NAB': '#a6d854', 
            'AXB': '#8da0cb'
        }
        
        # Create figure
        chromosomes = sorted(gene_intervals['Chromosome'].unique())
        n_chromosomes = len(chromosomes)
        fig, axes = plt.subplots(n_chromosomes, 1, figsize=(20, 1 * n_chromosomes + 1))
        if n_chromosomes == 1:
            axes = [axes]
        
        for idx, chrom in enumerate(chromosomes):
            ax = axes[idx]
            chrom_data = gene_intervals[gene_intervals['Chromosome'] == chrom]
            
            y_pos = 0
            for _, interval in chrom_data.iterrows():
                color = colors.get(interval['Primary_Class'], '#999999')
                width = (interval['End'] - interval['Start']) / 1e6
                start_mb = interval['Start'] / 1e6
                
                rect = plt.Rectangle((start_mb, y_pos), width, 1,
                                   facecolor=color, alpha=0.7, edgecolor='none')
                ax.add_patch(rect)
            
            ax.set_ylabel(f'Chr{chrom}')
            ax.set_xlim(0, gene_intervals['End'].max() / 1e6)
            ax.set_ylim(0, 1)
            ax.set_yticks([0.4])
            ax.set_yticklabels([f'Chr{chrom}'])
            ax.grid(axis='x', alpha=0.3)
            
            if idx == n_chromosomes - 1:
                ax.set_xlabel('Physical Position (Mb)')
        
        plt.suptitle(f'Adjacent Gene Region Classification ({confidence_description})', 
                    fontsize=16, y=0.95)
        plt.tight_layout(rect=[0, 0, 1, 0.95])
                
                # Add legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=color, label=cls) 
                         for cls, color in colors.items()]
        fig.legend(handles=legend_elements, loc='upper right', 
                  bbox_to_anchor=(0.98, 0.98))
        
        return fig
    
    def create_score_ratio_plot(self, data, confidence_description):
        """Exactly replicate R's score ratio line plot"""
        # Prepare data for plotting (exactly like R's pivot_longer)
        plot_data = []
        for _, gene in data.iterrows():
            if pd.notna(gene['Center']):
                for score_type in ['A', 'B', 'AB', 'NAB', 'AXB']:
                    plot_data.append({
                        'Chromosome': gene['Chromosome'],
                        'Position_Mb': gene['Center'] / 1e6,
                        'Score_Type': score_type,
                        'Ratio': gene[f'{score_type}_ratio']
                    })
    
        if not plot_data:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'No valid position data for score ratios', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title(f'Gene Classification Score Ratio ({confidence_description})')
            return fig
    
        plot_df = pd.DataFrame(plot_data)
    
        # Set up colors and order (exactly matching R)
        colors = {
            'A': '#66c2a5', 
            'B': '#e78ac3', 
            'AB': '#fc8d62', 
            'NAB': '#a6d854', 
            'AXB': '#8da0cb'
        }
        score_order = ['A', 'AB', 'AXB', 'B', 'NAB']
    
        # Create figure with subplots for each chromosome
        chromosomes = sorted(plot_df['Chromosome'].unique())
        n_chromosomes = len(chromosomes)
    
        legend_elements = []
        for score_type in score_order:
            legend_elements.append(plt.Line2D([0], [0], color=colors[score_type], lw=2, label=score_type))
    
        if n_chromosomes == 0:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'No chromosome data for score ratios', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title(f'Gene Classification Score Ratio ({confidence_description})')
            return fig
    
        fig, axes = plt.subplots(n_chromosomes, 1, figsize=(20, 1 * n_chromosomes + 1))
    
        if n_chromosomes == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
    
        for idx, chrom in enumerate(chromosomes):
            ax = axes[idx]
            chrom_data = plot_df[plot_df['Chromosome'] == chrom].sort_values('Position_Mb')
        
            # Plot each score type (exactly like R)
            for score_type in score_order:
                score_data = chrom_data[chrom_data['Score_Type'] == score_type]
                if len(score_data) > 0:
                    ax.plot(score_data['Position_Mb'], score_data['Ratio'], 
                           color=colors[score_type], alpha=0.7, linewidth=1)
        
            ax.set_title(f'Chromosome {chrom}')
            ax.set_xlabel('Position (Mb)')
            ax.set_ylabel('Score Ratio')
            ax.set_ylim(0, 1)
            ax.grid(alpha=0.3)
    
        fig.legend(handles=legend_elements, 
                   loc='lower center', 
                   bbox_to_anchor=(0.5, 0.02),
                   ncol=5,
                   fontsize=10)
    
        plt.suptitle(f'Gene Classification Score Ratio ({confidence_description})', 
                fontsize=16, y=0.98)
    
        plt.tight_layout(rect=[0, 0.05, 1, 0.98])
    
        return fig
    
    def create_confidence_comparison(self, data, confidence_description):
        """Exactly replicate R's confidence comparison (pie charts)"""
        # Filter data for different confidence levels
        data_high = data[data['Confidence'] == 'High']
        data_medium_above = data[data['Confidence'].isin(['High', 'Medium'])]
        data_all = data
        
        colors = {
            'A': '#66c2a5', 
            'B': '#e78ac3', 
            'AB': '#fc8d62', 
            'NAB': '#a6d854', 
            'AXB': '#8da0cb'
        }
        
        datasets = [
            (data_high, f'High Confidence\n(> {self.high_threshold:.0%})'),
            (data_medium_above, f'Medium Confidence\n(> {self.medium_threshold:.0%})'),
            (data_all, 'All Confidence Levels')
        ]
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        for i, (dataset, title) in enumerate(datasets):
            ax = axes[i]
            if len(dataset) > 0:
                class_counts = dataset['Primary_Class'].value_counts()
                
                pie_colors = []
                for cls in class_counts.index:
                    if cls in colors:
                        pie_colors.append(colors[cls])
                    else:
                        pie_colors.append('#999999')
                
                wedges, texts, autotexts = ax.pie(class_counts.values, labels=class_counts.index, 
                                                autopct='%1.1f%%', colors=pie_colors, startangle=90)
                ax.set_title(title, fontsize=14, y=-0.15)
                
                # Improve text appearance
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
            else:
                ax.text(0.5, 0.5, 'No Data', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=12)
                ax.set_title(title, fontsize=14)
        
        plt.suptitle(f'Gene Classification by Confidence Level ({confidence_description})', 
                    fontsize=16, y=0.95)
        plt.tight_layout()
        
        return fig
    
    def generate_summary_statistics(self, data, data_with_position, data_high_only,
                                  data_medium_above, data_all_confidence):
        """Exactly replicate R's summary statistics format"""
        summary_lines = []
        
        summary_lines.append("GFF-based Gene Classification Statistical Summary:")
        summary_lines.append("==================================================")
        summary_lines.append(f"Total number of genes: {len(data)}")
        summary_lines.append(f"Genes successfully matched with physical positions: {len(data_with_position)}")
        summary_lines.append(f"Genes without physical position matches: {len(data) - len(data_with_position)}")
        
        if len(data_with_position) > 0:
            chromosomes = sorted(data_with_position['Chromosome'].dropna().unique())
            summary_lines.append(f"Chromosomes involved: {', '.join(chromosomes)}")
        
        summary_lines.append("\nGene counts by confidence level (High confidence threshold > 80%):")
        summary_lines.append("==============================================================")
        
        if len(data_with_position) > 0:
            confidence_counts = data_with_position['Confidence'].value_counts().sort_index()
            for conf, count in confidence_counts.items():
                percentage = (count / len(data_with_position)) * 100
                summary_lines.append(f"{conf}: {count} ({percentage:.1f}%)")
        else:
            summary_lines.append("No valid physical position data")
        
        summary_lines.append("\nCumulative confidence statistics (High confidence threshold > 80%):")
        summary_lines.append("===============================================================")
        summary_lines.append(f"High confidence gene count (threshold > 80%): {len(data_high_only)}")
        summary_lines.append(f"Medium and above confidence gene count: {len(data_medium_above)}")
        summary_lines.append(f"All confidence level gene count: {len(data_all_confidence)}")
        
        summary_lines.append("\nStatistics by primary classification (Mixed classification categorized as NAB):")
        summary_lines.append("==================================================================================")
        
        if len(data_with_position) > 0:
            class_counts = data_with_position['Primary_Class'].value_counts()
            for cls, count in class_counts.items():
                percentage = (count / len(data_with_position)) * 100
                summary_lines.append(f"{cls}: {count} ({percentage:.1f}%)")
        else:
            summary_lines.append("No valid physical position data")
        
        summary_lines.append("\nChromosome length statistics:")
        if len(data_with_position) > 0:
            for chrom in sorted(data_with_position['Chromosome'].dropna().unique()):
                if chrom in self.chromosome_lengths:
                    length_mb = self.chromosome_lengths[chrom] / 1e6
                    gene_count = len(data_with_position[data_with_position['Chromosome'] == chrom])
                    summary_lines.append(f"Chromosome {chrom}: Length {length_mb:.2f} Mb, Gene count {gene_count}")
        else:
            summary_lines.append("No valid physical position data")
        
        return '\n'.join(summary_lines)
    
    def create_combined_plots(self, data, confidence_level, confidence_description, output_dir):
        """Create all plots for a specific confidence level and combine them"""
        print(f"  Creating plots for {confidence_level}")
    
        if not self.visual:
            print(f"  Visualization disabled, skipping plot creation")
            return True
    
        # Create individual plots
        fig1 = self.create_chromosome_facet_plot(data, confidence_description)
        fig2 = self.create_physical_heatmap(data, confidence_description)
        fig3 = self.create_adjacent_gene_plot(data, confidence_description)
        fig4 = self.create_score_ratio_plot(data, confidence_description)
    
        if confidence_level == "All Confidence":
            fig5 = self.create_confidence_comparison(data, confidence_description)
            fig5.savefig(os.path.join(output_dir, 'confidence_pie.pdf'), 
                        bbox_inches='tight', dpi=300)
            plt.close(fig5)
    
        # Save individual plots
        plot_prefix = confidence_level.lower().replace(' ', '_')
    
        fig1.savefig(os.path.join(output_dir, f'chromosome_facet_{plot_prefix}.pdf'), 
                    bbox_inches='tight', dpi=300)
        fig2.savefig(os.path.join(output_dir, f'physical_heatmap_{plot_prefix}.pdf'), 
                bbox_inches='tight', dpi=300)
        fig3.savefig(os.path.join(output_dir, f'adjacent_gene_{plot_prefix}.pdf'), 
                    bbox_inches='tight', dpi=300)
        fig4.savefig(os.path.join(output_dir, f'score_ratio_{plot_prefix}.pdf'), 
                    bbox_inches='tight', dpi=300)
    
        plt.close('all')
    
        return True
    
    def run_analysis(self, stats_file, gff_file, output_dir, sample_name):
        """Main analysis function - exactly replicates R script functionality"""
        print(f"Starting comprehensive gene classification analysis for {sample_name}")
        print(f"Visualization enabled: {'Yes' if self.visual else 'No'}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Process data (exactly like R)
        data_processed = self.process_data(stats_file, gff_file)
        
        # Classify genes (exactly like R)
        data_classified = self.classify_genes(data_processed)
        
        # Filter data with positions (exactly like R)
        data_with_position = data_classified[data_classified['Start'].notna()].copy()
        
        # Check and resolve overlapping genes (exactly like R)
        data_with_position = self.check_and_resolve_overlaps(data_with_position)
        
        # Create confidence level datasets (exactly like R)
        data_high_only = data_with_position[data_with_position['Confidence'] == 'High']
        data_medium_above = data_with_position[data_with_position['Confidence'].isin(['High', 'Medium'])]
        data_all_confidence = data_with_position
        
        # Create plots for each confidence level (exactly like R)
        if self.visual:
            confidence_levels = [
                (data_high_only, "High Confidence", "Only high confidence genes (threshold > 80%)"),
                (data_medium_above, "Medium Confidence", "Contains medium and high confidence genes (threshold > 50%)"),
                (data_all_confidence, "All Confidence", "Contains all confidence genes (High+Medium+Low)")
            ]
            
            for data, level, description in confidence_levels:
                if not data.empty:
                    self.create_combined_plots(data, level, description, output_dir)
        
        # Generate summary statistics (exactly like R)
        summary_text = self.generate_summary_statistics(
            data_classified, data_with_position, data_high_only,
            data_medium_above, data_all_confidence
        )
        
        # Save summary to file
        with open(os.path.join(output_dir, 'analysis_summary.txt'), 'w', encoding='utf-8') as f:
            f.write(summary_text)
        
        # Save detailed data files (exactly like R)
        data_classified.to_csv(os.path.join(output_dir, 'gff_based_gene_classification.csv'), index=False)
        data_with_position.to_csv(os.path.join(output_dir, 'gff_based_gene_classification_with_position.csv'), index=False)
        
        # Save by confidence level (exactly like R)
        data_high_only.to_csv(os.path.join(output_dir, 'gff_based_gene_classification_high_only.csv'), index=False)
        data_medium_above.to_csv(os.path.join(output_dir, 'gff_based_gene_classification_medium_and_above.csv'), index=False)
        data_all_confidence.to_csv(os.path.join(output_dir, 'gff_based_gene_classification_all_confidence.csv'), index=False)
        
        # Save gene intervals data (exactly like R)
        intervals_high = self.create_gene_intervals(data_high_only)
        intervals_medium = self.create_gene_intervals(data_medium_above)
        intervals_all = self.create_gene_intervals(data_all_confidence)
        
        intervals_high.to_csv(os.path.join(output_dir, 'gene_intervals_high_confidence.csv'), index=False)
        intervals_medium.to_csv(os.path.join(output_dir, 'gene_intervals_medium_confidence.csv'), index=False)
        intervals_all.to_csv(os.path.join(output_dir, 'gene_intervals_all_confidence.csv'), index=False)
        
        # Print completion message (exactly like R)
        print(f"\nAnalysis completed! All results saved to: {output_dir}")
        if self.visual:
            print("Visualization charts have been generated and saved as PDF files.")
        else:
            print("Visualization was disabled. No plot files were generated.")
        print("Note: High confidence threshold is set to > 80%, Mixed classification is categorized as NAB.")
        print("Chromosome-faceted classification distribution charts and gene classification score ratio line charts use unfiltered data (all confidence levels).")
        print("Adjacent segments with the same classification are now merged into continuous segments, and overlapping gene issues have been resolved.")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='POAtools - Step 4: Exact R Replication Gene Classification Analysis')
    parser.add_argument('-i', '--input', required=True, help='Input gene stats file or directory (txt or csv)')
    parser.add_argument('-genome', required=True, help='Reference genome GFF file')
    parser.add_argument('-O', '--output', default='./r_style_visualization', help='Output directory')
    parser.add_argument('-High', type=float, default=0.8, help='High confidence threshold (default: 0.8)')
    parser.add_argument('-Medium', type=float, default=0.5, help='Medium confidence threshold (default: 0.5)')
    parser.add_argument('-Min', type=float, default=0.4, help='Minimum confidence threshold (default: 0.4)')
    parser.add_argument('-v', '--visual', default='T', help='Enable/disable visualization (T/F, default: T)')
    parser.add_argument('-batch', action='store_true', help='Batch process all files in input directory')
    
    args = parser.parse_args()
    
    # Process visualization parameter
    visual = True
    if args.visual.upper() == 'F':
        visual = False
    elif args.visual.upper() == 'T':
        visual = True
    else:
        print(f"Error: Invalid value for -v parameter. Use T or F.")
        sys.exit(1)
    
    # Check if input is a directory for batch processing
    if os.path.isdir(args.input) and args.batch:
        print(f"Batch processing mode: Processing all gene stats files in {args.input}")
        
        # Create main output directory
        os.makedirs(args.output, exist_ok=True)
        
        # Find all gene_stats_*.txt files
        gene_stats_files = []
        for root, dirs, files in os.walk(args.input):
            for file in files:
                if file.startswith('gene_stats_') and file.endswith('.txt'):
                    gene_stats_files.append(os.path.join(root, file))
        
        if not gene_stats_files:
            print(f"Error: No gene_stats_*.txt files found in {args.input}")
            sys.exit(1)
        
        print(f"Found {len(gene_stats_files)} sample files to process")
        
        # Process each file
        success_count = 0
        for stats_file in gene_stats_files:
            # Extract sample name from filename
            filename = os.path.basename(stats_file)
            if filename.startswith('gene_stats_'):
                sample_name = filename.replace('gene_stats_', '').replace('.txt', '').replace('.csv', '')
            else:
                sample_name = os.path.splitext(filename)[0]
            
            # Create sample-specific output directory
            sample_output_dir = os.path.join(args.output, sample_name)
            os.makedirs(sample_output_dir, exist_ok=True)
            
            print(f"\nProcessing sample: {sample_name}")
            print(f"  Input: {stats_file}")
            print(f"  Output: {sample_output_dir}")
            
            # Initialize analyzer
            analyzer = ExactRReplication(
                high_threshold=args.High,
                medium_threshold=args.Medium,
                min_threshold=args.Min,
                visual=visual
            )
            
            try:
                success = analyzer.run_analysis(stats_file, args.genome, sample_output_dir, sample_name)
                if success:
                    success_count += 1
                    print(f"  ? Completed: {sample_name}")
                else:
                    print(f"  ? Failed: {sample_name}")
            except Exception as e:
                print(f"  ? Error processing {sample_name}: {e}")
        
        # Generate batch summary
        print(f"\n{'='*60}")
        print("Batch Processing Summary")
        print(f"{'='*60}")
        print(f"Total files found: {len(gene_stats_files)}")
        print(f"Successfully processed: {success_count}")
        print(f"Failed: {len(gene_stats_files) - success_count}")
        print(f"Output directory: {args.output}")
        print(f"{'='*60}")
        
        # Create summary file
        with open(os.path.join(args.output, 'batch_processing_summary.txt'), 'w') as f:
            f.write("Batch Processing Summary\n")
            f.write("="*80 + "\n")
            f.write(f"Input directory: {args.input}\n")
            f.write(f"Total files found: {len(gene_stats_files)}\n")
            f.write(f"Successfully processed: {success_count}\n")
            f.write(f"Failed: {len(gene_stats_files) - success_count}\n")
            f.write(f"Genome file: {args.genome}\n")
            f.write(f"High threshold: {args.High}\n")
            f.write(f"Medium threshold: {args.Medium}\n")
            f.write(f"Min threshold: {args.Min}\n")
            f.write(f"Visualization: {'Enabled' if visual else 'Disabled'}\n\n")
            
            f.write("Individual sample outputs:\n")
            for sample_dir in sorted(os.listdir(args.output)):
                sample_path = os.path.join(args.output, sample_dir)
                if os.path.isdir(sample_path):
                    f.write(f"  - {sample_dir}: {sample_path}\n")
        
        return
    
    # Single file processing (original logic)
    # Validate inputs
    if not os.path.exists(args.input):
        print(f"Error: Input path does not exist: {args.input}")
        sys.exit(1)
    
    if not os.path.isfile(args.genome):
        print(f"Error: Genome file does not exist: {args.genome}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    print("POAtools - Step 4: Exact R Replication Gene Classification Analysis")
    print("=" * 60)
    print(f"Input file: {args.input}")
    print(f"Genome file: {args.genome}")
    print(f"High confidence threshold: {args.High}")
    print(f"Medium confidence threshold: {args.Medium}")
    print(f"Minimum confidence threshold: {args.Min}")
    print(f"Visualization: {'Enabled' if visual else 'Disabled'}")
    print(f"Output directory: {args.output}")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = ExactRReplication(
        high_threshold=args.High,
        medium_threshold=args.Medium,
        min_threshold=args.Min,
        visual=visual
    )
    
    # Extract sample name from filename
    filename = os.path.basename(args.input)
    if filename.startswith('gene_stats_'):
        sample_name = filename.replace('gene_stats_', '').replace('.txt', '').replace('.csv', '')
    else:
        sample_name = os.path.splitext(filename)[0]
    
    # Run analysis
    try:
        success = analyzer.run_analysis(args.input, args.genome, args.output, sample_name)
        if success:
            print("=" * 60)
            print("Step 4 completed successfully!")
            print(f"Results saved to: {args.output}")
        else:
            print("Step 4 failed!")
            sys.exit(1)
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()