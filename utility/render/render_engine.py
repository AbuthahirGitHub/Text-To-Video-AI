import time
import os
import tempfile
import zipfile
import platform
import subprocess
from moviepy.editor import (AudioFileClip, CompositeVideoClip, CompositeAudioClip, ImageClip,
                            TextClip, VideoFileClip)
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
import requests

def download_file(url, filename):
    with open(filename, 'wb') as f:
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        f.write(response.content)

def search_program(program_name):
    try: 
        search_cmd = "where" if platform.system() == "Windows" else "which"
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_program_path(program_name):
    program_path = search_program(program_name)
    return program_path

def get_output_media(audio_file_path, timed_captions, background_video_data, video_server):
    OUTPUT_FILE_NAME = "rendered_video.mp4"
    magick_path = get_program_path("magick")
    print(f"ImageMagick path: {magick_path}")
    if magick_path:
        os.environ['IMAGEMAGICK_BINARY'] = magick_path
    else:
        os.environ['IMAGEMAGICK_BINARY'] = '/usr/bin/convert'
    
    visual_clips = []
    
    print(f"Processing {len(background_video_data)} background video segments...")
    
    # Track downloaded files for cleanup
    downloaded_files = []
    
    try:
        # Download and process each video segment
        for i, ((t1, t2), video_url) in enumerate(background_video_data):
            try:
                print(f"Processing segment {i+1}/{len(background_video_data)}: {t1:.2f}-{t2:.2f}")
                
                # Skip any None URLs (should not happen with our improved code)
                if video_url is None:
                    print(f"WARNING: No video URL for segment {t1:.2f}-{t2:.2f}, skipping")
                    continue
                
                # Download the video file
                video_filename = tempfile.NamedTemporaryFile(delete=False).name
                print(f"Downloading video for segment {t1:.2f}-{t2:.2f}...")
                
                download_file(video_url, video_filename)
                downloaded_files.append(video_filename)
                
                # Create VideoFileClip from the downloaded file
                print(f"Creating clip for segment {t1:.2f}-{t2:.2f}...")
                video_clip = VideoFileClip(video_filename)
                
                # Handle videos that are shorter than needed
                if video_clip.duration < (t2 - t1):
                    print(f"WARNING: Video is shorter than needed segment ({video_clip.duration}s < {t2-t1}s)")
                    # Loop the video if it's shorter than needed
                    repeat = int((t2 - t1) / video_clip.duration) + 1
                    video_clip = video_clip.loop(n=repeat)
                
                video_clip = video_clip.set_start(t1)
                video_clip = video_clip.set_end(t2)
                visual_clips.append(video_clip)
                
            except Exception as e:
                print(f"ERROR processing video segment {t1:.2f}-{t2:.2f}: {str(e)}")
                # Continue with other segments
                continue
        
        print("Creating audio track...")
        audio_clips = []
        audio_file_clip = AudioFileClip(audio_file_path)
        audio_clips.append(audio_file_clip)

        print("Adding captions...")
        for i, ((t1, t2), text) in enumerate(timed_captions):
            try:
                if i % 10 == 0:  # Print progress every 10 captions
                    print(f"Processing caption {i+1}/{len(timed_captions)}...")
                text_clip = TextClip(txt=text, fontsize=100, color="white", stroke_width=3, stroke_color="black", method="label")
                text_clip = text_clip.set_start(t1)
                text_clip = text_clip.set_end(t2)
                text_clip = text_clip.set_position(["center", 800])
                visual_clips.append(text_clip)
            except Exception as e:
                print(f"ERROR processing caption at {t1:.2f}-{t2:.2f}: {str(e)}")
                continue

        if not visual_clips:
            print("ERROR: No visual clips to render!")
            return None
            
        print("Compositing video clips...")
        video = CompositeVideoClip(visual_clips)
        
        if audio_clips:
            print("Adding audio to video...")
            audio = CompositeAudioClip(audio_clips)
            video.duration = audio.duration
            video.audio = audio

        print(f"Rendering final video to {OUTPUT_FILE_NAME}...")
        print("This may take some time depending on video length and complexity.")
        print("Progress indicators will appear below:")
        
        # Increased preset speed to 'ultrafast' for faster rendering but lower quality
        # Can be adjusted back to 'veryfast' for better quality
        video.write_videofile(
            OUTPUT_FILE_NAME, 
            codec='libx264', 
            audio_codec='aac', 
            fps=25, 
            preset='ultrafast',  # Faster rendering, lower quality
            threads=4,  # Use multiple threads
            logger=None  # Use default logger
        )
        
        print("Video rendering completed successfully!")
        
    except Exception as e:
        print(f"CRITICAL ERROR during video rendering: {str(e)}")
        return None
    finally:
        # Clean up downloaded files
        print("Cleaning up temporary files...")
        for filename in downloaded_files:
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except Exception as e:
                print(f"Warning: Could not remove temporary file {filename}: {str(e)}")

    return OUTPUT_FILE_NAME
