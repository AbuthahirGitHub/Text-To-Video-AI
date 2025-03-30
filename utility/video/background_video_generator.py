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

def search_videos(query_string, orientation_landscape=True):
   
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    params = {
        "query": query_string,
        "orientation": "landscape" if orientation_landscape else "portrait",
        "per_page": 15
    }

    response = requests.get(url, headers=headers, params=params)
    json_data = response.json()
    log_response(LOG_TYPE_PEXEL,query_string,response.json())
   
    return json_data


def getBestVideo(query_string, orientation_landscape=True, used_vids=[], attempt=0):
    # If we're on our fallback attempt, use a generic term instead
    if attempt > 0:
        # Select a random generic term that hasn't been used yet
        available_fallbacks = [term for term in GENERIC_FALLBACK_TERMS if term not in used_vids]
        if not available_fallbacks:
            # If all fallbacks are used, reset and try again
            available_fallbacks = GENERIC_FALLBACK_TERMS
        
        query_string = random.choice(available_fallbacks)
        print(f"Using generic fallback video search: '{query_string}'")
    
    # Search for videos
    try:
        vids = search_videos(query_string, orientation_landscape)
        
        # Verify videos exist in the response
        if 'videos' not in vids or not vids['videos']:
            if attempt == 0:
                # Try with a generic term instead
                return getBestVideo(query_string, orientation_landscape, used_vids, attempt=1)
            else:
                print(f"No videos found for fallback term: {query_string}")
                return None
                
        videos = vids['videos']  # Extract the videos list from JSON

        # Filter and extract videos with width and height as 1920x1080 for landscape or 1080x1920 for portrait
        if orientation_landscape:
            filtered_videos = [video for video in videos if video['width'] >= 1920 and video['height'] >= 1080 and video['width']/video['height'] == 16/9]
        else:
            filtered_videos = [video for video in videos if video['width'] >= 1080 and video['height'] >= 1920 and video['height']/video['width'] == 16/9]

        # Sort the filtered videos by duration in ascending order
        sorted_videos = sorted(filtered_videos, key=lambda x: abs(15-int(x['duration'])))

        # Extract the top 3 videos' URLs
        for video in sorted_videos:
            for video_file in video['video_files']:
                if orientation_landscape:
                    if video_file['width'] == 1920 and video_file['height'] == 1080:
                        if not (video_file['link'].split('.hd')[0] in used_vids):
                            return video_file['link']
                else:
                    if video_file['width'] == 1080 and video_file['height'] == 1920:
                        if not (video_file['link'].split('.hd')[0] in used_vids):
                            return video_file['link']
        
        # If we didn't find any matching videos but haven't tried fallback yet, try a generic term
        if attempt == 0:
            print(f"No matching videos found for '{query_string}', trying generic fallback")
            return getBestVideo(query_string, orientation_landscape, used_vids, attempt=1)
        else:
            print(f"No matching videos found for fallback term: {query_string}")
            return None
            
    except Exception as e:
        print(f"Error searching for videos: {str(e)}")
        if attempt == 0:
            # Try with a generic term instead
            return getBestVideo(query_string, orientation_landscape, used_vids, attempt=1)
        else:
            return None
            
    print("NO LINKS found for this round of search with query :", query_string)
    
    # If we get here and haven't tried fallback yet, try with a generic term
    if attempt == 0:
        return getBestVideo(query_string, orientation_landscape, used_vids, attempt=1)
    
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
                print("No specific videos found, using random generic video")
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
            
            timed_video_urls.append([[t1, t2], url])
            
    elif video_server == "stable_diffusion":
        timed_video_urls = get_images_for_video(timed_video_searches)

    return timed_video_urls
