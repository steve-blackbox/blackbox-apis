import os
import hashlib
import json
import sys

# Target core directories to monitor inside 01_LA_SOUTE_A_CASH
TARGET_DIRS = ['INTERFACES', 'SEO', '02_code_shield', '03_audio_convert_pro', '04_secure_file_link', '05_affiliate_link_cloak', '06_webhook_retry_shield']
INTEGRITY_FILE = 'soute_integrity.json'

def generate_file_hash(filepath):
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def build_snapshot():
    snapshot = {}
    print("[⚙️ SENTINEL] Scanning soute infrastructure nodes...")
    for target in TARGET_DIRS:
        if os.path.isdir(target):
            for root, _, files in os.walk(target):
                for file in files:
                    if file.startswith('.') or file == INTEGRITY_FILE:
                        continue
                    full_path = os.path.join(root, file)
                    file_hash = generate_file_hash(full_path)
                    if file_hash:
                        snapshot[full_path] = file_hash
    return snapshot

def seal_soute():
    snapshot = build_snapshot()
    with open(INTEGRITY_FILE, 'w') as f:
        json.dump(snapshot, f, indent=4)
    print(f"[🏆 SEALED] Integrity mapping locked into {INTEGRITY_FILE}. Soute is secure.")

def verify_soute():
    if not os.path.exists(INTEGRITY_FILE):
        print("[🚨 ERROR] No integrity seal found. Run 'python3 soute_sentinel.py seal' first.")
        sys.exit(1)
        
    with open(INTEGRITY_FILE, 'r') as f:
        locked_snapshot = json.load(f)
        
    current_snapshot = build_snapshot()
    corrupted = False
    
    print("[🔍 AUDIT] Cross-checking dynamic hashes with locked vault...")
    for filepath, locked_hash in locked_snapshot.items():
        if filepath not in current_snapshot:
            print(f"[🚨 MISSING ASSET] File removed from disk: {filepath}")
            corrupted = True
        elif current_snapshot[filepath] != locked_hash:
            print(f"[🚨 CORRUPTED ASSET] File modified or tampered: {filepath}")
            corrupted = True
            
    for filepath in current_snapshot:
        if filepath not in locked_snapshot:
            print(f"[🚨 UNTRACKED ASSET] Rogue file injected into soute: {filepath}")
            corrupted = True
            
    if not corrupted:
        print("[💎 NOMINAL] 100% Integrity match. Your local empire is intact and sterile.")
    else:
        print("[❌ WARNING] Soute status compromised! Check the alerts logged above.")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'seal':
        seal_soute()
    else:
        verify_soute()