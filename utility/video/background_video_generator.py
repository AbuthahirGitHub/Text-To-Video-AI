import os 
import requests
import random
from utility.utils import log_response,LOG_TYPE_PEXEL

PEXELS_API_KEY = os.environ.get('PEXELS_KEY')

# Define a list of generic fallback search terms
GENERIC_FALLBACK_TERMS = [
    "ocean",
    "sky",
    "sunset",
    "mountains",
    "forest",
    "water",
    "beach",
    "clouds",
    "waterfall",
    "lake",
    "city",
    "stars",
    "nature",
    "desert",
    "snow",
    "river",
    "trees",
    "flowers",
    "sunrise",
    "planet"
]

# Emergency fallback terms to use when everything else fails
EMERGENCY_FALLBACK_TERMS = [
    "background",
    "texture",
    "pattern",
    "abstract",
    "color"
]

def search_videos(query_string, orientation_landscape=True, ignore_orientation=False):
   
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    params = {
        "query": query_string,
        "per_page": 15
    }
    
    # Only specify orientation if we're not ignoring it
    if not ignore_orientation:
        params["orientation"] = "landscape" if orientation_landscape else "portrait"

    response = requests.get(url, headers=headers, params=params)
    json_data = response.json()
    log_response(LOG_TYPE_PEXEL,query_string,response.json())
   
    return json_data


def getBestVideo(query_string, orientation_landscape=True, used_vids=[], attempt=0):
    # If we're on fallback attempts, use different strategies
    if attempt == 1:
        # First fallback: Use a generic term
        available_fallbacks = [term for term in GENERIC_FALLBACK_TERMS if term not in used_vids]
        if not available_fallbacks:
            available_fallbacks = GENERIC_FALLBACK_TERMS
        
        query_string = random.choice(available_fallbacks)
        print(f"Using generic fallback video search: '{query_string}'")
    elif attempt == 2:
        # Second fallback: Use an emergency term
        query_string = random.choice(EMERGENCY_FALLBACK_TERMS)
        print(f"Using emergency fallback video search: '{query_string}'")
    elif attempt == 3:
        # Third fallback: Random with any orientation
        # Just search for "video" to get anything
        query_string = "video"
        print("Searching for ANY video, ignoring orientation and quality requirements")
        
    # Determine if we should ignore orientation requirements for this attempt
    ignore_orientation = (attempt >= 3)
    
    # Search for videos
    try:
        vids = search_videos(query_string, orientation_landscape, ignore_orientation)
        
        # Verify videos exist in the response
        if 'videos' not in vids or not vids['videos']:
            if attempt < 3:
                # Try with next fallback level
                return getBestVideo(query_string, orientation_landscape, used_vids, attempt=attempt+1)
            else:
                print(f"Exhausted all fallback options, no videos found for '{query_string}'")
                return None
                
        videos = vids['videos']  # Extract the videos list from JSON

        # For last attempt, accept any video with reasonable dimensions
        if attempt >= 3:
            # Just get the first video with reasonable quality
            for video in videos:
                for video_file in video['video_files']:
                    if video_file['width'] >= 640 and video_file['height'] >= 360:
                        return video_file['link']
        
        # Filter and extract videos with appropriate dimensions
        if orientation_landscape:
            filtered_videos = [video for video in videos if video['width'] >= 1920 and video['height'] >= 1080 and video['width']/video['height'] == 16/9]
        else:
            filtered_videos = [video for video in videos if video['width'] >= 1080 and video['height'] >= 1920 and video['height']/video['width'] == 16/9]

        # If no perfect matches but we're on attempt 2+, be more lenient with ratios
        if not filtered_videos and attempt >= 2:
            if orientation_landscape:
                filtered_videos = [video for video in videos if video['width'] >= 1280 and video['height'] >= 720 and video['width'] > video['height']]
            else:
                filtered_videos = [video for video in videos if video['width'] >= 720 and video['height'] >= 1280 and video['height'] > video['width']]

        # Sort the filtered videos by duration in ascending order
        sorted_videos = sorted(filtered_videos, key=lambda x: abs(15-int(x['duration'])))

        # Extract the videos' URLs
        for video in sorted_videos:
            for video_file in video['video_files']:
                # Original strict criteria
                if attempt < 2:
                    if orientation_landscape:
                        if video_file['width'] == 1920 and video_file['height'] == 1080:
                            if not (video_file['link'].split('.hd')[0] in used_vids):
                                return video_file['link']
                    else:
                        if video_file['width'] == 1080 and video_file['height'] == 1920:
                            if not (video_file['link'].split('.hd')[0] in used_vids):
                                return video_file['link']
                # More lenient criteria for fallbacks
                else:
                    if orientation_landscape:
                        if video_file['width'] >= 1280 and video_file['height'] >= 720 and video_file['width'] > video_file['height']:
                            if not (video_file['link'].split('.hd')[0] in used_vids):
                                return video_file['link']
                    else:
                        if video_file['width'] >= 720 and video_file['height'] >= 1280 and video_file['height'] > video_file['width']:
                            if not (video_file['link'].split('.hd')[0] in used_vids):
                                return video_file['link']
        
        # If we still didn't find any matching videos but haven't tried all fallbacks
        if attempt < 3:
            print(f"No matching videos found for '{query_string}', trying next fallback level")
            return getBestVideo(query_string, orientation_landscape, used_vids, attempt=attempt+1)
        else:
            # Last resort: just return any video file from the first video
            if videos and len(videos) > 0 and 'video_files' in videos[0] and len(videos[0]['video_files']) > 0:
                print(f"Using last resort video with non-ideal dimensions")
                return videos[0]['video_files'][0]['link']
            else:
                print("Completely failed to find any usable video")
                return None
            
    except Exception as e:
        print(f"Error searching for videos: {str(e)}")
        if attempt < 3:
            # Try with next fallback level
            return getBestVideo(query_string, orientation_landscape, used_vids, attempt=attempt+1)
        else:
            return None
    
    # If we get here, try next fallback level
    if attempt < 3:
        return getBestVideo(query_string, orientation_landscape, used_vids, attempt=attempt+1)
    
    print("Exhausted all options, no videos found")
    return None


