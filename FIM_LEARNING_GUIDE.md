# File Integrity Monitoring - Security Learning Guide

## 🎓 Understanding FIM from First Principles

This guide explains HOW and WHY file integrity monitoring works,
perfect for learning security concepts hands-on.

---

## 📖 Chapter 1: What Problem Does FIM Solve?

### The Security Challenge

**Scenario**: You're a system administrator. One morning, you notice:
- Users can't log in
- Your website shows strange content
- System behaves oddly

**Question**: What happened? When? What was changed?

**Problem**: Without FIM, you have NO IDEA what files were modified!

### FIM's Solution

File Integrity Monitoring solves this by:
1. **Recording** the "fingerprint" of every important file
2. **Checking** regularly if fingerprints have changed
3. **Alerting** immediately when changes occur

**Analogy**: Like a security camera, but for files!

---

## 🔬 Chapter 2: Cryptographic Hashing

### What is a Hash?

A **hash** is a fixed-length "fingerprint" of data:

```
Input:  "Hello World"
Hash:   7f83b1657ff1fc53b92dc18148a1d65...

Input:  "Hello World!"  (added one character!)
Hash:   7509e5bda0c762d2bac7f90d758b5b2...
                ↑ COMPLETELY DIFFERENT
```

### Hash Properties (Why They're Perfect for FIM)

#### 1. Deterministic
Same input = same hash (every time)
```python
hash("file.txt")  # Always: abc123...
hash("file.txt")  # Always: abc123...
```

#### 2. One-Way (Irreversible)
Can't get file from hash
```python
hash = "abc123..."
original_file = ??? # Impossible!
```

#### 3. Avalanche Effect
Tiny change → completely different hash
```python
"Hello"  → hash: 185f8db3...
"Hello!" → hash: 9b71d224...
         ↑ Changed ONE character, hash is completely different
```

#### 4. Fixed Length
Any file size → same hash length
```python
1 byte file    → 64 character hash
1 GB file      → 64 character hash
```

#### 5. Collision Resistant
Nearly impossible for two different files to have same hash

**Math**: SHA256 has 2^256 possible hashes
- That's more than atoms in the universe!
- Practically: collisions don't happen

### Common Hash Algorithms

| Algorithm | Output Size | Speed | Security | Use Case |
|-----------|-------------|-------|----------|----------|
| **MD5** | 128 bits | Fastest | ❌ Broken | Testing only |
| **SHA1** | 160 bits | Fast | ⚠️ Weak | Legacy |
| **SHA256** | 256 bits | Medium | ✅ Strong | **Recommended** |
| **SHA512** | 512 bits | Slower | ✅ Strongest | Max security |

**Why MD5 is broken**: Researchers found ways to create 
collisions (two different files with same hash). Never use
for security!

**Why SHA256 is recommended**: No known collisions, good 
performance, industry standard.

---

## 🔍 Chapter 3: How FIM Works (Step by Step)

### Phase 1: Baseline Creation

```python
# For each important file:
for file_path in important_files:
    # 1. Read the file
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # 2. Calculate hash
    hash_value = sha256(content).hexdigest()
    
    # 3. Store in database
    baseline[file_path] = {
        'hash': hash_value,
        'timestamp': now(),
        'size': file_size
    }
```

**Result**: Database of file "fingerprints"

### Phase 2: Monitoring

```python
# Continuously:
while monitoring:
    for file_path in baseline:
        # 1. Calculate current hash
        current_hash = sha256(read_file(file_path))
        
        # 2. Compare with baseline
        if current_hash != baseline[file_path]['hash']:
            # 3. ALERT! File changed!
            send_alert(
                f"File {file_path} was modified!"
            )
            
            # 4. Update baseline
            baseline[file_path]['hash'] = current_hash
    
    # Wait before next check
    sleep(check_interval)
```

### Phase 3: Detection & Response

When hash mismatch detected:
1. **Generate alert** (email, SIEM, log)
2. **Record details** (what, when, old/new hash)
3. **Update baseline** (or investigate first!)
4. **Investigate** (who made the change? why?)

