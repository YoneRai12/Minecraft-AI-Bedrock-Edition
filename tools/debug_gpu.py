import torch
import sys

print("=== PyTorch GPU Diagnostics ===")
print(f"Python: {sys.version}")
print(f"PyTorch Version: {torch.__version__}")
print(f"CUDA Version (PyTorch): {torch.version.cuda}")
print(f"CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"Device Count: {torch.cuda.device_count()}")
    print(f"Current Device: {torch.cuda.current_device()}")
    print(f"Device Name: {torch.cuda.get_device_name(0)}")
    try:
        cap = torch.cuda.get_device_capability(0)
        print(f"Device Capability: {cap} (sm_{cap[0]}{cap[1]})")
    except Exception as e:
        print(f"Error getting capability: {e}")
        
    print(f"Supported Archs in this build: {torch.cuda.get_arch_list()}")
    
    # Check specifically for sm_120 (Blackwell)
    if "sm_120" in torch.cuda.get_arch_list():
        print("SUCCESS: This PyTorch build supports sm_120 (RTX 5090)!")
    else:
        print("WARNING: This PyTorch build DOES NOT listing 'sm_120' support.")
        print("Typical supported: sm_50 to sm_90.")
else:
    print("No CUDA device detected by PyTorch.")

print("=============================")
print("If you see 'sm_120' in Supported Archs, it should work.")
input("Press Enter to close...")
