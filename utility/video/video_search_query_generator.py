import json
import re
import os
from datetime import datetime

def fix_json(json_str):
    """Fix common JSON formatting issues."""
    # Replace typographical apostrophes with straight quotes
    json_str = json_str.replace("'", "'")
    # Replace any incorrect quotes (e.g., mixed single and double quotes)
    json_str = json_str.replace(""", "\"").replace(""", "\"").replace("'", "\"").replace("'", "\"")
    # Add escaping for quotes within the strings
    json_str = json_str.replace('"you didn"t"', '"you didn\'t"')
    return json_str

def extract_keywords_from_sentence(sentence):
    """Extract keywords from a sentence."""
    # Strip punctuation and convert to lowercase
    clean_sentence = re.sub(r'[^\w\s]', '', sentence.lower())
    
    # Split into words
    words = clean_sentence.split()
    
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 
                 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'like', 'through', 'over', 'before', 
                 'after', 'between', 'under', 'during', 'since', 'without', 'of', 'have', 'has', 'had', 
                 'do', 'does', 'did', 'can', 'could', 'will', 'would', 'should', 'may', 'might', 'must'}
    
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Find significant words (nouns and adjectives are most visual)
    significant_words = []
    
    # Try to extract up to 3 significant keywords
    if len(filtered_words) >= 3:
        significant_words = filtered_words[:3]
    elif len(filtered_words) > 0:
        significant_words = filtered_words
    else:
        # Fallback if no significant words found
        significant_words = ["scenic", "landscape", "nature"]
    
    # If we have single words, try to combine them into meaningful phrases
    if len(significant_words) == 1:
        return [f"{significant_words[0]} scene", f"beautiful {significant_words[0]}", f"{significant_words[0]} view"]
    elif len(significant_words) == 2:
        return [f"{significant_words[0]} {significant_words[1]}", f"{significant_words[1]} {significant_words[0]}", f"beautiful {significant_words[0]}"]
    else:
        return [f"{significant_words[0]} {significant_words[1]}", f"{significant_words[1]} {significant_words[2]}", f"{significant_words[0]} {significant_words[2]}"]

def getVideoSearchQueriesTimed(script, captions_timed):
    """
    Generate video search queries from timed captions without using AI.
    """
    # Check if we have captions to process
    if not captions_timed or len(captions_timed) == 0:
        print("Warning: No timed captions available to generate video search queries")
        return None
    
    try:
        search_terms = []
        
        for caption in captions_timed:
            time_range = caption[0]  # [start_time, end_time]
            text = caption[1]        # caption text
            
            # Extract keywords from each caption
            keywords = extract_keywords_from_sentence(text)
            
            # Add to search terms
            search_terms.append([time_range, keywords])
        
        return search_terms
            
    except Exception as e:
        print(f"Error in video search query generation: {str(e)}")
        
        # Create a basic fallback with generic terms
        if captions_timed:
            end_time = captions_timed[-1][0][1]
            return [[[0, end_time], ["nature", "landscape", "scenery"]]]
   
    return None

def merge_empty_intervals(segments):
    """Merge segments with empty URLs."""
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