---

## 🎯 Chapter 4: Practice Mode Deep Dive

### What Practice Mode Does

```python
# 1. Create test environment
def setup_practice():
    create_directory('./test_files')
    
    for i in range(10):
        create_file(f'test_file_{i}.txt')
        write_random_content()

# 2. Establish baseline
baseline = {}
for file in test_files:
    baseline[file] = calculate_hash(file)

# 3. Simulate changes
every 30 seconds:
    pick_random_file()
    modify_it()  # FIM will detect this!

# 4. Monitor and alert
every 10 seconds:
    check_all_files()
    if_changed: alert()
```

### Learning Objectives

**Exercise 1**: Watch automatic detection
- FIM simulates changes every 30s
- See alerts in real-time
- Understand hash comparison

**Exercise 2**: Manual modification
```bash
# Modify a file yourself
echo "I made this change!" >> test_file_0.txt

# Watch FIM detect it immediately!
```

**Exercise 3**: Different change types
```bash
# Modify content
echo "new" >> test_file_1.txt

# Delete file
rm test_file_2.txt

# Create file
echo "hi" > new_file.txt

# See how FIM handles each!
```

### Safe Experimentation

Why practice mode is safe:
- ✅ Only touches `./test_files/` directory
- ✅ No system files involved
- ✅ Can delete and restart anytime
- ✅ Perfect for breaking things and learning

---

## 🛡️ Chapter 5: Active Mode (Real Security)

### Real-World Use Cases

#### Case 1: Detect Malware

**Scenario**: Ransomware modifies system files

```yaml
# Monitor critical executables
watch_paths:
  - path: C:/Windows/System32
    description: "System executables"
```

**FIM alerts**: 
```
MODIFIED: C:/Windows/System32/notepad.exe
Old hash: abc123...
New hash: xyz789...
```

**Response**: QUARANTINE! Malware detected!

#### Case 2: Web Defacement

**Scenario**: Attacker modifies website

```yaml
watch_paths:
  - path: /var/www/html
    description: "Web server files"
```

**FIM alerts**:
```
MODIFIED: /var/www/html/index.html
```

**Response**: Restore from backup, investigate breach

#### Case 3: Configuration Changes

**Scenario**: Unauthorized admin access

```yaml
watch_paths:
  - path: /etc/passwd
    description: "User accounts"
  - path: /etc/shadow
    description: "Password hashes"
```

**FIM alerts**:
```
MODIFIED: /etc/passwd
MODIFIED: /etc/shadow
```

**Response**: Check: who added accounts? Incident response!

### Setting Up Active Monitoring

```yaml
# Start small
watch_paths:
  - path: /etc/hosts
    description: "Single critical file"

# Verify it works
# (manually modify /etc/hosts, see alert)

# Gradually expand
watch_paths:
  - path: /etc/hosts
  - path: /etc/passwd
  - path: /var/www/html
  - path: /home/admin/.ssh
```

---

## 🧠 Chapter 6: Understanding the Code

### Key Components

#### 1. Hash Generation
```python
def calculate_file_hash(file_path):
    """
    Core security function.
    Converts file → fixed-length fingerprint
    """
    hasher = hashlib.sha256()
    
    # Read in chunks (efficient for large files)
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(8192)  # 8KB at a time
            if not chunk:
                break
            hasher.update(chunk)
    
    return hasher.hexdigest()
```

**Why chunks?**: Large files (GB) can't fit in memory. 
Hashing algorithms process data incrementally.

#### 2. Change Detection
```python
def check_file_integrity(file_path):
    """
    Compare current state with baseline.
    This is where security happens!
    """
    # Get current hash
    current_hash = calculate_file_hash(file_path)
    
    # Get baseline hash
    baseline_hash = baseline[file_path]['hash']
    
    # Compare
    if current_hash != baseline_hash:
        # ALERT! Change detected!
        raise_alert(file_path, baseline_hash, current_hash)
```

