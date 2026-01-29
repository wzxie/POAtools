#!/bin/bash
# POAtools Installation Script
# Version: 3.0.0
# Usage: ./install.sh

set -e

echo "=========================================="
echo "POAtools Installation"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}?${NC} $1"
}

info() {
    echo -e "${YELLOW}?${NC} $1"
}

error() {
    echo -e "${RED}?${NC} $1"
}

# Check if we're in the right directory
info "Checking for required files..."

REQUIRED_FILES=(
    "POAtools"
    "step1_snp_density.sh"
    "step2_gene_scoring.sh" 
    "step3_gene_statistics.sh"
    "step4_exact_r_replication.py"
    "check_python_deps.py"
)

missing_files=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        success "Found: $file"
    else
        error "Missing: $file"
        missing_files=1
    fi
done

if [ $missing_files -eq 1 ]; then
    echo ""
    error "Some required files are missing!"
    echo "Please make sure all POAtools files are in the current directory."
    echo "You can download them from: https://github.com/yourusername/poatools"
    exit 1
fi

# Set execution permissions
echo ""
info "Setting execution permissions..."
chmod +x POAtools step*.sh step4_exact_r_replication.py check_python_deps.py
success "Permissions set successfully"

# Create a convenience launcher
echo ""
info "Creating convenience launcher..."
cat > poatools_launcher << 'EOF'
#!/bin/bash
# POAtools Launcher
# Use this script to run POAtools from any location

# Get the directory where this launcher is located
LAUNCHER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$LAUNCHER_DIR"

# Run POAtools with all arguments
exec ./POAtools "$@"
EOF

chmod +x poatools_launcher
success "Launcher created: poatools_launcher"

# Create environment setup script
echo ""
info "Creating environment setup script..."
cat > setup_environment.sh << 'EOF'
#!/bin/bash
# Setup POAtools environment for current terminal

CURRENT_DIR="$(pwd)"
export PATH="$CURRENT_DIR:$PATH"

echo "Environment setup complete!"
echo "Current directory has been added to PATH: $CURRENT_DIR"
echo ""
echo "You can now use: poatools_launcher --help"
echo ""
echo "To make this permanent, add this line to your ~/.bashrc:"
echo "  export PATH=\"$CURRENT_DIR:\$PATH\""
EOF

chmod +x setup_environment.sh
success "Environment script created: setup_environment.sh"

# Create a usage guide
echo ""
info "Creating usage guide..."
cat > QUICK_START_GUIDE.txt << 'EOF'
POATOOLS QUICK START GUIDE
==========================

Installation successful! Here's how to use POAtools:

1. EASIEST: Run from current directory
   ./poatools_launcher --help
   ./poatools_launcher -i input.vcf -c parent1,parent2 -q samples.txt

2. SETUP CURRENT TERMINAL:
   source setup_environment.sh
   Then use: poatools_launcher --help

3. PERMANENT SETUP (add to ~/.bashrc):
   echo 'export PATH="'$(pwd)':$PATH"' >> ~/.bashrc
   source ~/.bashrc
   Then use: poatools_launcher --help

4. CHECK DEPENDENCIES:
   python3 check_python_deps.py

5. SAMPLE COMMAND:
   ./poatools_launcher -i demo.vcf.gz -c ZR48,ZR166 -q samples.txt -1 -2 -3 -4

FILE STRUCTURE:
  - POAtools                    # Main program
  - step1_snp_density.sh       # Step 1: SNP density analysis
  - step2_gene_scoring.sh      # Step 2: Gene classification scoring
  - step3_gene_statistics.sh   # Step 3: Gene statistics calculation
  - step4_exact_r_replication.py # Step 4: Visualization (R style)
  - poatools_launcher          # Convenience launcher
  - setup_environment.sh       # Environment setup script

OUTPUT:
  Output files will be saved in the 'output/' directory by default.

DEPENDENCIES:
  - Python 3.6+ with packages: pandas, numpy, matplotlib, seaborn
  - System tools: bcftools, gawk, tabix

TROUBLESHOOTING:
  - Run: python3 check_python_deps.py
  - Ensure all scripts have execute permissions: chmod +x *.sh *.py
  - Check system tools are installed: bcftools --version, awk --version

For detailed documentation, visit: https://github.com/yourusername/poatools

Happy analyzing!
EOF
success "Quick start guide created: QUICK_START_GUIDE.txt"

# Create a test script
echo ""
info "Creating test script..."
cat > test_installation.sh << 'EOF'
#!/bin/bash
# Test POAtools installation

echo "Testing POAtools installation..."
echo "================================"

# Test 1: Check if launcher works
echo -n "Test 1: Launcher executable... "
if [ -x "./poatools_launcher" ]; then
    echo "PASS"
else
    echo "FAIL"
    exit 1
fi

# Test 2: Check main script
echo -n "Test 2: Main script executable... "
if [ -x "./POAtools" ]; then
    echo "PASS"
else
    echo "FAIL"
    exit 1
fi

# Test 3: Run help command
echo -n "Test 3: Help command... "
if ./poatools_launcher --help 2>&1 | grep -q "POAtools"; then
    echo "PASS"
else
    echo "FAIL"
    exit 1
fi

# Test 4: Check Python dependencies
echo -n "Test 4: Python dependencies... "
if python3 check_python_deps.py 2>&1 | grep -q "All required"; then
    echo "PASS"
else
    echo "PARTIAL (some packages missing)"
    echo "  Run: python3 check_python_deps.py for details"
fi

echo "================================"
echo "All tests completed successfully!"
echo "POAtools is ready to use."
EOF

chmod +x test_installation.sh
success "Test script created: test_installation.sh"

# Check system dependencies
echo ""
info "Checking system dependencies..."

check_dependency() {
    if command -v $1 &> /dev/null; then
        success "$1: Found"
    else
        error "$1: Not found"
        return 1
    fi
}

echo "System tools:"
check_dependency "bcftools" || echo "  Install: sudo apt-get install bcftools"
check_dependency "awk" || echo "  Install: sudo apt-get install gawk"
check_dependency "python3" || echo "  Install: sudo apt-get install python3"
check_dependency "pip3" || echo "  Install: sudo apt-get install python3-pip"

echo ""
info "Checking Python packages..."
python3 check_python_deps.py

# Create directory for outputs
echo ""
info "Creating output directory..."
mkdir -p output
success "Output directory created: output/"

# Final message
echo ""
echo "=========================================="
success "POATOOLS INSTALLATION COMPLETE!"
echo "=========================================="
echo ""
echo "NEXT STEPS:"
echo "1. Read the quick start guide: cat QUICK_START_GUIDE.txt"
echo "2. Test installation: ./test_installation.sh"
echo "3. Setup environment: source setup_environment.sh"
echo "4. Start using POAtools: ./poatools_launcher --help"
echo ""
echo "IMPORTANT: All files remain in this directory."
echo "No system files were modified."
echo ""
echo "Need help? Visit: https://github.com/yourusername/poatools"
echo "=========================================="