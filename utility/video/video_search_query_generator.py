import os
import json
import re
from datetime import datetime

def extract_keywords(text, captions):
    """
    Extract simple keywords from script text without using AI.
    
    Args:
        text (str): The script text
        captions (list): Timed captions
        
    Returns:
        list: A list of time-based keywords
    """
    # Extract basic keywords from the captions
    keywords = []
    
    # Common boring words to exclude
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
        'of', 'in', 'to', 'for', 'with', 'by', 'at', 'from', 'about', 
        'as', 'that', 'this', 'these', 'those', 'it', 'its', 'have', 'has',
        'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
        'must', 'need', 'shall', 'may', 'might', 'can', 'cannot'
    }
    
    # Visual context words to add
    visual_context = {
        'business': ['office', 'meeting', 'corporate'],
        'technology': ['computer', 'digital', 'tech'],
        'nature': ['landscape', 'outdoor', 'scenery'],
        'people': ['crowd', 'group', 'people'],
        'city': ['urban', 'cityscape', 'metropolitan'],
        'food': ['cooking', 'restaurant', 'cuisine'],
        'health': ['fitness', 'wellness', 'medical'],
        'education': ['classroom', 'learning', 'education'],
        'sports': ['sports', 'athletics', 'game'],
        'music': ['concert', 'music', 'performance'],
        'art': ['artwork', 'gallery', 'creative'],
        'science': ['laboratory', 'research', 'science'],
        'travel': ['travel', 'tourism', 'adventure'],
        'fashion': ['fashion', 'style', 'clothing'],
        'environment': ['environment', 'climate', 'sustainability']
    }
    
    # Go through each caption
    for i, caption in enumerate(captions):
        time_range, text = caption
        
        # Simple keyword extraction: split by spaces and remove stop words
        words = [word.lower() for word in re.findall(r'\b\w+\b', text)]
        filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Get up to 3 keywords for this segment
        segment_keywords = filtered_words[:3]
        
        if segment_keywords:
            # Add visual context based on keywords
            for word in segment_keywords:
                for context, related in visual_context.items():
                    if word in context or context in word:
                        segment_keywords.extend(related)
                        break
            
            # Remove duplicates and limit to 3 keywords
            segment_keywords = list(set(segment_keywords))[:3]
            
            # Add this segment with timing and keywords
            keywords.append([time_range, segment_keywords])
    
    # If no keywords were extracted, use some defaults
    if not keywords:
        end_time = 10.0
        if captions and captions[-1][0][1]:
            end_time = captions[-1][0][1]
            
        keywords = [
            [[0, end_time/3], ["nature", "landscape", "scenery"]],
            [[end_time/3, 2*end_time/3], ["timelapse", "sunset", "mountains"]],
            [[2*end_time/3, end_time], ["water", "ocean", "waves"]]
        ]
    
    return keywords

def getVideoSearchQueriesTimed(script, captions_timed):
    """
    Get video search queries based on time segments without using AI.
    
    Args:
        script (str): The script text
        captions_timed (list): List of timed captions
        
    Returns:
        list: A list of time-based keywords for video search
    """
    # Check if we have captions to process
    if not captions_timed or len(captions_timed) == 0:
        print("Warning: No timed captions available to generate video search queries")
        
        # Create dummy captions if none provided
        if script:
            import re
            sentences = re.split(r'(?<=[.!?])\s+', script)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Create simple timed captions (3 seconds per sentence)
            captions_timed = []
            current_time = 0
            for sentence in sentences:
                captions_timed.append([[current_time, current_time + 3], sentence])
                current_time += 3
                
            if not captions_timed:
                return None
        else:
            return None
    
    try:
        # Extract keywords without AI
        search_terms = extract_keywords(script, captions_timed)
        return search_terms
    except Exception as e:
        print(f"Error in video search query generation: {e}")
        
        # Fallback to basic keywords
        if captions_timed and len(captions_timed) > 0:
            end = captions_timed[-1][0][1]
            return [[[0, end], ["nature", "landscape", "scenery"]]]
   
    return None

def merge_empty_intervals(segments):
    """Merge intervals with empty content."""
    if not segments:
        return None
        
    merged = []
    i = 0
    while i < len(segments):
        interval, url = segments[i]
        if url is None:
            # Find consecutive None intervals
            j = i + 1
            while j < len(segments) and segments[j][1] is None:
                j += 1
            
            # Merge consecutive None intervals with the previous valid URL
            if i > 0:
                prev_interval, prev_url = merged[-1]
                if prev_url is not None and prev_interval[1] == interval[0]:
                    merged[-1] = [[prev_interval[0], segments[j-1][0][1]], prev_url]
                else:
                    merged.append([interval, prev_url])
            else:
                merged.append([interval, None])
            
            i = j
        else:
            merged.append([interval, url])
            i += 1
    
    return merged