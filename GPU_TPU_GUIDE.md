# Running Text-To-Video-AI on GPU and TPU

This guide explains how to run Text-To-Video-AI on different hardware accelerators.

## Requirements

- Python 3.7+ 
- For GPU: CUDA-capable GPU with CUDA 11.0+
- For TPU: Google Colab TPU or Cloud TPU

## Quick Setup

### Regular Installation

For any environment (CPU/GPU/TPU):

```bash
# Clone the repository
git clone https://github.com/yourusername/Text-To-Video-AI.git
cd Text-To-Video-AI

# Run the setup script
python setup.py
```

### Google Colab-specific Setup

In Google Colab, run:

```python
!git clone https://github.com/yourusername/Text-To-Video-AI.git
%cd Text-To-Video-AI
!python colab_setup.py
```

## Selecting Hardware

The application automatically detects available hardware, but you can force a specific option:

### CPU Only

```bash
python app.py --force-cpu --text "Your script text here"
```

### GPU Only (will fail if GPU not available)

```bash
python app.py --force-gpu --text "Your script text here"
```

### TPU Only (will fail if TPU not available)

```bash
python app.py --force-tpu --text "Your script text here"
```

## Troubleshooting

### Missing edge-tts Module

If you see an error about missing `edge_tts` module:

```
ModuleNotFoundError: No module named 'edge_tts'
```

Run the setup script to install dependencies:

```bash
python setup.py
```

Or install it manually:

```bash
pip install edge-tts
```

### ALSA Audio Issues

If you see ALSA errors:

```
ALSA lib confmisc.c:855:(parse_card) cannot find card '0'
```

Run these commands:

```bash
# For Linux
sudo apt-get update
sudo apt-get install -y alsa-base alsa-utils libasound2-dev portaudio19-dev

# For Colab
!python colab_setup.py
```

### CUDA Errors

If your GPU is not being detected or you're seeing CUDA errors:

1. Verify your GPU is CUDA-capable
2. Ensure you have the correct version of PyTorch for your CUDA version:

```bash
# For CUDA 11.7
pip install torch==2.0.0+cu117 -f https://download.pytorch.org/whl/torch_stable.html
```

## Google Colab Example

Here's a complete example for Google Colab:

```python
# Clone repository
!git clone https://github.com/yourusername/Text-To-Video-AI.git
%cd Text-To-Video-AI

# Install dependencies
!python colab_setup.py

# Run with GPU
!python app.py --force-gpu --text "Interesting facts about space: The Sun makes up 99.86% of our solar system's mass. A day on Venus is longer than its year. Space is completely silent because there is no air to carry sound waves."
```

The output video will be saved as `final_video.mp4` in the current directory. 