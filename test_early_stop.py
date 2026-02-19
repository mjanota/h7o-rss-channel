#!/usr/bin/env python3
"""
Test, který ověří přestahování 5 nejnovějších položek
"""

import json
import os
from kosmas_generator import KosmasRSSGenerator
from rss_generator import H7oRSSGenerator


def test_kosmas_refetch_5_newest():
    """Test přestahování 5 nejnovějších položek pro Kosmas"""
    print("=== Test Kosmas - Přestahování 5 nejnovějších ===\n")
    
    # Nejprve zjistíme, co je aktuálně na první stránce
    print("1. Stahuji první stránku webu pro zjištění aktuálního stavu...")
    gen = KosmasRSSGenerator()
    soup = gen.fetch_page(1)
    if not soup:
        print("❌ Chyba při stahování první stránky")
        return
    
    current_items = gen.extract_items_from_page(soup)
    print(f"   → Na první stránce je {len(current_items)} položek")
    
    if len(current_items) < 5:
        print(f"❌ Na první stránce je jen {len(current_items)} položek, očekáváno alespoň 5")
        return
    
    # Vezmeme prvních 5 položek z první stránky
    top_5_from_web = current_items[:5]
    top_5_urls = [item['url'] for item in top_5_from_web]
    top_5_titles = [item['title'] for item in top_5_from_web]
    
    print("\n2. Prvních 5 položek z první stránky webu:")
    for i, title in enumerate(top_5_titles, 1):
        print(f"   {i}. {title}")
    
    # Načteme existující cache
    print("\n3. Načítám cache...")
    if not os.path.exists('kosmas_cache.json'):
        print("❌ Není k dispozici kosmas_cache.json pro test")
        return
        
    with open('kosmas_cache.json', 'r', encoding='utf-8') as f:
        full_cache = json.load(f)
    
    print(f"   → Původní cache: {len(full_cache)} položek")
    
    # Odebereme těch 5 položek z cache
    cache_urls = {item['url'] for item in full_cache}
    removed_count = sum(1 for url in top_5_urls if url in cache_urls)
    
    cache_without_5 = [item for item in full_cache if item['url'] not in top_5_urls]
    
    print(f"   → Odeberu {removed_count} položek z cache")
    
    # Uložíme upravenou cache
    with open('kosmas_cache.json', 'w', encoding='utf-8') as f:
        json.dump(cache_without_5, f, ensure_ascii=False, indent=2)
    
    print(f"   ✓ Upravená cache uložena: {len(cache_without_5)} položek")
    
    print("\n4. Spouštím Kosmas generátor...")
    print("   Měl by najít těch 5 vynechaných položek.\n")
    
    # Spustíme generátor
    gen = KosmasRSSGenerator()
    gen.run()
    
    # Načteme aktualizovanou cache
    print("\n5. Kontrola výsledku...")
    with open('kosmas_cache.json', 'r', encoding='utf-8') as f:
        new_cache = json.load(f)
    
    # Ověříme, že se 5 položek vrátilo
    new_cache_urls = {item['url'] for item in new_cache}
    found_count = sum(1 for url in top_5_urls if url in new_cache_urls)
    
    print(f"\n{'='*60}")
    print(f"VÝSLEDEK: Nalezeno {found_count} z {removed_count} vynechaných položek")
    if found_count == removed_count and removed_count > 0:
        print(f"✅ TEST ÚSPĚŠNÝ - všech {removed_count} položek bylo znovu staženo!")
    elif found_count > 0:
        print(f"⚠️  Nalezeno jen {found_count}/{removed_count} položek")
        print("Chybějící položky:")
        for url, title in zip(top_5_urls, top_5_titles):
            if url not in new_cache_urls:
                print(f"  - {title}")
    else:
        print(f"❌ TEST SELHAL - žádné položky nebyly staženy")
    print(f"{'='*60}")


