#!/usr/bin/env python
"""Quick test for flight search flow - check if form data reaches views and API"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finda.settings')
django.setup()

from django.test import Client
from datetime import datetime, timedelta

client = Client()

# Test flight search form submission
tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

print(f"\n[TEST] Flight search form submission...")
print(f"Origin: IST | Destination: ANK | Date: {tomorrow} | Adults: 1")

response = client.post('/', {
    'origin': 'IST',
    'destination': 'ANK',
    'date': tomorrow,
    'adults': '1'
})

print(f"Status Code: {response.status_code}")

# Check rendered HTML
if response.status_code == 200:
    html = response.content.decode('utf-8')
    
    # Save HTML for inspection
    with open('test_response.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("\n[DEBUG] HTML saved to test_response.html")
    
    # Search for flight results in HTML
    if 'flight-row' in html:
        print("[✓] Flight rows found in HTML")
        # Count flight rows
        count = html.count('flight-row')
        print(f"    Found {count} flight row elements")
    else:
        print("[✗] No flight rows in HTML")
    
    # Check for error message
    if 'Hata:' in html:
        print("[?] Error message detected in HTML")
        # Extract error after "Hata:"
        import re
        errors = re.findall(r'Hata:</strong> ([^<]+)', html)
        if errors:
            print(f"    → Error text: {errors[0]}")
    
    # Check if flight_results context exists in template
    if 'Uçuş Bulundu' in html or 'Uçuş Ara' in html:
        print("[✓] Flight section rendered")
    else:
        print("[✗] Flight section NOT rendered")
        
    # Direct check: is the form populated with values?
    if f'value="{tomorrow}"' in html:
        print("[✓] Form date value persisted")
    else:
        print("[✗] Form date value NOT persisted")

print("\n[TEST] Done")


