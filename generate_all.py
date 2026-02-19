#!/usr/bin/env python3
"""
Unified RSS Generator - generuje RSS pro všechny zdroje
"""

from rss_generator import H7oRSSGenerator
from kosmas_generator import KosmasRSSGenerator


def main():
    print("=" * 60)
    print("  RSS Generator pro H7O a Kosmas.cz")
    print("=" * 60)
    print()
    
    # Generujeme H7O feed
    print("🔹 Generuji H7O RSS feed...\n")
    h7o_gen = H7oRSSGenerator()
    h7o_gen.run()
    
    print("\n" + "=" * 60 + "\n")
    
    # Generujeme Kosmas feed
    print("🔹 Generuji Kosmas.cz RSS feed...\n")
    kosmas_gen = KosmasRSSGenerator()
    kosmas_gen.run()
    
    print("\n" + "=" * 60)
    print("✅ Všechny RSS feedy byly úspěšně vygenerovány!")
    print("=" * 60)


if __name__ == "__main__":
    main()