#### 3. Baseline Management
```python
# Creating baseline
baseline = {}
for file_path in files_to_monitor:
    baseline[file_path] = {
        'hash': calculate_hash(file_path),
        'size': get_file_size(file_path),
        'timestamp': now()
    }

# Saving baseline
with open('baseline.json', 'w') as f:
    json.dump(baseline, f)

# Loading baseline
with open('baseline.json', 'r') as f:
    baseline = json.load(f)
```

**Critical**: Baseline must be protected! If attacker
modifies baseline, FIM is useless.

### Python Patterns Used

#### Loops
```python
# FOR - iterate over files
for file_path in files_to_check:
    check_integrity(file_path)

# WHILE - continuous monitoring
while running:
    perform_checks()
    time.sleep(interval)
```

#### Variables
```python
# Simple
hash_value = "abc123..."
file_path = "/etc/passwd"

# Collections
baseline = {}  # Dictionary: {path: record}
alerts = []    # List: [alert1, alert2, ...]
```

#### Functions
```python
# Definition
def calculate_hash(file_path: str) -> str:
    # ...logic...
    return hash_value

# Call
result = calculate_hash("/etc/passwd")
```

#### Statements
```python
# IF - decision making
if hash_changed:
    alert("File modified!")

# TRY/EXCEPT - error handling
try:
    hash = calculate_hash(file)
except FileNotFoundError:
    log("File not found")

# WITH - resource management
with open(file, 'rb') as f:
    content = f.read()
```

---

## 🔒 Chapter 7: Security Concepts

### Defense in Depth

FIM is ONE layer in security:

```
Layer 1: Firewall (block attacks)
Layer 2: IDS/IPS (detect intrusions)
Layer 3: FIM (detect changes) ← YOU ARE HERE
Layer 4: SIEM (correlate events)
Layer 5: Incident Response
```

**FIM's role**: Detect what got through other layers!

### Compliance Requirements

Many standards REQUIRE FIM:

**PCI-DSS** (Payment Card Industry):
- Requirement 11.5: Deploy FIM

**HIPAA** (Healthcare):
- Detect unauthorized access to patient data

**SOX** (Financial):
- Monitor critical system files

**Without FIM**: You can't comply!

### Incident Response

When FIM alerts:

```
1. DETECT  → FIM alert: file modified
2. ANALYZE → Who? When? What changed?
3. CONTAIN → Isolate affected system
4. ERADICATE → Remove malware/threat
5. RECOVER → Restore from clean backup
6. LESSONS → Update security controls
```

**FIM is step 1**: Can't respond to what you don't detect!

---

## 💡 Chapter 8: Advanced Topics

### Limitations of FIM

#### 1. Memory-only Malware
FIM only monitors files on disk. Malware running entirely
in RAM won't be detected.

**Solution**: Combine with EDR (Endpoint Detection)

#### 2. Baseline Compromise
If attacker modifies both file AND baseline, no alert!

**Solution**: 
- Store baseline on read-only media
- Sign baseline cryptographically
- Use centralized FIM server

#### 3. Performance Impact
Hashing large files = CPU/disk usage

**Solution**:
- Tune check intervals
- Prioritize critical files
- Use faster hash algorithms (with caution!)

### Real-Time Monitoring

Instead of periodic checks, monitor filesystem events:

**Linux**: inotify
```python
import inotify

watch = inotify.add_watch('/etc', inotify.IN_MODIFY)
# Alert immediately when file changes!
```

**Windows**: ReadDirectoryChangesW API

**Advantage**: Instant detection (no polling)
**Disadvantage**: More complex, higher resource usage

### Centralized FIM

For multiple servers:

```
Server 1 → FIM agent → Central FIM server
Server 2 → FIM agent → Central FIM server
Server 3 → FIM agent → Central FIM server
```

**Benefits**:
- Single dashboard
- Centralized alerts
- Protected baseline storage
- Compliance reporting

