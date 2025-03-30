import os 
import requests
from utility.utils import log_response,LOG_TYPE_PEXEL

PEXELS_API_KEY = os.environ.get('PEXELS_KEY')

# Default fallback videos for different categories
DEFAULT_VIDEOS = {
    "nature": "https://player.vimeo.com/external/451681820.hd.mp4?s=4c8b4e4bb4f4d72d5401e9b56933acd2c8348a6a&profile_id=174&oauth2_token_id=57447761",
    "technology": "https://player.vimeo.com/external/493348284.hd.mp4?s=d95e80ecbdf1d79f4dc2f3d2c72d186c6764fd62&profile_id=174&oauth2_token_id=57447761",
    "abstract": "https://player.vimeo.com/external/459746141.hd.mp4?s=da8e8cf71bcc05503deaabd7bd04878a31bdd42b&profile_id=174&oauth2_token_id=57447761",
    "business": "https://player.vimeo.com/external/449696192.hd.mp4?s=a8326e506357fba26f9d01e9c6e923bc9fc126a3&profile_id=174&oauth2_token_id=57447761",
    "space": "https://player.vimeo.com/external/499024082.hd.mp4?s=b1218ee0f3de6b5e96e2360be639e95cf65bf749&profile_id=174&oauth2_token_id=57447761"
}

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

def get_broader_terms(query_string):
    """
    Generate broader search terms based on specific query.
    This helps when specific queries don't return results.
    """
    # Maps specific terms to broader categories
    broader_categories = {
        "dog": ["animals", "pets", "canine"],
        "cat": ["animals", "pets", "feline"],
        "car": ["vehicle", "transportation", "driving"],
        "building": ["architecture", "city", "structure"],
        "computer": ["technology", "electronics", "digital"],
        "phone": ["technology", "mobile", "communication"],
        "forest": ["nature", "trees", "woodland"],
        "beach": ["coast", "ocean", "sea"],
        "mountain": ["landscape", "nature", "hiking"],
        "food": ["cooking", "meal", "cuisine"],
        "office": ["workplace", "business", "corporate"],
        "home": ["house", "interior", "living"],
        "travel": ["journey", "vacation", "tourism"]
    }
    
    # Check if the query contains any of our specific terms
    broader_terms = []
    for specific, broader in broader_categories.items():
        if specific in query_string.lower():
            broader_terms.extend(broader)
    
    # If no matches, use some general categories
    if not broader_terms:
        broader_terms = ["nature", "landscape", "abstract"]
        
    return broader_terms

def getBestVideo(query_string, orientation_landscape=True, used_vids=[]):
    vids = search_videos(query_string, orientation_landscape)
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
    
    # If no exact resolution match, try with relaxed resolution constraints
    if not sorted_videos and videos:
        # Try with any HD resolution videos
        relaxed_videos = []
        for video in videos:
            for video_file in video['video_files']:
                if orientation_landscape:
                    if video_file['width'] >= 1280 and video_file['height'] >= 720:
                        if not (video_file['link'].split('.hd')[0] in used_vids):
                            return video_file['link']
                else:
                    if video_file['width'] >= 720 and video_file['height'] >= 1280:
                        if not (video_file['link'].split('.hd')[0] in used_vids):
                            return video_file['link']
    
    print("NO LINKS found for this round of search with query:", query_string)
    return None


def generate_video_url(timed_video_searches, video_server):
        timed_video_urls = []
        if video_server == "pexel":
            used_links = []
            for (t1, t2), search_terms in timed_video_searches:
                url = None
                
                # Try each search term in the list
                for query in search_terms:
                    url = getBestVideo(query, orientation_landscape=True, used_vids=used_links)
                    if url:
                        used_links.append(url.split('.hd')[0])
                        break
                
                # If no URL found, try broader terms for each search term
                if not url:
                    for query in search_terms:
                        broader_terms = get_broader_terms(query)
                        for broader_term in broader_terms:
                            url = getBestVideo(broader_term, orientation_landscape=True, used_vids=used_links)
                            if url:
                                used_links.append(url.split('.hd')[0])
                                break
                        if url:
                            break
                
                # If still no URL, use a default fallback video
                if not url:
                    # Determine which category of default video to use
                    category = "nature"  # Default fallback
                    for term in search_terms:
                        if "technology" in term or "computer" in term or "digital" in term:
                            category = "technology"
                            break
                        elif "space" in term or "universe" in term or "galaxy" in term:
                            category = "space"
                            break
                        elif "business" in term or "office" in term or "work" in term:
                            category = "business"
                            break
                    
                    url = DEFAULT_VIDEOS.get(category)
                    print(f"Using fallback video for segment [{t1}-{t2}] with category: {category}")
                
                timed_video_urls.append([[t1, t2], url])
        
        elif video_server == "stable_diffusion":
            timed_video_urls = get_images_for_video(timed_video_searches)

        return timed_video_urls
