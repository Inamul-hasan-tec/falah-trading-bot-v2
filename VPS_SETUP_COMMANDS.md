# 🚀 VPS Setup Commands - Copy & Paste

## Step 1: On VPS - Install Requirements

```bash
# You're already here, now install packages
pip install -r requirements-vps.txt
```

**If that fails, install core packages only:**

```bash
pip install kiteconnect pandas numpy python-dotenv pyyaml requests ta
```

---

## Step 2: Test Installation

```bash
# Test imports
python3 -c "import pandas; import numpy; from kiteconnect import KiteConnect; print('✅ Core packages working!')"

# Test config
python3 -c "import yaml; print(yaml.safe_load(open('config/config.yaml')))"

# Test .env
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key loaded:', os.getenv('KITE_API_KEY')[:10] + '...')"
```

---

## Step 3: Create Run Script

```bash
# Create run script
cat > run_v2.sh << 'EOF'
#!/bin/bash
cd /root/trading-bots/falah-trading-bot-v2
source venv/bin/activate
python3 main.py --mode paper
EOF

# Make executable
chmod +x run_v2.sh
```

---

## Step 4: Test Run

```bash
# Test in foreground first
./run_v2.sh
```

**Press Ctrl+C to stop**

---

## Step 5: Run in Background (Production)

```bash
# Install screen
apt install screen -y

# Start in screen session
screen -S trading-v2
./run_v2.sh

# Detach: Press Ctrl+A then D
```

---

## Management Commands

```bash
# View running screens
screen -ls

# Attach to bot
screen -r trading-v2

# Kill bot
screen -X -S trading-v2 quit

# View logs
tail -f logs/trading.log
```

---

## Quick Troubleshooting

**If pandas import fails:**
```bash
pip install --upgrade pandas==2.0.3 numpy==1.24.3
```

**If kiteconnect fails:**
```bash
pip install --upgrade kiteconnect
```

**If config not found:**
```bash
ls -la config/
cat config/config.yaml
```

**If .env not found:**
```bash
ls -la .env
cat .env
```
