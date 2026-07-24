# ============================================================
# StrategyOpt Environment Setup Script
# ============================================================

$ErrorActionPreference = "Stop"  # Exit on any unhandled error
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPath = Join-Path $ProjectRoot ".venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
$PipExe = Join-Path $VenvPath "Scripts\pip.exe"

# ============================================================
# Helper: print a section header so output is easy to read
# ============================================================
function Write-Header($text) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host " $text" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
}

# ============================================================
# STEP 1: Verify Python is available and is a suitable version
# ============================================================
Write-Header "Checking Python installation"


#Check for local python on PATH
$pyCmd = Get-Command python -ErrorAction SilentlyContinue

if (-not $pyCmd) {
    Write-Host "ERROR: Python not found on PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/downloads/"
    Write-Host "Make sure to check 'Add Python to PATH' during installation."
    exit 1
}

try{
# Parse the version number so we can check it programmatically
$VersionOutput = & python --version 2>&1
# Output looks like "Python 3.13.0" - split on space and dot to get components
$VersionString = $VersionOutput -replace "Python ", ""
$VersionParts = $VersionString.Split(".")
$Major = [int]$VersionParts[0]
$Minor = [int]$VersionParts[1]
}
catch{
    Write-Host "ERROR: Could not parse Python version." -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/downloads/"
    exit 1
}

Write-Host "Found: $VersionOutput"

if ($Major -lt 3 -or ($Major -eq 3 -and $Minor -lt 11)) {
    Write-Host "ERROR: Python 3.11 or higher is required." -ForegroundColor Red
    Write-Host "Found: $VersionOutput"
    exit 1
}

Write-Host "Python version OK." -ForegroundColor Green

# ============================================================
# STEP 2: Create virtual environment if it doesn't exist
# ============================================================
Write-Header "Setting up virtual environment"

if (Test-Path $VenvPath) {
    Write-Host "Existing .venv found, skipping creation." -ForegroundColor Yellow
} else {
    Write-Host "Creating .venv..."
    & python -m venv $VenvPath
    Write-Host "Virtual environment created." -ForegroundColor Green
}

# ============================================================
# STEP 3: Upgrade pip
# ============================================================
Write-Header "Upgrading pip"
& $PipExe install --upgrade pip --quiet
Write-Host "pip up to date." -ForegroundColor Green

# ============================================================
# STEP 4: Detect GPU and select the right PyTorch build
# ============================================================
Write-Header "Detecting GPU capabilities"

$TorchIndexUrl = $null      # null means use default PyPI (CPU build)
$TorchExtras = ""           # label for display purposes
$CudaVersion = $null

$NVIDIAsmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue

if ($NVIDIAsmi){
    Write-Host "NVIDIA GPU found, querying GPU..."

    $SMIoutput = & nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
    $CUDAline = & nvidia-smi 2>&1 | Select-String "CUDA Version"

    if ($CUDAline) {
        $CUDAmatch = $CUDAline -match "CUDA Version:\s*([\d\.]+)"
        if ($CUDAmatch) {
            $CudaVersion = [version]$Matches[1]
            Write-Host "Detected CUDA Version: $CudaVersion" -ForegroundColor Green
            Write-Host "GPU: $SmiOutput"

        # Choses the newest PyTorch CUDA build that fits under the driver ceiling
        if ($CUDAVersion -ge [version]"12.4"){
            $TorchIndexUrl = "https://download.pytorch.org/whl/cu124"
            $TorchExtras = "CUDA 12.4"
        } elseif ($CUDAVersion -ge [version]"11.8") {
            $TorchIndexUrl = "https://download.pytorch.org/whl/cu118"
            $TorchExtras = "CUDA 11.8"
        } else {
                 Write-Host "CUDA version too old for modern PyTorch CUDA builds." -ForegroundColor Yellow
                Write-Host "Falling back to CPU-only PyTorch."
                $TorchExtras = "CPU (CUDA too old)"
            }
        }
                
    } else {
            Write-Host "nvidia-smi found but couldn't parse CUDA version." -ForegroundColor Yellow
            Write-Host "Falling back to CPU-only PyTorch."
            $TorchExtras = "CPU (parse failed)"
        }
} else {
    Write-Host "nvidia-smi not found - no NVIDIA GPU detected." -ForegroundColor Yellow
    Write-Host "Installing CPU-only PyTorch."
    $TorchExtras = "CPU"

}
Write-Host "PyTorch build selected: $TorchExtras" -ForegroundColor Cyan

# ============================================================
# STEP 5: Install PyTorch first, separately, pinned
# ============================================================
Write-Header "Installing PyTorch ($TorchExtras)"

if ($TorchIndexUrl) {
    & $PipExe install torch torchvision torchaudio --index-url $TorchIndexUrl
} else{
    & $PipExe install torch torchvision torchaudio
}

if($TorchIndexUrl) {
    Write-Host "Verifying CUDA availability..."
    $CUDACheck = & $PythonExe -c "import torch; print(torch.cuda.is_available())"
    if ($CUDACheck -eq "True") {
        $DeviceName = & $PythonExe -c "import torch; print(torch.cuda.get_device_name(0))"
        Write-Host "CUDA confirmed: $DeviceName" -ForegroundColor Green
    } else {
        Write-Host "WARNING: CUDA build installed but torch.cuda.is_available returned False." -ForegroundColor Red
        Write-Host "This may indicate a driver/toolkit mismatch. The script will continue to run but GPU accleration may not work."
    }
}

# ============================================================
# STEP 5: Install remaining packages
# Constrain torch so pip does not overwrite
# ============================================================
Write-Header "Installing remaining packages"

$ConstraintsPath = Join-Path $ProjectRoot "torch-constraints.txt"
$TorchInstall = & $PipExe show torch | Select-String "^Version"
$TorchVersion = ($TorchInstall -split ": ")[1].Trim()
"torch==$TorchVersion" | Out-File -FilePath $ConstraintsPath -Encoding utf8

Write-Host "Locking torch at $TorchVersion to prevent pip overwriting CUDA build..."

& $PipExe install `
numpy pandas matplotlib scipy `
simpy gymnasium stable-baselines3 `
requests beautifulsoup4 lxml truststore `
--constraint $ConstraintsPath

Remove-Item $ConstraintsPath

# ============================================================
# STEP 7: Verify the environment
# ============================================================
Write-Header "Verifying environment"
& $PythonExe "$ProjectRoot\verifyPython.py"

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "To activate the environment in your terminal, run:"
Write-Host "    .venv\Scripts\activate" -ForegroundColor Cyan