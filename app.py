import os
import sys
import subprocess
import platform
import argparse
import json
import asyncio

# Function to check and install missing packages
def check_and_install_dependencies():
    required_packages = [
        "edge_tts",
        "whisper_timestamped",
        "torch",
        "numpy",
        "moviepy"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is already installed.")
        except ImportError:
            print(f"Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ Successfully installed {package}.")
            except Exception as e:
                print(f"✗ Failed to install {package}: {str(e)}")
                if package == "edge_tts":
                    print("Attempting alternative installation for edge-tts...")
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", "edge-tts"])
                        print("✓ Successfully installed edge-tts with hyphen.")
                    except Exception as e2:
                        print(f"✗ Failed alternative installation: {str(e2)}")

# Detect available hardware
def detect_hardware():
    hardware = {"cpu": True, "gpu": False, "tpu": False}
    
    # Check for GPU (CUDA) availability with PyTorch
    try:
        import torch
        hardware["gpu"] = torch.cuda.is_available()
        if hardware["gpu"]:
            print(f"✓ GPU detected: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA Version: {torch.version.cuda}")
    except Exception as e:
        print(f"✗ Error checking GPU: {str(e)}")
    
    # Check for TPU availability (Google Colab TPU or other)
    try:
        if "COLAB_TPU_ADDR" in os.environ:
            hardware["tpu"] = True
            print("✓ TPU detected (Colab)")
        elif os.path.exists("/usr/lib/libtpu.so"):
            hardware["tpu"] = True
            print("✓ TPU detected")
    except Exception as e:
        print(f"✗ Error checking TPU: {str(e)}")
    
    return hardware

# Import modules with proper error handling
def import_modules():
    global edge_tts, whisper, generate_script, generate_audio, generate_timed_captions
    global generate_video_url, get_output_media, getVideoSearchQueriesTimed, merge_empty_intervals
    
    modules_imported = True
    
    # Try importing each module separately with error handling
    try:
        import edge_tts
    except ImportError as e:
        print(f"WARNING: Could not import edge_tts: {str(e)}")
        print("Audio generation might not work. Please run the setup.py script first.")
        modules_imported = False
    
    try:
        import whisper_timestamped as whisper
    except ImportError as e:
        print(f"WARNING: Could not import whisper_timestamped: {str(e)}")
        print("Caption generation might not work. Please run the setup.py script first.")
        modules_imported = False
    
    try:
        from utility.script.script_generator import generate_script
    except ImportError as e:
        print(f"WARNING: Could not import script_generator: {str(e)}")
        modules_imported = False
    
    try:
        from utility.audio.audio_generator import generate_audio
    except ImportError as e:
        print(f"WARNING: Could not import audio_generator: {str(e)}")
        modules_imported = False
    
    try:
        from utility.captions.timed_captions_generator import generate_timed_captions
    except ImportError as e:
        print(f"WARNING: Could not import timed_captions_generator: {str(e)}")
        modules_imported = False
    
    try:
        from utility.video.background_video_generator import generate_video_url
    except ImportError as e:
        print(f"WARNING: Could not import background_video_generator: {str(e)}")
        modules_imported = False
    
    try:
        from utility.render.render_engine import get_output_media
    except ImportError as e:
        print(f"WARNING: Could not import render_engine: {str(e)}")
        modules_imported = False
    
    try:
        from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals
    except ImportError as e:
        print(f"WARNING: Could not import video_search_query_generator: {str(e)}")
        modules_imported = False
    
    return modules_imported

def read_script_file(file_path):
    """Read script from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        raise ValueError(f"Error reading script file: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Generate a video from a script.")
    
    # Require exactly one of these arguments
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--text', type=str, help='Direct text input for the script')
    input_group.add_argument('--file', type=str, help='Path to a text file containing the script')
    
    # Add options for hardware selection
    parser.add_argument('--force-cpu', action='store_true', help='Force CPU usage even if GPU is available')
    parser.add_argument('--force-gpu', action='store_true', help='Force GPU usage (will error if not available)')
    parser.add_argument('--force-tpu', action='store_true', help='Force TPU usage (will error if not available)')
    
    try:
        args = parser.parse_args()
    except:
        # If there's a problem parsing arguments, print usage and exit
        parser.print_help()
        sys.exit(1)
    
    # Detect available hardware
    hardware = detect_hardware()
    
    # Handle hardware selection
    if args.force_cpu:
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        os.environ["TPU_NAME"] = ""
        print("Forcing CPU usage as requested.")
    elif args.force_gpu and not hardware["gpu"]:
        print("Error: GPU requested but not available.")
        sys.exit(1)
    elif args.force_tpu and not hardware["tpu"]:
        print("Error: TPU requested but not available.")
        sys.exit(1)
    
    SAMPLE_FILE_NAME = "audio_tts.wav"
    VIDEO_SERVER = "pexel"
    OUTPUT_VIDEO_NAME = "final_video.mp4"

    try:
        # Get script content either from direct text or file
        script_content = read_script_file(args.file) if args.file else args.text
        
        # Process the input script (no AI generation, just pass through)
        script = generate_script(script_content)
        print("Script to be used:")
        print(script)
        print("\nGenerating audio...")
        
        # Generate audio with error handling
        try:
            asyncio.run(generate_audio(script, SAMPLE_FILE_NAME))
            print("Audio generated successfully")
        except Exception as e:
            print(f"Warning: Audio generation encountered issues: {str(e)}")
            print("Attempting to continue...")

        # Generate captions
        print("\nGenerating captions...")
        timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)
        print("Captions generated successfully")

        # Generate video search terms
        print("\nGenerating video search terms...")
        search_terms = getVideoSearchQueriesTimed(script, timed_captions)
        if search_terms:
            print("Search terms generated successfully")
        else:
            print("No search terms generated")

        # Get background videos
        background_video_urls = None
        if search_terms is not None:
            print("\nFetching background videos...")
            background_video_urls = generate_video_url(search_terms, VIDEO_SERVER)
            if background_video_urls:
                print("Background videos fetched successfully")
            else:
                print("No background videos found")

        background_video_urls = merge_empty_intervals(background_video_urls)

        # Render final video
        if background_video_urls is not None:
            print("\nRendering final video...")
            video = get_output_media(SAMPLE_FILE_NAME, timed_captions, background_video_urls, VIDEO_SERVER)
            print(f"\nVideo generated successfully: {OUTPUT_VIDEO_NAME}")
        else:
            print("\nError: Could not generate video due to missing background videos")

    except Exception as e:
        print(f"\nError: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    print("=== Text-To-Video-AI ===")
    print(f"Python version: {platform.python_version()}")
    print(f"System: {platform.system()} {platform.version()}")
    print("Checking dependencies...")
    
    # Check and install missing dependencies
    check_and_install_dependencies()
    
    # Configure environment for audio
    try:
        # Windows-specific path adjustments
        if os.name == 'nt':
            temp_dir = os.environ.get('TEMP', 'C:\\Windows\\Temp')
            runtime_dir = os.path.join(temp_dir, 'runtime-dir')
        else:
            # Linux/Mac paths
            runtime_dir = '/tmp/runtime-dir'
            
        os.environ['XDG_RUNTIME_DIR'] = runtime_dir
        os.makedirs(runtime_dir, mode=0o700, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create runtime directory: {str(e)}")
        print("Some audio operations might not work correctly.")
    
    # Import modules
    if not import_modules():
        print("\nSome modules could not be imported. Please run the setup script:")
        print("python setup.py  # For regular environments")
        print("python colab_setup.py  # For Google Colab")
        sys.exit(1)
    
    # Run the main function
    sys.exit(main())
