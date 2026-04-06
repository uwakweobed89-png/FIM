# File Integrity Monitor (FIM)

## 🎓 Educational Security Tool

Learn how file integrity monitoring works through hands-on practice!
Detect unauthorized file changes by comparing cryptographic hashes.

---

## 🔐 What is File Integrity Monitoring?

### The Concept
File Integrity Monitoring (FIM) is a security control that:
1. **Takes a "snapshot"** of files using cryptographic hashes
2. **Compares current state** to the baseline regularly
3. **Alerts when changes occur** that weren't authorized

### Real-World Use Cases
- **System files**: Detect malware modifications
- **Configuration files**: Catch unauthorized changes
- **Web servers**: Detect website defacement  
- **Compliance**: Required by PCI-DSS, HIPAA, SOX
- **Forensics**: Know exactly when files changed

### How It Works (Simple Explanation)
```
Step 1: Baseline Creation
File: important.txt → Hash: abc123def456

Step 2: Monitoring
File: important.txt → Hash: abc123def456 ✅ NO CHANGE

Step 3: Detection
Someone modifies important.txt!
File: important.txt → Hash: xyz789ghi012 🚨 ALERT!
```

---

## 🎯 Practice vs Active Modes

### Practice Mode (SAFE - Start Here!)
- ✅ Creates test files automatically
- ✅ Simulates file modifications
- ✅ Safe to experiment and learn
- ✅ No risk to your system
- ✅ Perfect for understanding concepts

**What you'll learn**:
- How hashes detect changes
- What triggers alerts
- How baselines work
- Security monitoring concepts

### Active Mode (REAL System Monitoring)
- ⚠️ Monitors ACTUAL system files
- ⚠️ Alerts on real changes
- ⚠️ Requires proper configuration
- ⚠️ Use after understanding practice mode

**Production use cases**:
- Monitor /etc/passwd (Linux)
- Monitor /etc/hosts (all systems)
- Watch Windows registry files
- Protect web server files

---

## 📦 Installation

### Step 1: Install Dependencies
```bash
pip install -r fim_requirements.txt
```

### Step 2: Configure Environment (Optional)
```bash
# Copy example file
cp fim_env.example .env

# Edit with your credentials
nano .env
```

### Step 3: Review Configuration
```bash
# Edit configuration
nano fim_config.yaml
```

---

## 🚀 Quick Start - Practice Mode (5 Minutes)

### Run It Now!
```bash
python file_integrity_monitor.py
```

**You'll see**:
```
=== PRACTICE MODE ===
Learning file integrity monitoring safely
Setting up practice environment in ./test_files
Created 10 test files
Baseline created with 10 files

--- Check Iteration 1 ---
[SIMULATION] Modified: test_file_3.txt
MODIFIED: ./test_files/test_file_3.txt
  Old hash: 5d41402abc...
  New hash: 7d793037a0...
Alert: MODIFIED - ./test_files/test_file_3.txt
```

### What's Happening?
1. **10 test files created** in `./test_files/`
2. **Baseline established** (initial hashes calculated)
3. **Automatic modifications** simulated every 30 seconds
4. **Changes detected** immediately
5. **Alerts generated** and logged

### Try This (Hands-On Learning):
```bash
# In another terminal, manually modify a test file:
echo "I made this change!" >> ./test_files/test_file_0.txt

# Watch the FIM detect it in real-time!
```

---

## 📊 Understanding the Output

### Normal Check (No Changes)
```
--- Check Iteration 5 ---
[No alerts]
```
**Meaning**: All files match their baseline hashes ✅

### File Modified Alert
```
WARNING - MODIFIED: ./test_files/test_file_3.txt
WARNING -   Old hash: 5d41402abc4b2a76b9719d91...
WARNING -   New hash: 7d793037a0c70f9e4a9d7e5f...
Alert: MODIFIED - ./test_files/test_file_3.txt
```
**Meaning**: File content changed! Hash mismatch detected 🚨

### File Created Alert
```
INFO - NEW FILE: ./test_files/new_file.txt
Alert: CREATED - ./test_files/new_file.txt
```
**Meaning**: File didn't exist in baseline ℹ️

### File Deleted Alert
```
WARNING - DELETED: ./test_files/test_file_7.txt
Alert: DELETED - ./test_files/test_file_7.txt
```
**Meaning**: File removed from disk 🗑️

