#!/usr/bin/env bash
# One-step installation script for AtomSculptor
#
# Usage:
#   ./install.sh              # default: core + web extras
#   ./install.sh --all        # core + web + treesitter-full + dev
#   ./install.sh --dev        # core + web + dev extras
#   ./install.sh --no-venv    # skip venv creation (use current environment)

set -euo pipefail

INSTALL_ALL=false
INSTALL_DEV=false
SKIP_VENV=false

for arg in "$@"; do
    case "$arg" in
        --all)      INSTALL_ALL=true ;;
        --dev)      INSTALL_DEV=true ;;
        --no-venv)  SKIP_VENV=true ;;
        -h|--help)
            echo "Usage: ./install.sh [--all] [--dev] [--no-venv]"
            echo "  --all      Install all optional extras (web, dev, treesitter-full)"
            echo "  --dev      Include development dependencies"
            echo "  --no-venv  Skip virtual environment creation"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg (try --help)"
            exit 1
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  AtomSculptor Installation"
echo "=========================================="

# ── 1. Check Python ──────────────────────────────────────────────────────────
echo ""
echo "[1/5] Checking Python..."
if ! command -v python3 > /dev/null 2>&1; then
    echo "ERROR: python3 not found in PATH"
    exit 1
fi
PYTHON_BIN=$(command -v python3)
PYTHON_VERSION=$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.12"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "ERROR: Python >= $REQUIRED_VERSION required (found $PYTHON_VERSION)"
    exit 1
fi
echo "  ✓ Python $PYTHON_VERSION"

# ── 2. Virtual environment ───────────────────────────────────────────────────
echo ""
echo "[2/5] Setting up virtual environment..."
if [ "$SKIP_VENV" = true ]; then
    echo "  Skipped (--no-venv)"
    PIP_BIN="$PYTHON_BIN -m pip"
else
    if [ ! -d .venv ]; then
        "$PYTHON_BIN" -m venv .venv
        echo "  ✓ Created .venv"
    else
        echo "  ✓ .venv already exists"
    fi
    # shellcheck disable=SC1091
    source .venv/bin/activate
    PIP_BIN="pip"
fi

# ── 3. Python dependencies ───────────────────────────────────────────────────
echo ""
echo "[3/5] Installing Python dependencies..."
if [ "$INSTALL_ALL" = true ]; then
    $PIP_BIN install -e ".[web,dev,treesitter-full]"
elif [ "$INSTALL_DEV" = true ]; then
    $PIP_BIN install -e ".[web,dev]"
else
    $PIP_BIN install -e ".[web]"
fi
echo "  ✓ Python packages installed"

# ── 4. Frontend dependencies ─────────────────────────────────────────────────
echo ""
echo "[4/5] Installing frontend dependencies..."
if command -v npm > /dev/null 2>&1; then
    (cd web_gui/static && npm ci --silent 2>/dev/null || npm install --silent)
    echo "  ✓ npm packages installed"
else
    echo "  ⚠  npm not found – skipping frontend install"
    echo "     Install Node.js 18+ and run: cd web_gui/static && npm ci"
fi

# ── 5. Environment file ──────────────────────────────────────────────────────
echo ""
echo "[5/5] Checking .env..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "  ✓ Created .env from .env.example"
        echo "  ⚠  Edit .env and add your API keys"
    else
        echo "  ⚠  No .env.example found – create .env manually"
    fi
else
    echo "  ✓ .env already exists"
fi

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "=========================================="
echo "  ✓ Installation complete!"
echo "=========================================="
echo ""
echo "Quick start:"
if [ "$SKIP_VENV" = false ]; then
    echo "  source .venv/bin/activate"
fi
echo "  python main.py --web          # web GUI on http://localhost:8000"
echo "  python main.py                # ADK CLI mode"
echo ""
echo "Optional: start Memgraph for code-graph-rag features:"
echo "  docker compose up -d"
echo ""
