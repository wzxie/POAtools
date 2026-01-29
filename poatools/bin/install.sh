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
BLUE='\033[0;34m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✓${NC} $1"
}

info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

note() {
    echo -e "${BLUE}ℹ${NC} $1"
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

# Create a convenience launcher (for current directory usage)
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

# Create global accessible POAtools command
echo ""
info "Creating global POAtools command..."

# Get current directory absolute path
CURRENT_DIR="$(pwd)"
POATOOLS_PATH="$CURRENT_DIR/POAtools"

# Ensure that~/. local/bin exists and is in PATH
USER_BIN="$HOME/.local/bin"
echo ""
info "Setting up user bin directory: $USER_BIN"

# Create directory
mkdir -p "$USER_BIN"

#Add to the PATH of the current shell
if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
    export PATH="$USER_BIN:$PATH"
    success "Added $USER_BIN to current shell PATH"
fi

# Check and update the user's environment configuration file
ENV_FILES=("$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile")
PATH_ADDED=0

for env_file in "${ENV_FILES[@]}"; do
    if [ -f "$env_file" ]; then
        if ! grep -q "\.local/bin" "$env_file" 2>/dev/null; then
            echo "" >> "$env_file"
            echo "# Added by POAtools installer" >> "$env_file"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$env_file"
            info "Added ~/.local/bin to $env_file"
            PATH_ADDED=1
        else
            info "~/.local/bin already in $env_file"
        fi
    fi
done

# If none have been added, create. bashrc
if [ $PATH_ADDED -eq 0 ] && [ ! -f "$HOME/.bashrc" ]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' > "$HOME/.bashrc"
    info "Created ~/.bashrc with PATH setting"
fi

# Create symbolic link
echo ""
info "Creating symlink to POAtools..."
if [ -f "$USER_BIN/POAtools" ]; then
    rm -f "$USER_BIN/POAtools"
    info "Removed existing symlink"
fi

ln -sf "$CURRENT_DIR/POAtools" "$USER_BIN/POAtools"
success "Created symlink: $USER_BIN/POAtools"

# Immediately test if the command is available
echo ""
info "Testing POAtools command..."
if command -v POAtools &>/dev/null; then
    success "POAtools command is now available!"
    echo "You can use: POAtools --help"
else
    error "POAtools command not found in PATH. Trying alternative setup..."
    
    # Create a directly usable wrapper script
    cat > "$USER_BIN/poatools" << 'EOF'
#!/bin/bash
# POAtools wrapper
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"$DIR/POAtools" "$@"
EOF
    
    chmod +x "$USER_BIN/poatools"
    ln -sf "$CURRENT_DIR/POAtools" "$USER_BIN/POAtools" 2>/dev/null || true
    
    # Try again
    if command -v POAtools &>/dev/null; then
        success "POAtools command is now available!"
    else
        echo ""
        error "Manual setup required."
        echo "Please add this line to your shell profile:"
        echo "  alias POAtools='$CURRENT_DIR/POAtools'"
    fi
fi

# Intelligent installation of Python dependencies
echo ""
info "Checking and installing Python dependencies..."

install_python_deps() {
    echo ""
    info "Checking and installing Python dependencies..."
    
    # Detection Package Manager
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        error "No pip found. Please install pip first."
        echo "  Debian/Ubuntu: sudo apt-get install python3-pip"
        echo "  RedHat/CentOS: sudo yum install python3-pip"
        return 1
    fi
    
    # Check the compiler
    if ! command -v g++ &> /dev/null; then
        echo ""
        note "C++ compiler (g++) not found!"
        echo "This may cause issues when installing pandas from source."
        echo "We will try pre-compiled packages first."
        echo ""
        COMPILER_AVAILABLE=0
    else
        success "C++ compiler found: $(g++ --version | head -1)"
        COMPILER_AVAILABLE=1
    fi
    
    # Installation strategy: First try 'prefer basic', if not, try specifying a version
    install_package() {
        local pkg=$1
        local version=$2
        
        echo ""
        info "Installing $pkg..."
        
        if python3 -c "import $pkg" 2>/dev/null; then
            local ver=$(python3 -c "import $pkg; print($pkg.__version__)" 2>/dev/null || echo "")
            success "$pkg is already installed${ver:+ (v$ver)}"
            return 0
        fi
        
        # Try multiple installation strategies
        local strategies=()
        
        if [ "$pkg" = "pandas" ]; then
            strategies=(
                "--prefer-binary $pkg"
                "$pkg==1.5.3"
                "$pkg==1.4.4"
                "$pkg"
            )
        elif [ "$pkg" = "seaborn" ]; then
            strategies=(
                "--prefer-binary $pkg"
                "$pkg==0.12.2"
                "$pkg==0.11.2"
                "$pkg"
            )
        else
            strategies=(
                "--prefer-binary $pkg"
                "$pkg"
            )
        fi
        
        for strategy in "${strategies[@]}"; do
            info "  Trying: $PIP_CMD install --user $strategy"
            if $PIP_CMD install --user $strategy 2>&1 | tee /tmp/install.log; then
                if python3 -c "import $pkg" 2>/dev/null; then
                    local ver=$(python3 -c "import $pkg; print($pkg.__version__)" 2>/dev/null || echo "")
                    success "$pkg installed successfully${ver:+ (v$ver)}"
                    return 0
                fi
            fi
            sleep 1
        done
        
        error "Failed to install $pkg"
        return 1
    }
    
    # Install the core package
    local failed_packages=()
    
    for pkg in numpy matplotlib pandas seaborn; do
        if ! install_package "$pkg"; then
            failed_packages+=("$pkg")
        fi
    done
    
    echo ""
    if [ ${#failed_packages[@]} -eq 0 ]; then
        success "All Python dependencies installed successfully!"
    else
        error "Failed to install: ${failed_packages[*]}"
        echo ""
        echo "Possible solutions:"
        echo "  1. Install system compiler:"
        echo "     sudo yum install gcc-c++ python3-devel"
        echo "     or"
        echo "     sudo apt-get install g++ python3-dev"
        echo ""
        echo "  2. Try installing manually:"
        echo "     $PIP_CMD install --prefer-binary ${failed_packages[*]}"
        echo ""
        echo "  3. Use conda (if available):"
        echo "     conda install ${failed_packages[*]}"
        echo ""
        echo "  4. Install older versions:"
        echo "     $PIP_CMD install pandas==1.5.3 seaborn==0.12.2"
    fi
    
    return ${#failed_packages[@]}
}

# Run Python dependency installation
install_python_deps || true

# Create environment setup script
echo ""
info "Creating environment setup script..."
cat > setup_environment.sh << EOF
#!/bin/bash
# Setup POAtools environment for current terminal

CURRENT_DIR="$CURRENT_DIR"
USER_BIN="\$HOME/.local/bin"

# Add both current directory and user bin to PATH
export PATH="\$CURRENT_DIR:\$USER_BIN:\$PATH"

# Create user bin directory if it doesn't exist
mkdir -p "\$USER_BIN"

# Create or update symlink
if [ -f "\$USER_BIN/POAtools" ]; then
    rm -f "\$USER_BIN/POAtools"
fi
ln -sf "\$CURRENT_DIR/POAtools" "\$USER_BIN/POAtools"

echo "Environment setup complete!"
echo "Added to PATH: \$CURRENT_DIR and \$USER_BIN"
echo ""
echo "You can now use: POAtools --help"
echo ""
echo "To make this permanent, add these lines to your ~/.bashrc:"
echo "  export PATH=\"\\\$HOME/.local/bin:\\\$PATH\""
echo "  alias POAtools='$CURRENT_DIR/POAtools'"
EOF

chmod +x setup_environment.sh
success "Environment script created: setup_environment.sh"

# Create alias setup script
echo ""
info "Creating alias setup script..."
cat > setup_alias.sh << EOF
#!/bin/bash
# Setup POAtools alias for easier access

CURRENT_DIR="$CURRENT_DIR"
SHELL_RC=""

# Detect shell and determine RC file
if [[ "\$SHELL" == *"zsh"* ]]; then
    SHELL_RC="\$HOME/.zshrc"
elif [[ "\$SHELL" == *"bash"* ]]; then
    if [ -f "\$HOME/.bashrc" ]; then
        SHELL_RC="\$HOME/.bashrc"
    elif [ -f "\$HOME/.bash_profile" ]; then
        SHELL_RC="\$HOME/.bash_profile"
    fi
fi

if [ -z "\$SHELL_RC" ] || [ ! -f "\$SHELL_RC" ]; then
    echo "Could not detect your shell RC file. Please manually add the following alias:"
    echo "  alias POAtools='$CURRENT_DIR/POAtools'"
    exit 1
fi

# Check if alias already exists
if grep -q "alias POAtools=" "\$SHELL_RC"; then
    echo "POAtools alias already exists in \$SHELL_RC"
    echo "Updating to current directory..."
    # Remove existing alias line
    sed -i.bak '/alias POAtools=/d' "\$SHELL_RC"
fi

# Add alias
echo "" >> "\$SHELL_RC"
echo "# POAtools alias" >> "\$SHELL_RC"
echo "alias POAtools='$CURRENT_DIR/POAtools'" >> "\$SHELL_RC"
echo "" >> "\$SHELL_RC"

echo "Alias added to \$SHELL_RC"
echo "Please restart your terminal or run: source \$SHELL_RC"
echo "Then you can use: POAtools --help"
EOF

chmod +x setup_alias.sh
success "Alias setup script created: setup_alias.sh"

# Create Python dependency repair script
echo ""
info "Creating Python dependency fix script..."
cat > fix_python_deps.sh << 'EOF'
#!/bin/bash
# Fix Python dependencies without compiler

echo "========================================"
echo "Python Dependency Fix Script"
echo "========================================"
echo ""
echo "This script will help install Python dependencies without requiring"
echo "a C++ compiler. We will try multiple strategies."
echo ""

# Detection Package Manager
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "ERROR: No pip found. Please install pip first."
    echo "  Debian/Ubuntu: sudo apt-get install python3-pip"
    echo "  RedHat/CentOS: sudo yum install python3-pip"
    exit 1
fi

echo "Using pip command: $PIP_CMD"
echo ""

# Try different versions of installation strategies
PACKAGES=("numpy" "matplotlib" "pandas" "seaborn")
SUCCESS=()
FAILED=()

for pkg in "${PACKAGES[@]}"; do
    echo "Installing $pkg..."
    
    # Check if it has been installed
    if python3 -c "import $pkg" 2>/dev/null; then
        echo "  ✓ $pkg is already installed"
        SUCCESS+=("$pkg")
        continue
    fi
    
    # 尝试不同策略
    STRATEGIES=()
    if [ "$pkg" = "pandas" ]; then
        STRATEGIES=(
            "--prefer-binary --no-cache-dir pandas==1.5.3"
            "--prefer-binary --no-cache-dir pandas==1.4.4"
            "--prefer-binary --no-cache-dir pandas==1.3.5"
            "--prefer-binary pandas"
            "pandas==1.5.3"
        )
    elif [ "$pkg" = "seaborn" ]; then
        STRATEGIES=(
            "--prefer-binary --no-cache-dir seaborn==0.12.2"
            "--prefer-binary --no-cache-dir seaborn==0.11.2"
            "--prefer-binary seaborn"
            "seaborn==0.12.2"
        )
    else
        STRATEGIES=(
            "--prefer-binary --no-cache-dir $pkg"
            "--prefer-binary $pkg"
            "$pkg"
        )
    fi
    
    INSTALLED=0
    for strategy in "${STRATEGIES[@]}"; do
        echo "  Trying: $PIP_CMD install --user $strategy"
        if timeout 300 $PIP_CMD install --user $strategy 2>&1 | grep -q "Successfully installed\|Requirement already satisfied"; then
            # Verify installation
            if python3 -c "import $pkg" 2>/dev/null; then
                echo "  ✓ $pkg installed successfully"
                SUCCESS+=("$pkg")
                INSTALLED=1
                break
            fi
        fi
        sleep 2
    done
    
    if [ $INSTALLED -eq 0 ]; then
        echo "  ✗ Failed to install $pkg"
        FAILED+=("$pkg")
    fi
done

echo ""
echo "========================================"
echo "RESULTS"
echo "========================================"
echo "Successfully installed: ${SUCCESS[*]}"
echo "Failed to install: ${FAILED[*]}"
echo ""

if [ ${#FAILED[@]} -gt 0 ]; then
    echo "TROUBLESHOOTING:"
    echo ""
    
    if [ "$(uname)" = "Linux" ]; then
        echo "1. Try installing system packages first:"
        if command -v yum &> /dev/null; then
            echo "   sudo yum install python3-devel gcc-c++"
        elif command -v apt-get &> /dev/null; then
            echo "   sudo apt-get install python3-dev g++"
        fi
        echo ""
    fi
    
    echo "2. Try using conda (if available):"
    echo "   conda install ${FAILED[*]}"
    echo ""
    
    echo "3. Try creating a virtual environment:"
    echo "   python3 -m venv poatools_venv"
    echo "   source poatools_venv/bin/activate"
    echo "   pip install ${FAILED[*]}"
    echo ""
    
    echo "4. Some packages may not be critical. You can still try POAtools."
fi

echo ""
echo "Test the installation:"
echo "  python3 -c \"import pandas; import seaborn; print('All packages imported successfully')\""
echo ""
EOF

chmod +x fix_python_deps.sh
success "Python dependency fix script created: fix_python_deps.sh"

# Create a usage guide
echo ""
info "Creating usage guide..."
cat > QUICK_START_GUIDE.txt << EOF
POATOOLS QUICK START GUIDE
==========================

Installation successful! Here's how to use POAtools:

1. QUICKEST (already set up):
   POAtools --help
   POAtools -i input.vcf -c parent1,parent2 -q samples.txt

2. USING ALIAS (if you move the directory):
   ./setup_alias.sh
   # Then restart terminal or: source ~/.bashrc
   POAtools --help

3. SETUP CURRENT TERMINAL:
   source setup_environment.sh
   Then use: POAtools --help

4. FIX PYTHON DEPENDENCIES (if needed):
   ./fix_python_deps.sh
   # This will try multiple strategies to install dependencies

5. CHECK DEPENDENCIES:
   python3 check_python_deps.py

6. SAMPLE COMMAND:
   POAtools -i demo.vcf.gz -c ZR48,ZR166 -q samples.txt -1 -2 -3 -4

LOCATION:
  - Main program: $CURRENT_DIR/POAtools
  - Symlink: ~/.local/bin/POAtools

FILE STRUCTURE:
  - POAtools                    # Main program
  - step1_snp_density.sh       # Step 1: SNP density analysis
  - step2_gene_scoring.sh      # Step 2: Gene classification scoring
  - step3_gene_statistics.sh   # Step 3: Gene statistics calculation
  - step4_exact_r_replication.py # Step 4: Visualization (R style)
  - poatools_launcher          # Convenience launcher (for current dir)
  - setup_environment.sh       # Environment setup script
  - setup_alias.sh             # Alias setup script
  - fix_python_deps.sh         # Python dependency fix script

OUTPUT:
  Output files will be saved in the 'output/' directory by default.

DEPENDENCIES:
  - Python 3.6+ with packages: pandas, numpy, matplotlib, seaborn
  - System tools: bcftools, gawk, tabix

TROUBLESHOOTING:
  - If 'POAtools' command not found, run: source setup_environment.sh
  - Or set up alias: ./setup_alias.sh
  - For Python dependency issues: ./fix_python_deps.sh
  - Run: python3 check_python_deps.py
  - Check system tools: bcftools --version, awk --version

PYTHON DEPENDENCY FIX OPTIONS:
  1. Run: ./fix_python_deps.sh
  2. Install system packages: sudo yum install gcc-c++ python3-devel
  3. Use conda: conda install pandas seaborn numpy matplotlib
  4. Try older versions: pip3 install pandas==1.5.3 seaborn==0.12.2

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

# Test 1: Check if POAtools command works
echo -n "Test 1: POAtools command... "
if command -v POAtools &> /dev/null; then
    echo "PASS"
    POATOOLS_CMD="POAtools"
else
    echo "FAIL (trying local version)"
    if [ -x "./POAtools" ]; then
        POATOOLS_CMD="./POAtools"
        echo "  Using local ./POAtools"
    else
        echo "  ERROR: No POAtools found"
        exit 1
    fi
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
if $POATOOLS_CMD --help 2>&1 | grep -q "POAtools"; then
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
    echo "  Or try: ./fix_python_deps.sh"
fi

echo "================================"
echo "Installation test completed!"
echo ""
echo "If Test 1 failed, run: source setup_environment.sh"
echo "If Test 4 failed, run: ./fix_python_deps.sh"
echo ""
echo "Then try: POAtools --help"
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
check_dependency "bcftools" || echo "  Install: sudo apt-get install bcftools  OR  sudo yum install bcftools"
check_dependency "awk" || echo "  Install: sudo apt-get install gawk  OR  sudo yum install gawk"
check_dependency "python3" || echo "  Install: sudo apt-get install python3  OR  sudo yum install python3"
check_dependency "pip3" || echo "  Install: sudo apt-get install python3-pip  OR  sudo yum install python3-pip"

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
echo "SUMMARY:"
echo "  ✓ POAtools command is available: POAtools --help"
echo "  ✓ User bin directory: ~/.local/bin added to PATH"
echo "  ✓ Python dependencies installation attempted"
echo ""
echo "NEXT STEPS:"
echo "1. Test the installation: ./test_installation.sh"
echo "2. Try the command: POAtools --help"
echo "3. If Python dependencies missing: ./fix_python_deps.sh"
echo "4. For permanent access: ./setup_alias.sh"
echo ""
echo "QUICK START:"
echo "  POAtools --help                        # Show help"
echo "  POAtools -i input.vcf -c parent1,parent2  # Run analysis"
echo ""
echo "PYTHON DEPENDENCY NOTES:"
echo "  If pandas/seaborn installation failed, try:"
echo "  - ./fix_python_deps.sh (recommended)"
echo "  - sudo yum install gcc-c++ python3-devel (if you have sudo)"
echo "  - pip3 install pandas==1.5.3 seaborn==0.12.2 (manual install)"
echo ""
echo "LOCATION:"
echo "  Main program: $(pwd)/POAtools"
echo "  Symlink: ~/.local/bin/POAtools"
echo ""
echo "Need help? Visit: https://github.com/yourusername/poatools"
echo "=========================================="