#!/usr/bin/env python3
"""
Test skript pro analýzu struktury Kosmas.cz
"""

import requests
from bs4 import BeautifulSoup

# Stáhneme stránku
url = "https://www.kosmas.cz/novinky/"
print(f"Stahuji: {url}")
response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')

# Krok 1: Najdeme hlavní kontejner
print("\n=== KROK 1: Hledám div.grid-items__pagenumber ===")
container = soup.find('div', class_='grid-items__pagenumber')
if container:
    print("✓ Kontejner nalezen")
else:
    print("✗ Kontejner NENALEZEN")
    exit(1)

# Krok 2: Najdeme všechny items
print("\n=== KROK 2: Hledám div.grid-item ===")
items = container.find_all('div', class_='grid-item')
print(f"✓ Nalezeno {len(items)} položek")

# Krok 3: Analyzujeme první položku
if items:
    print("\n=== KROK 3: Analyzuji první položku ===")
    first_item = items[0]
    
    # Najdeme title
    print("\n--- Hledám h3.g-item__title ---")
    title_elem = first_item.find('h3', class_='g-item__title')
    if title_elem:
        print(f"✓ Title element nalezen")
        print(f"  Text: {title_elem.get_text(strip=True)[:80]}...")
    else:
        print("✗ Title element NENALEZEN")
    
    # Najdeme link (a pod h3)
    print("\n--- Hledám <a> pod <h3> ---")
    if title_elem:
        link_elem = title_elem.find('a', href=True)
        if link_elem:
            print(f"✓ Link nalezen")
            print(f"  URL: {link_elem['href']}")
        else:
            print("✗ Link NENALEZEN")
    
    # Najdeme autory
    print("\n--- Hledám span.titul-author ---")
    author_span = first_item.find('span', class_='titul-author')
    authors = []
    if author_span:
        print(f"✓ Author span nalezen")
        author_links = author_span.find_all('a')
        if author_links:
            authors = [a.get_text(strip=True) for a in author_links]
            print(f"✓ Nalezeno {len(authors)} autorů: {', '.join(authors)}")
        else:
            print("✗ Autoři NENALEZENI v <a> tazích")
    else:
        print("✗ Author span NENALEZEN")
    
    # Vytvoříme description z title a autorů
    print("\n--- Vytvářím description ---")
    if title_elem and authors:
        title_text = title_elem.get_text(strip=True)
        description = f"{title_text} - {', '.join(authors)}"
        print(f"✓ Description: {description}")
    elif title_elem:
        description = title_elem.get_text(strip=True)
        print(f"✓ Description (bez autorů): {description}")
    else:
        print("✗ Nelze vytvořit description")

print("\n=== HOTOVO ===")