---

## 🔧 Configuration Guide

### Switch to Active Mode

Edit `fim_config.yaml`:
```yaml
mode: active  # Changed from 'practice'

active:
  hash_algorithm: sha256
  check_interval: 60
  
  watch_paths:
    # Linux example
    - path: /etc/passwd
      description: "User accounts"
    
    # Windows example
    - path: C:/Windows/System32/drivers/etc/hosts
      description: "Hosts file"
```

### Hash Algorithms

| Algorithm | Speed | Security | Use Case |
|-----------|-------|----------|----------|
| **md5** | Fastest | Low | Testing only |
| **sha1** | Fast | Medium | Legacy systems |
| **sha256** | Medium | High | **Recommended** |
| **sha512** | Slower | Highest | Maximum security |

**Recommendation**: Use SHA256 (good balance)

### Check Intervals

```yaml
# Practice mode
check_interval: 10  # Check every 10 seconds (fast learning)

# Active mode
check_interval: 60  # Check every 60 seconds (production)
```

**Guidelines**:
- **Critical files**: 30-60 seconds
- **Normal files**: 5-15 minutes
- **Archives**: 1-24 hours

---

## 🎓 Learning Exercises

### Exercise 1: Understand Hashes (10 min)
```bash
# Start practice mode
python file_integrity_monitor.py

# In another terminal:
# 1. View a test file
cat ./test_files/test_file_0.txt

# 2. Check the baseline
cat file_hashes.json | grep test_file_0

# 3. Modify the file
echo "CHANGE" >> ./test_files/test_file_0.txt

# 4. Watch FIM detect it!
# 5. Check the new hash in file_hashes.json
```

**What you'll learn**: Even tiny changes create completely 
different hashes!

### Exercise 2: Test Different Changes (15 min)
Try these and observe the alerts:

```bash
# 1. Modify content
echo "hack" >> ./test_files/test_file_1.txt

# 2. Delete file
rm ./test_files/test_file_2.txt

# 3. Create new file
echo "new" > ./test_files/new_file.txt

# 4. Rename file (appears as delete + create)
mv ./test_files/test_file_3.txt ./test_files/renamed.txt
```

### Exercise 3: Understand Ignore Patterns (10 min)
```bash
# These files are automatically ignored:
echo "test" > ./test_files/temp.log    # Ignored (.log)
echo "test" > ./test_files/temp.tmp    # Ignored (.tmp)

# This file is monitored:
echo "test" > ./test_files/important.txt  # MONITORED
```

**Edit config to add your own ignore patterns!**

---

## 🔍 How File Hashing Works

### The Math (Simplified)
```python
# Original file
content = "Hello World"

# Hash function (SHA256)
hash = sha256(content)
# Result: 7f83b1657ff1fc53b92dc18148a1d65...

# Change ONE letter
content = "Hello World!"
hash = sha256(content)  
# Result: 7509e5bda0c762d2bac7f90d758b5b2...
# ↑ COMPLETELY DIFFERENT!
```

### Why Hashes Are Perfect for FIM
1. **Deterministic**: Same file = same hash
2. **Unique**: Different files = different hashes
3. **One-way**: Can't reverse hash to get file
4. **Fast**: Quick to calculate
5. **Fixed-size**: Any file → same length hash

### Hash Collision (Theoretical)
**Question**: Can two files have the same hash?

**Answer**: With SHA256, probability is 1 in 2^256
(more atoms in the universe than possible collisions)

**Practical**: For FIM purposes, it's impossible!

---

## 🚨 Understanding Alerts

### Alert Types

#### MODIFIED (Most Critical)
```json
{
  "alert_type": "MODIFIED",
  "file_path": "/etc/passwd",
  "old_hash": "abc123...",
  "new_hash": "xyz789...",
  "details": "File modified!"
}
```
**Severity**: 🔴 Critical
**Action**: Investigate immediately!

**Possible causes**:
- Legitimate update
- Malware modification
- Unauthorized change
- System breach

#### CREATED (Informational)
```json
{
  "alert_type": "CREATED",
  "file_path": "/tmp/new_script.sh",
  "new_hash": "def456..."
}
```
**Severity**: 🟡 Medium
**Action**: Verify if expected

**Possible causes**:
- New legitimate file
- Attacker planted file
- System update

