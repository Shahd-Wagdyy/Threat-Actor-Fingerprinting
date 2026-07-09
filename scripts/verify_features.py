import sys
import os
sys.path.append(os.getcwd())
from scripts.preprocessing.preprocess import get_language
from scripts.features.ioc_extractor import extract_from_text

# Test Language Detection
print(f"English Language: {get_language('Hello this is a test in English.')}")
print(f"Russian Language: {get_language('Привет, это тест на русском языке.')}")

# Test IOC Extraction
sample_text = """
Check this IP: 1.2.3.4 and domain example.com.
Follow this URL: http://test.com/malware.exe
Mail me at: test@test.com
Wallet: 0x1234567890abcdef1234567890abcdef12345678
Reg: HKEY_LOCAL_MACHINE\\Software\\Test
Mutex: Global\\TestMutex12345
This is a ransomware exploit leak.
"""
results = extract_from_text(sample_text)
print("\nIOC Extraction Results:")
for k, v in results.items():
    if "_count" in k:
        print(f"{k}: {v}")
    elif isinstance(v, list) and v:
        print(f"{k}: {v}")