def test_h7o_refetch_5_newest():
    """Test přestahování 5 nejnovějších článků pro H7O"""
    print("\n\n=== Test H7O - Přestahování 5 nejnovějších ===\n")
    
    # Nejprve zjistíme, co je aktuálně na první stránce
    print("1. Stahuji první stránku webu pro zjištění aktuálního stavu...")
    gen = H7oRSSGenerator()
    soup = gen.fetch_page(1)
    if not soup:
        print("❌ Chyba při stahování první stránky")
        return
    
    current_articles = gen.extract_articles_from_page(soup)
    print(f"   → Na první stránce je {len(current_articles)} článků")
    
    if len(current_articles) < 5:
        print(f"❌ Na první stránce je jen {len(current_articles)} článků, očekáváno alespoň 5")
        return
    
    # Vezmeme prvních 5 článků z první stránky
    top_5_from_web = current_articles[:5]
    top_5_urls = [item['url'] for item in top_5_from_web]
    top_5_titles = [item['title'] for item in top_5_from_web]
    
    print("\n2. Prvních 5 článků z první stránky webu:")
    for i, title in enumerate(top_5_titles, 1):
        print(f"   {i}. {title}")
    
    # Načteme existující cache
    print("\n3. Načítám cache...")
    if not os.path.exists('articles_cache.json'):
        print("❌ Není k dispozici articles_cache.json pro test")
        return
        
    with open('articles_cache.json', 'r', encoding='utf-8') as f:
        full_cache = json.load(f)
    
    print(f"   → Původní cache: {len(full_cache)} článků")
    
    # Odebereme těch 5 článků z cache
    cache_urls = {item['url'] for item in full_cache}
    removed_count = sum(1 for url in top_5_urls if url in cache_urls)
    
    cache_without_5 = [item for item in full_cache if item['url'] not in top_5_urls]
    
    print(f"   → Odeberu {removed_count} článků z cache")
    
    # Uložíme upravenou cache
    with open('articles_cache.json', 'w', encoding='utf-8') as f:
        json.dump(cache_without_5, f, ensure_ascii=False, indent=2)
    
    print(f"   ✓ Upravená cache uložena: {len(cache_without_5)} článků")
    
    print("\n4. Spouštím H7O generátor...")
    print("   Měl by najít těch 5 vynechaných článků.\n")
    
    # Spustíme generátor
    gen = H7oRSSGenerator()
    gen.run()
    
    # Načteme aktualizovanou cache
    print("\n5. Kontrola výsledku...")
    with open('articles_cache.json', 'r', encoding='utf-8') as f:
        new_cache = json.load(f)
    
    # Ověříme, že se 5 článků vrátilo
    new_cache_urls = {item['url'] for item in new_cache}
    found_count = sum(1 for url in top_5_urls if url in new_cache_urls)
    
    print(f"\n{'='*60}")
    print(f"VÝSLEDEK: Nalezeno {found_count} z {removed_count} vynechaných článků")
    if found_count == removed_count and removed_count > 0:
        print(f"✅ TEST ÚSPĚŠNÝ - všech {removed_count} článků bylo znovu staženo!")
    elif found_count > 0:
        print(f"⚠️  Nalezeno jen {found_count}/{removed_count} článků")
        print("Chybějící články:")
        for url, title in zip(top_5_urls, top_5_titles):
            if url not in new_cache_urls:
                print(f"  - {title}")
    else:
        print(f"❌ TEST SELHAL - žádné články nebyly staženy")
    print(f"{'='*60}")


if __name__ == "__main__":
    # Výběr testu
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'kosmas':
            test_kosmas_refetch_5_newest()
        elif sys.argv[1] == 'h7o':
            test_h7o_refetch_5_newest()
        else:
            print("Použití: python test_early_stop.py [kosmas|h7o]")
    else:
        print("Spouštím oba testy...\n")
        test_kosmas_refetch_5_newest()
        test_h7o_refetch_5_newest()

