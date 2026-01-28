import torch
import sys
import pygetwindow as gw
import time
import os

print("=== MainkurafutoAI System Diagnostic ===")

# 1. GPU Check
print("\n[1] GPU / PyTorch Check")
print(f"Python: {sys.version.split()[0]}")
try:
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"Device: {torch.cuda.get_device_name(0)}")
        cap = torch.cuda.get_device_capability(0)
        print(f"Capability: sm_{cap[0]}{cap[1]}")
        archs = torch.cuda.get_arch_list()
        print(f"Supported Archs: {archs}")
        if f"sm_{cap[0]}{cap[1]}" not in archs:
            print("CRITICAL: Your GPU architecture is NOT in the supported list!")
    else:
        print("CRITICAL: CUDA is NOT available. Falling back to CPU.")
except Exception as e:
    print(f"Error checking GPU: {e}")

# 2. Window Check
print("\n[2] Window Detection Check")
try:
    titles = gw.getAllTitles()
    mc_windows = [t for t in titles if "Minecraft" in t]
    print(f"All 'Minecraft' windows found: {mc_windows}")
    
    for title in mc_windows:
        win = gw.getWindowsWithTitle(title)[0]
        print(f" - '{title}': {win.left},{win.top} {win.width}x{win.height} (Active: {win.isActive})")
except Exception as e:
    print(f"Error checking windows: {e}")

print("\n=== End of Report ===")
print("Please copy this output if problems persist.")
time.sleep(5)
