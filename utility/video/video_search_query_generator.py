import os
import json
import re
from datetime import datetime

# Define common visual replacements for technical/abstract terms
VISUAL_REPLACEMENTS = {
    # Medical/Healthcare
    'medical': ['hospital', 'doctor', 'healthcare', 'nurse', 'patient care'],
    'healthcare': ['hospital', 'doctor', 'medical care', 'patient care'],
    'hcpcs': ['medical coding', 'healthcare office', 'medical document'],
    'reimbursement': ['money', 'payment', 'financial', 'office'],
    'billing': ['invoice', 'payment', 'office work', 'paperwork'],
    'claim': ['document', 'paperwork', 'office work'],
    'compliant': ['checklist', 'approval', 'agreement', 'handshake'],
    'compliance': ['checklist', 'legal document', 'verification'],
    'insurance': ['protection', 'safety', 'contract', 'agreement'],
    'payment': ['money', 'cash', 'financial', 'transaction'],
    'underpaid': ['money problem', 'financial issue', 'payment dispute'],
    'discrepancies': ['difference', 'error', 'problem', 'confusion'],
    'ensures': ['guarantee', 'verification', 'confirmation', 'quality'],
    'provider': ['professional', 'expert', 'specialist', 'doctor'],
    'submits': ['delivery', 'sending', 'paperwork', 'documentation'],
    
    # Generic fallbacks for abstract concepts
    'process': ['workflow', 'steps', 'procedure', 'method'],
    'system': ['organization', 'structure', 'network', 'framework'],
    'service': ['assistance', 'support', 'help', 'customer service'],
    'quality': ['excellence', 'premium', 'best', 'superior'],
    'policy': ['rules', 'regulation', 'guidelines', 'standards'],
    'management': ['leadership', 'supervision', 'direction', 'control'],
    'solution': ['answer', 'resolution', 'fix', 'remedy']
}

# List of general visual concepts to use as fallbacks
GENERIC_VISUALS = [
    ["office", "business", "professional"],
    ["teamwork", "collaboration", "meeting"],
    ["computer", "technology", "digital"],
    ["document", "paperwork", "contract"],
    ["success", "achievement", "growth"],
    ["people working", "professional", "business"],
    ["data", "analytics", "charts"],
    ["time management", "clock", "schedule"],
    ["customer service", "help", "support"],
    ["finance", "money", "investment"]
]

def get_visual_replacement(word):
    """Get a visually concrete replacement for an abstract word."""
    word = word.lower()
    if word in VISUAL_REPLACEMENTS:
        replacements = VISUAL_REPLACEMENTS[word]
        return replacements[0]  # Return the first replacement
    return word

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
        'as', 'that', 'this', 'these', 'those', 'it', 'its', 'their',
        'they', 'them', 'when', 'where', 'how', 'what', 'why', 'who'
    }
    
    # Go through each caption
    for i, caption in enumerate(captions):
        time_range, text = caption
        
        # Simple keyword extraction: split by spaces and remove stop words
        words = [word.lower() for word in re.findall(r'\b\w+\b', text)]
        filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Get up to 3 keywords for this segment
        segment_keywords = filtered_words[:3]
        
        # Replace abstract terms with visual concepts
        visual_keywords = []
        for word in segment_keywords:
            visual_keywords.append(get_visual_replacement(word))
        
        # If we have keywords, use them (otherwise will use default fallbacks)
        if visual_keywords:
            # Add specialized visualization keywords for certain topics
            if any(word in ['space', 'universe', 'galaxy', 'planet', 'star'] for word in visual_keywords):
                visual_keywords = ['space', 'stars', 'galaxy']
            elif any(word in ['animal', 'animals', 'wildlife', 'nature'] for word in visual_keywords):
                visual_keywords = ['animals', 'wildlife', 'nature']
            elif any(word in ['ocean', 'sea', 'water', 'marine'] for word in visual_keywords):
                visual_keywords = ['ocean', 'waves', 'underwater']
            elif any(word in ['medical', 'healthcare', 'hospital', 'doctor'] for word in visual_keywords):
                visual_keywords = ['healthcare', 'medical', 'hospital']
            elif any(word in ['business', 'office', 'professional', 'corporate'] for word in visual_keywords):
                visual_keywords = ['business', 'office', 'professional']
            
            # Ensure we have exactly 3 keywords (padding if needed)
            while len(visual_keywords) < 3:
                visual_keywords.append("business" if len(visual_keywords) == 0 else 
                                      "office" if len(visual_keywords) == 1 else 
                                      "professional")
                
            # Add this segment with timing and keywords
            keywords.append([time_range, visual_keywords[:3]])  # Limit to top 3
    
    # If no keywords were extracted, use generic business visuals
    if not keywords:
        end_time = 10.0
        if captions and captions[-1][0][1]:
            end_time = captions[-1][0][1]
            
        # Generate even segments with generic business visuals
        segment_count = min(len(GENERIC_VISUALS), 5)  # Up to 5 segments
        segment_length = end_time / segment_count
        
        for i in range(segment_count):
            start_time = i * segment_length
            end_time_seg = (i + 1) * segment_length
            keywords.append([
                [start_time, end_time_seg], 
                GENERIC_VISUALS[i % len(GENERIC_VISUALS)]
            ])
    
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
        
        # Fallback to basic keywords that will definitely find videos
        if captions_timed and len(captions_timed) > 0:
            end = captions_timed[-1][0][1]
            return [[[0, end], ["office", "business", "professional"]]]
   
    return None

def merge_empty_intervals(segments):
    """Merge intervals with empty content."""
    if not segments:
        # Return a default video if no segments found
        return [[[0, 10], ["office", "business", "professional"]]]
        
    # Check if all segments have no videos
    all_empty = all(url is None for _, url in segments)
    if all_empty:
        print("No videos found for any search term. Using default business videos.")
        # Return a single segment with business-related search terms
        end_time = segments[-1][0][1] if segments else 10
        return [[[0, end_time], ["office", "business", "professional"]]]
        
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
                    # Use a default video instead of None
                    merged.append([interval, ["office", "business", "professional"]])
            else:
                # Use a default video at the beginning
                merged.append([interval, ["office", "business", "professional"]])
            
            i = j
        else:
            merged.append([interval, url])
            i += 1
    
    return merged