def generate_video_url(timed_video_searches, video_server):
    timed_video_urls = []
    if video_server == "pexel":
        used_links = []
        used_fallback_terms = []
        
        for (t1, t2), search_terms in timed_video_searches:
            url = None
            
            # Try the specific search terms first
            for query in search_terms:
                url = getBestVideo(query, orientation_landscape=True, used_vids=used_links)
                if url:
                    used_links.append(url.split('.hd')[0])
                    break
            
            # If no video was found, try a random generic term
            if not url:
                print("No specific videos found, using fallback video")
                # Get a random term we haven't used yet
                available_terms = [term for term in GENERIC_FALLBACK_TERMS if term not in used_fallback_terms]
                if not available_terms:
                    # If all terms are used, reset
                    available_terms = GENERIC_FALLBACK_TERMS
                    used_fallback_terms = []
                
                fallback_term = random.choice(available_terms)
                used_fallback_terms.append(fallback_term)
                
                url = getBestVideo(fallback_term, orientation_landscape=True, used_vids=used_links)
                if url:
                    used_links.append(url.split('.hd')[0])
                    print(f"Using fallback video for '{fallback_term}'")
            
            # If STILL no video, we'll have tried all fallback mechanisms in getBestVideo,
            # including emergency terms and even "anything with decent dimensions"
            if not url:
                print("WARNING: Using default placeholder video URL - all fallbacks failed")
                # Hardcoded fallback to a reliable Pexels video as absolute last resort
                url = "https://player.vimeo.com/external/368320203.hd.mp4?s=050513f8c83b9e5552132ca0497fce60b0a9af48&profile_id=175&oauth2_token_id=57447761"
            
            timed_video_urls.append([[t1, t2], url])
            
    elif video_server == "stable_diffusion":
        timed_video_urls = get_images_for_video(timed_video_searches)

    return timed_video_urls