#### DELETED (Warning)
```json
{
  "alert_type": "DELETED",
  "file_path": "/etc/important.conf",
  "old_hash": "ghi789..."
}
```
**Severity**: 🟠 High
**Action**: Restore if unintended

**Possible causes**:
- Accidental deletion
- Ransomware
- System maintenance

---

## 📧 Email Alerts Setup

### Gmail Configuration (Recommended for Testing)

#### Step 1: Enable 2-Step Verification
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"

#### Step 2: Create App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Name it "File Integrity Monitor"
4. Copy the 16-character password

#### Step 3: Configure FIM
```bash
# Edit .env file
nano .env

# Add:
FIM_EMAIL_SENDER=your-email@gmail.com
FIM_EMAIL_PASSWORD=abcd efgh ijkl mnop  # App password
FIM_EMAIL_RECIPIENT=security@yourcompany.com
```

#### Step 4: Enable in Config
```yaml
# Edit fim_config.yaml
alerts:
  email:
    enabled: true  # ← Change to true
```

### Test Email Alerts
```bash
# Run in practice mode
python file_integrity_monitor.py

# Modify a file
echo "test" >> ./test_files/test_file_0.txt

# You should receive an email!
```

---

## 🖥️ Cross-Platform Usage

### Linux
```yaml
watch_paths:
  - path: /etc/passwd
    description: "User accounts"
  - path: /etc/shadow
    description: "Password hashes"
  - path: /etc/hosts
    description: "Hostname mapping"
  - path: /var/www/html
    description: "Web server files"
```

### Windows
```yaml
watch_paths:
  - path: C:/Windows/System32/drivers/etc/hosts
    description: "Hosts file"
  - path: C:/Windows/System32/config
    description: "Registry hives"
```

### macOS
```yaml
watch_paths:
  - path: /etc/passwd
    description: "User accounts"
  - path: /private/etc/hosts
    description: "Hosts file"
```

### VirtualBox VM
- Same as host OS (Linux/Windows)
- Great for testing without risk
- Can snapshot VM and revert changes

---

## 📊 Output Files

### file_hashes.json (Database)
```json
{
  "./test_files/test_file_0.txt": {
    "path": "./test_files/test_file_0.txt",
    "hash_value": "5d41402abc4b2a76b9719d911017c592",
    "algorithm": "sha256",
    "size": 125,
    "modified_time": 1704067200.0,
    "last_checked": "2025-01-01T10:00:00"
  }
}
```
**Purpose**: Stores baseline hashes
**Location**: Current directory
**Backup**: Recommended!

### fim_alerts_YYYYMMDD_HHMMSS.json (Alerts)
```json
[
  {
    "alert_type": "MODIFIED",
    "file_path": "./test_files/test_file_3.txt",
    "old_hash": "abc123...",
    "new_hash": "xyz789...",
    "timestamp": "2025-01-01T10:05:30",
    "mode": "practice",
    "details": "File modified!"
  }
]
```
**Purpose**: Export of all alerts
**Created**: On shutdown or every N iterations
**Use**: Send to SIEM, archive, analyze

### file_integrity_monitor.log (Logs)
```
2025-01-01 10:00:00 - INFO - FIM initialized in PRACTICE mode
2025-01-01 10:00:01 - INFO - Created 10 test files
2025-01-01 10:00:02 - INFO - Baseline created with 10 files
2025-01-01 10:05:30 - WARNING - MODIFIED: test_file_3.txt
```
**Purpose**: Detailed application logs
**Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

---

## 🐛 Troubleshooting

### "Permission denied" Errors
```
ERROR - Permission denied: /etc/shadow
```
**Solution**: Run with sudo (Linux) or as Administrator (Windows)
```bash
sudo python file_integrity_monitor.py
```

### No Files Monitored
```
INFO - Baseline created with 0 files
```
**Solution**: Check `watch_paths` in config, ensure paths exist

### Hash Mismatches on Every Check
**Possible causes**:
- Log files that change constantly (add to ignore_patterns)
- System files updated by OS
- Temporary files

**Solution**: Add to `ignore_patterns` in config

### Email Not Sending
```
ERROR - Email send failed: Authentication failed
```
**Solutions**:
1. Use Gmail App Password (not regular password)
2. Enable "Less secure apps" (not recommended)
3. Check SMTP settings
4. Verify .env file loaded

