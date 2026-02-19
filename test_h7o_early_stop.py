#!/usr/bin/env python3
"""
Test H7O early stop logiky
"""

import json
import os
from rss_generator import H7oRSSGenerator


def test_h7o_early_stop():
    """Test early stop pro H7O generátor"""
    print("=== Test H7O Early Stop ===\n")
    
    # Načteme existující cache
    if not os.path.exists('articles_cache.json'):
        print("❌ Není k dispozici articles_cache.json pro test")
        return
        
    with open('articles_cache.json', 'r', encoding='utf-8') as f:
        full_cache = json.load(f)
    
    print(f"Celková cache: {len(full_cache)} článků")
    
    # Vytvoříme částečnou cache - jen prvních 20 článků
    partial_cache = full_cache[:20]
    
    # Uložíme částečnou cache
    with open('articles_cache_test.json', 'w', encoding='utf-8') as f:
        json.dump(partial_cache, f, ensure_ascii=False, indent=2)
    
    print(f"Vytvořena testovací cache: {len(partial_cache)} článků")
    print("Nyní spustíme generátor s max_pages=20...")
    print("Měl by přestat stahovat, když najde článek z cache.\n")
    
    # Vytvoříme generátor s testovací cache
    gen = H7oRSSGenerator(
        cache_file='articles_cache_test.json',
        rss_file='h7o_feed_test.xml',
        max_age_months=3
    )
    
    # Načteme partial cache
    cached_articles = gen.load_cache()
    cached_urls = {a['url'] for a in cached_articles}
    
    # Spustíme stahování s cached_urls a velkým max_pages
    print("Stahuji s kontrolou cache...")
    new_articles = gen.fetch_all_articles(max_pages=20, cached_urls=cached_urls)
    
    print(f"\nVýsledek: Staženo {len(new_articles)} nových článků")
    print(f"Early stop funguje, pokud zastavil dříve než stáhl všech 20 stránek! ✓")
    
    # Úklid
    os.remove('articles_cache_test.json')
    if os.path.exists('h7o_feed_test.xml'):
        os.remove('h7o_feed_test.xml')


if __name__ == "__main__":
    test_h7o_early_stop()
