#!/usr/bin/env python
import os
import sys
import subprocess
import platform

def print_header():
    print("=" * 50)
    print("Text-To-Video-AI Setup")
    print("=" * 50)
    print(f"Python version: {platform.python_version()}")
    print(f"System: {platform.system()} {platform.version()}")
    print("=" * 50)

def install_requirements():
    print("\n[1/3] Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Successfully installed requirements.")
    except Exception as e:
        print(f"✗ Error installing requirements: {str(e)}")
        print("Attempting to install critical dependencies individually...")
        
        critical_deps = [
            "edge-tts",
            "whisper-timestamped",
            "torch",
            "numpy",
            "moviepy"
        ]
        
        for dep in critical_deps:
            try:
                print(f"Installing {dep}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"✓ Successfully installed {dep}.")
            except Exception as e2:
                print(f"✗ Failed to install {dep}: {str(e2)}")

def setup_environment():
    print("\n[2/3] Setting up environment...")
    
    # Windows-specific path adjustments
    if os.name == 'nt':
        temp_dir = os.environ.get('TEMP', 'C:\\Windows\\Temp')
        runtime_dir = os.path.join(temp_dir, 'runtime-dir')
    else:
        # Linux/Mac paths
        runtime_dir = '/tmp/runtime-dir'
        
    os.environ['XDG_RUNTIME_DIR'] = runtime_dir
    try:
        os.makedirs(runtime_dir, mode=0o700, exist_ok=True)
        print(f"✓ Created runtime directory: {runtime_dir}")
    except Exception as e:
        print(f"✗ Error creating runtime directory: {str(e)}")

def detect_hardware():
    print("\n[3/3] Detecting hardware...")
    
    # Check for CPU info
    try:
        if platform.system() == "Windows":
            cpu_info = platform.processor()
        else:
            cpu_info = os.popen("cat /proc/cpuinfo | grep 'model name' | head -n1").read().strip()
        print(f"CPU: {cpu_info}")
    except:
        print("CPU: Unknown")
    
    # Check for GPU (CUDA) availability with PyTorch
    try:
        import torch
        has_gpu = torch.cuda.is_available()
        if has_gpu:
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"CUDA Version: {torch.version.cuda}")
        else:
            print("GPU: Not available")
    except Exception as e:
        print(f"GPU: Error detecting - {str(e)}")
    
    # Check for TPU availability
    try:
        if "COLAB_TPU_ADDR" in os.environ:
            print("TPU: Available (Google Colab)")
        elif os.path.exists("/usr/lib/libtpu.so"):
            print("TPU: Available")
        else:
            print("TPU: Not available")
    except Exception as e:
        print(f"TPU: Error detecting - {str(e)}")

def main():
    print_header()
    install_requirements()
    setup_environment()
    detect_hardware()
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("You can now run the Text-To-Video-AI with:")
    print("python app.py --text \"Your script text here\"")
    print("or")
    print("python app.py --file path/to/script.txt")
    print("=" * 50)

if __name__ == "__main__":
    main() 