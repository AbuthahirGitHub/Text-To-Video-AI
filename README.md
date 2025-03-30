# Text To Video AI 🔥

Generate video from text using AI (Modified Version - No Script Generation)

This is a modified version of Text To Video AI that removes the AI script generation components. It focuses solely on converting your own text scripts into videos with matching visuals from Pexels.

## Features

- Converts your text into a video with matching visuals
- Uses Pexels API to find relevant videos for your script
- Adds synchronized text-to-speech audio
- Includes captions
- Optimized for performance with GPU support

## Requirements

- Python 3.7+
- Pexels API key

## Setup

Run the following steps:

```
export PEXELS_KEY="your-pexels-key"

pip install -r requirements.txt

python app.py --file "your_script.txt"
```

Or, use the direct text option:

```
python app.py --text "Your script goes here. This is a simplified version that doesn't use AI for script generation."
```

Output will be generated in `final_video.mp4`

## Quick Start

For a simple way to run the code, checkout the Google Colab notebook:

1. Run `!python colab_setup.py` to set up the Colab environment
2. Set your Pexels API key: `os.environ["PEXELS_KEY"]="your-pexels-key"`
3. Run with your script: `!python app.py --file "/content/Text-To-Video-AI/test_script.txt"`

## How It Works

1. You provide the script text
2. The system extracts keywords from your text
3. It searches Pexels for matching videos
4. It generates audio from your text using TTS
5. It combines everything into a final video

## Troubleshooting

If no matching videos are found for a segment, the system will:
1. Try alternative keywords from the same segment
2. Use default videos if no matches are found
3. Merge empty intervals with adjacent segments that have videos

## 💁 Contribution

As an open-source project we are extremely open to contributions.

### Other useful Video AI Projects

[AI Influencer generator](https://github.com/SamurAIGPT/AI-Influencer-Generator)

[AI Youtube Shorts generator](https://github.com/SamurAIGPT/AI-Youtube-Shorts-Generator/)

[Faceless Video Generator](https://github.com/SamurAIGPT/Faceless-Video-Generator)

[AI B-roll generator](https://github.com/Anil-matcha/AI-B-roll)

[AI video generator](https://www.vadoo.tv/ai-video-generator)

[Text to Video AI](https://www.vadoo.tv/text-to-video-ai)

[Autoshorts AI](https://www.vadoo.tv/autoshorts-ai)

[Pixverse alternative](https://www.vadoo.tv/pixverse-ai)

[Hailuo AI alternative](https://www.vadoo.tv/hailuo-ai)

[Minimax AI alternative](https://www.vadoo.tv/minimax-ai)