**Tools**: OSSEC, Wazuh, Tripwire Enterprise

---

## 🎯 Chapter 9: Hands-On Exercises

### Beginner Exercises

**Exercise 1**: Understand hashes
```bash
# Hash the same file twice
echo "test" > file.txt
sha256sum file.txt  # Note the hash
sha256sum file.txt  # Same hash!

# Modify and hash again
echo "test2" > file.txt
sha256sum file.txt  # Different hash!
```

**Exercise 2**: Manual FIM
```bash
# 1. Create baseline
sha256sum /etc/hosts > baseline.txt

# 2. Modify file
echo "127.0.0.1 test" >> /etc/hosts

# 3. Check integrity
sha256sum /etc/hosts > current.txt
diff baseline.txt current.txt  # DIFFERENT!
```

### Intermediate Exercises

**Exercise 3**: Practice mode exploration
1. Start FIM in practice mode
2. Manually modify 3 different test files
3. Observe the different alert types
4. Check the baseline JSON file
5. Delete a test file and watch detection

**Exercise 4**: Active mode setup
1. Choose a non-critical file to monitor
2. Configure active mode
3. Create baseline
4. Manually modify the file
5. Verify alert received

### Advanced Exercises

**Exercise 5**: Detect simulated breach
```bash
# Scenario: Attacker modifies system file

# 1. Start FIM monitoring /etc/hosts
# 2. Simulate attack:
echo "127.0.0.1 evil.com" >> /etc/hosts
# 3. FIM should alert immediately
# 4. Investigate: check /etc/hosts
# 5. Restore: git checkout /etc/hosts
```

**Exercise 6**: Compliance reporting
1. Run FIM for 24 hours
2. Collect all alerts
3. Generate report:
   - How many changes detected?
   - Which files changed most?
   - Were changes authorized?

---

## 📚 Chapter 10: Further Learning

### Recommended Reading

**Books**:
- "Applied Cryptography" by Bruce Schneier
- "Practical Malware Analysis" by Michael Sikorski

**Standards**:
- PCI-DSS v4.0 (Section 11.5)
- NIST SP 800-92 (Log Management)

**Tools to Explore**:
- **OSSEC**: Open-source HIDS with FIM
- **Wazuh**: Fork of OSSEC, actively maintained
- **Tripwire**: Commercial FIM solution
- **Samhain**: Lightweight FIM for Linux

### Career Paths

FIM knowledge valuable for:
- **Security Analyst**: Monitor alerts, investigate changes
- **Incident Responder**: Use FIM in breach investigations
- **Compliance Auditor**: Verify FIM implementation
- **System Administrator**: Deploy and maintain FIM
- **Security Engineer**: Design FIM architecture

### Certifications

FIM covered in:
- **CompTIA Security+**: Security controls
- **CISSP**: Domain 7 - Security Operations
- **GIAC GCIH**: Incident handling
- **CEH**: Intrusion detection

---

## 🎓 Final Thoughts

### What You've Learned

✅ **Cryptographic hashing**: How and why it works
✅ **File integrity monitoring**: Core security concept
✅ **Practice mode**: Safe experimentation environment
✅ **Active mode**: Real-world security deployment
✅ **Python programming**: Loops, functions, statements
✅ **Security operations**: Detection and response

### Next Steps

1. **Master practice mode** (understand every alert)
2. **Deploy active mode** (start with one file)
3. **Expand coverage** (add critical files)
4. **Integrate alerts** (email, SIEM)
5. **Document procedures** (what to do on alerts)
6. **Explore advanced tools** (OSSEC, Wazuh)

### The Big Picture

File Integrity Monitoring is a **fundamental security control**.
Every secure organization uses FIM to:
- Detect breaches
- Ensure compliance
- Protect critical systems
- Support incident response

**You now understand FIM at a deep level!**

Use this knowledge to:
- Secure your own systems
- Advance your security career
- Build on this foundation

**Keep learning, keep monitoring, stay secure! 🔐**
