"""Intent detection utility for routing queries to product or flight search."""

import re


FLIGHT_KEYWORDS = {
    'tr': ['uçuş', 'bilet', 'uçak', 'hava', 'seyahat', 'havayolu', 'gidiş', 'biniş'],
    'en': ['flight', 'ticket', 'airplane', 'plane', 'fly', 'airport', 'airline', 'trip', 'travel'],
}

TURKISH_CITIES = {
    'istanbul': ['ist', 'iow'],
    'ankara': ['ank', 'esr'],
    'izmir': ['izm', 'adb'],
    'antalya': ['ant', 'gny'],
    'adana': ['adp', 'gwj'],
    'bursa': ['yeg'],
    'gaziantep': ['gno'],
    'bodrum': ['bjv'],
    'alanya': ['acy'],
    'erzurum': ['erz'],
    'kayseri': ['kay'],
    'konya': ['kya'],
    'trabzon': ['trz'],
}


def detect_flight_intent(query):
    """
    Detect if a query is flight-related.
    
    Returns:
        dict: {'is_flight': bool, 'confidence': float, 'reason': str}
    """
    if not query or not isinstance(query, str):
        return {'is_flight': False, 'confidence': 0.0, 'reason': 'empty'}
    
    query_lower = query.lower().strip()
    
    # Check for exact city code patterns (e.g., "ist ank")
    city_code_pattern = r'\b([a-z]{3})\s+([a-z]{3})\b'
    if re.search(city_code_pattern, query_lower):
        return {'is_flight': True, 'confidence': 0.9, 'reason': 'city_code_pattern'}
    
    # Check for flight keywords in Turkish
    for keyword in FLIGHT_KEYWORDS['tr']:
        if keyword in query_lower:
            return {'is_flight': True, 'confidence': 0.8, 'reason': f'keyword_tr: {keyword}'}
    
    # Check for flight keywords in English
    for keyword in FLIGHT_KEYWORDS['en']:
        if keyword in query_lower:
            return {'is_flight': True, 'confidence': 0.8, 'reason': f'keyword_en: {keyword}'}
    
    # Check for city name patterns (e.g., "istanbul ankara", "ankara to istanbul")
    cities_pattern = '|'.join(list(TURKISH_CITIES.keys()))
    if re.search(rf'\b({cities_pattern})\b.*\b({cities_pattern})\b', query_lower):
        return {'is_flight': True, 'confidence': 0.85, 'reason': 'city_names'}
    
    # Check for "to" or "->" patterns with cities
    if re.search(r'\b(?:to|den|dan|\'dan|from)\b', query_lower):
        if re.search(rf'\b({cities_pattern})\b', query_lower):
            return {'is_flight': True, 'confidence': 0.7, 'reason': 'city_with_direction'}
    
    # Check for date patterns (YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY)
    date_pattern = r'(\d{4}-\d{2}-\d{2}|\d{2}[./]\d{2}[./]\d{4})'
    has_date = bool(re.search(date_pattern, query))
    
    # If has date + city code/keyword = likely flight
    if has_date and (re.search(city_code_pattern, query_lower) or 
                     any(kw in query_lower for kw in FLIGHT_KEYWORDS['tr'] + FLIGHT_KEYWORDS['en'])):
        return {'is_flight': True, 'confidence': 0.9, 'reason': 'date_with_flight_marker'}
    
    return {'is_flight': False, 'confidence': 0.0, 'reason': 'no_flight_markers'}