---

## 🎯 Best Practices

### Security
1. **Protect baseline**: Backup `file_hashes.json`
2. **Monitor FIM itself**: Hash the FIM script!
3. **Regular reviews**: Check alerts daily
4. **Restrict access**: Only admins should modify baseline

### Performance
1. **Start small**: Monitor critical files first
2. **Tune intervals**: Balance security vs resources
3. **Use ignore patterns**: Skip logs, caches, temp files
4. **Consider file size**: Large files = slower hashing

### Operational
1. **Test in practice mode first**
2. **Document watch paths** (why monitoring each)
3. **Set up alerts** (email/SIEM)
4. **Regular baseline updates** (after legitimate changes)

---

## 📚 Python Concepts Demonstrated

### Loops
```python
# FOR loop - iterate over files
for file_path in test_files:
    check_file_integrity(file_path)

# WHILE loop - continuous monitoring
while self.running:
    perform_checks()
    time.sleep(interval)
```

### Variables
```python
# Simple variables
hash_value = "abc123def456"
file_path = "/etc/passwd"

# Collections
baseline = {}  # Dictionary
alert_queue = []  # List
```

### Functions
```python
# Function definition
def calculate_file_hash(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

# Function call
hash_result = calculate_file_hash("/etc/passwd")
```

### Statements
```python
# IF statement
if current_hash != baseline_hash:
    alert("File modified!")

# TRY/EXCEPT statement
try:
    hash_value = calculate_hash(file)
except FileNotFoundError:
    log("File not found")

# WITH statement (context manager)
with open(file, 'rb') as f:
    content = f.read()
```

---

## 🔄 Workflow Examples

### Daily Security Operations
```bash
# Morning: Start FIM
python file_integrity_monitor.py

# Throughout day: Monitor logs
tail -f file_integrity_monitor.log

# Evening: Review alerts
cat fim_alerts_*.json | grep MODIFIED

# Investigate any suspicious changes
```

### After System Updates
```bash
# 1. Stop FIM
# Press Ctrl+C

# 2. Perform system updates
sudo apt update && sudo apt upgrade

# 3. Recreate baseline
rm file_hashes.json
python file_integrity_monitor.py
# This creates new baseline with updated files

# 4. Resume monitoring
# FIM now knows about legitimate changes
```

### Incident Response
```bash
# Suspect breach? Check FIM immediately!

# 1. View recent changes
grep MODIFIED file_integrity_monitor.log

# 2. Review alert details
cat fim_alerts_*.json | jq '.[] | select(.alert_type=="MODIFIED")'

# 3. Investigate modified files
# Check: WHO, WHEN, WHY

# 4. Restore from backup if needed
```

---

## 🎓 Next Steps

### After Mastering Practice Mode
1. ✅ Switch to active mode
2. ✅ Monitor a single critical file
3. ✅ Gradually add more paths
4. ✅ Set up email alerts
5. ✅ Integrate with SIEM (optional)

### Advanced Topics
- Integrity monitoring for databases
- Real-time monitoring (inotify on Linux)
- Integration with security tools (OSSEC, Wazuh)
- Compliance reporting (PCI-DSS, HIPAA)
- Centralized FIM for multiple servers

---

## 📝 Quick Reference

### Start Monitoring
```bash
python file_integrity_monitor.py
```

### Check Line Length (verify PEP 8)
```bash
python check_line_length.py file_integrity_monitor.py
```

### View Current Baseline
```bash
cat file_hashes.json | jq .
```

### View Alerts
```bash
cat fim_alerts_*.json | jq .
```

### Recreate Baseline (after legitimate changes)
```bash
rm file_hashes.json
python file_integrity_monitor.py
```

---

## 🎉 Summary

You now have a **production-ready File Integrity Monitor** with:

✅ **Practice mode** - Safe learning environment
✅ **Active mode** - Real system monitoring
✅ **Cross-platform** - Linux, Windows, macOS
✅ **Multiple hash algorithms** - MD5, SHA1, SHA256, SHA512
✅ **Smart alerting** - Email, SIEM, logs
✅ **PEP 8 compliant** - 79-character line limit
✅ **Well-documented** - Learn by doing
✅ **Production-ready** - Use in real environments

**Start with practice mode, learn the concepts, then deploy to production!**

**Happy monitoring! 🔐🎓**
