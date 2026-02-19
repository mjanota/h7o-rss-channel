#!/usr/bin/env python3
"""
RSS Generator pro články z https://www.h7o.cz/clanky
- Při prvním spuštění stáhne články za poslední 3 měsíce
- Při dalších spuštěních přidá nové články a smaže staré
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from feedgen.feed import FeedGenerator
import json
import os
import re
from urllib.parse import urljoin


class H7oRSSGenerator:
    def __init__(self, base_url="https://www.h7o.cz/clanky", 
                 cache_file="articles_cache.json",
                 rss_file="h7o_feed.xml",
                 max_age_months=3):
        self.base_url = base_url
        self.cache_file = cache_file
        self.rss_file = rss_file
        self.max_age_months = max_age_months
        self.articles = []

    def load_cache(self):
        """Načte uložený stav článků z cache souboru"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_cache(self, articles):
        """Uloží aktuální stav článků do cache souboru"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

    def parse_date(self, date_str):
        """Převede datum z formátu DD/MM/YYYY na datetime objekt"""
        try:
            return datetime.strptime(date_str.strip(), "%d/%m/%Y")
        except ValueError:
            return None

    def fetch_page(self, page_num=1):
        """Stáhne a parsuje jednu stránku článků"""
        if page_num == 1:
            url = self.base_url
        else:
            url = f"{self.base_url}?flexiArticles25-paginator-pageNumber={page_num}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Chyba při stahování stránky {page_num}: {e}")
            return None

    def extract_articles_from_page(self, soup):
        """Extrahuje informace o článcích z HTML stránky"""
        articles = []
        seen_urls = set()  # Pro odstranění duplicit

        # Najdeme všechny divy s class="article"
        article_divs = soup.find_all('div', class_='article')

        for article_div in article_divs:
            try:
                # Najdeme nadpis v article__heading
                heading = article_div.find('h3', class_='article__heading')
                if not heading:
                    continue

                # Získáme nadpis článku
                title = heading.get_text(strip=True)

                # Najdeme odkaz s class="article__link"
                link_elem = article_div.find('a', class_='article__link', href=True)

                if not link_elem:
                    continue

                url = urljoin(self.base_url, link_elem['href'])

                if not title or not url or url in seen_urls:
                    continue

                # Najdeme datum v div s class="article__date"
                date = None
                date_div = article_div.find('div', class_='article__date')
                if date_div:
                    date_text = date_div.get_text(strip=True)
                    date = self.parse_date(date_text)

                if not date:
                    continue

                # Získáme popis z p s class="article__perex"
                description = ""
                perex_p = article_div.find('p', class_='article__perex')
                if perex_p:
                    description = perex_p.get_text(strip=True)

                # Získáme autora z div s class="article__author"
                author = ""
                author_div = article_div.find('div', class_='article__author')
                if author_div:
                    author = author_div.get_text(strip=True)

                # Získáme kategorii z div s class="article__category"
                category = ""
                category_div = article_div.find('div', class_='article__category')
                if category_div:
                    category = category_div.get_text(strip=True)

                seen_urls.add(url)
                article = {
                    'title': title,
                    'url': url,
                    'description': description,
                    'date': date.isoformat(),
                    'date_obj': date,
                    'author': author,
                    'category': category
                }
                articles.append(article)

            except Exception as e:
                print(f"Chyba při zpracování článku: {e}")
                continue

        return articles

    def fetch_all_articles(self, max_pages=20, cached_urls=None):
        """Stáhne články ze všech stránek (nebo do max_pages)"""
        if cached_urls is None:
            cached_urls = set()

        all_articles = []
        page_num = 1
        cutoff_date = datetime.now() - timedelta(days=self.max_age_months * 30)

        print(f"Stahuji články novější než {cutoff_date.strftime('%d/%m/%Y')}...")
        print(f"Maximální počet stránek: {max_pages}")

        while page_num <= max_pages:
            print(f"Zpracovávám stránku {page_num}...", end=" ")
            soup = self.fetch_page(page_num)

            if not soup:
                print("Chyba při stahování.")
                break

            articles = self.extract_articles_from_page(soup)

            if not articles:
                print("Žádné články nenalezeny.")
                break

            # Filtrujeme články podle data a kontrolujeme duplicity
            new_articles = []
            old_count = 0
            cached_count = 0

            for article in articles:
                # Pokud článek už máme v cache, zastavíme
                if article["url"] in cached_urls:
                    cached_count += 1
                    continue

                if article['date_obj'] >= cutoff_date:
                    new_articles.append(article)
                else:
                    old_count += 1

            all_articles.extend(new_articles)
            print(
                f"Nalezeno {len(new_articles)} relevantních článků (přeskočeno {old_count} starých, {cached_count} již v cache)."
            )

            # Pokud najdeme článek z cache, zastavíme - starší už máme
            if cached_count > 0:
                print(f"Nalezen článek již v cache, zastavuji stahování.")
                break

            # Pokud všechny články jsou staré, zastavíme
            if old_count > 0 and len(new_articles) == 0:
                print("Všechny články na stránce jsou starší než limit.")
                break

            # Pokud většina článků je stará, pravděpodobně už nenajdeme nic nového
            if old_count > len(articles) / 2:
                print(f"Více než polovina článků je starších než limit, zastavuji.")
                break

            # Kontrola, zda existuje další stránka
            next_page = soup.find('a', string=re.compile(r'Další|›|»'))
            if not next_page:
                print("Dosaženo poslední stránky.")
                break

            page_num += 1

        if page_num > max_pages:
            print(f"Dosaženo maximálního počtu stránek ({max_pages}).")

        return all_articles

    def generate_rss(self, articles):
        """Generuje RSS XML soubor z článků"""
        fg = FeedGenerator()
        fg.title('H7O - Časopis Host 7 dní online')
        fg.link(href=self.base_url, rel='alternate')
        fg.description('RSS kanál článků z H7O - Časopis Host')
        fg.language('cs')

        # Seřadíme články podle data (nejnovější první)
        sorted_articles = sorted(articles, key=lambda x: x['date'], reverse=True)

        for article in sorted_articles:
            fe = fg.add_entry()
            fe.title(article['title'])
            fe.link(href=article['url'])
            fe.description(article['description'])
            fe.guid(article['url'], permalink=True)

            # Převedeme datum na datetime objekt pro RSS s timezone
            pub_date = datetime.fromisoformat(article['date'])
            # Přidáme timezone pokud není přítomna
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)
            fe.pubDate(pub_date)

        # Uložíme RSS do souboru
        fg.rss_file(self.rss_file, pretty=True)
        print(f"\nRSS soubor vytvořen: {self.rss_file}")
        print(f"Celkem článků v RSS: {len(sorted_articles)}")

    def run(self):
        """Hlavní funkce pro spuštění generátoru"""
        print("=== H7O RSS Generator ===\n")

        # Načteme cache
        cached_articles = self.load_cache()
        is_first_run = len(cached_articles) == 0

        # Vytvoříme množinu URL z cache pro rychlé porovnání
        cached_urls = {a["url"] for a in cached_articles}

        if is_first_run:
            print("První spuštění - stahuji všechny články za poslední 3 měsíce...\n")
            # Stáhneme všechny relevantní články
            new_articles = self.fetch_all_articles(cached_urls=cached_urls)
        else:
            print(f"Nalezeno {len(cached_articles)} článků v cache.")
            print("Kontroluji nové články...\n")
            # Stáhneme jen první stránku pro kontrolu nových článků
            soup = self.fetch_page(1)
            if soup:
                new_articles = self.extract_articles_from_page(soup)
            else:
                new_articles = []

        # Identifikujeme skutečně nové články
        truly_new = [a for a in new_articles if a['url'] not in cached_urls]

        if truly_new:
            print(f"\nNalezeno {len(truly_new)} nových článků")
            if len(truly_new) <= 10:
                for article in truly_new:
                    print(f"  - {article['title']}")
            else:
                print(f"  (Zobrazuji prvních 10 z {len(truly_new)})")
                for article in truly_new[:10]:
                    print(f"  - {article['title']}")
        else:
            print("\nŽádné nové články nenalezeny.")

        # Sloučíme nové a cache články
        all_articles = cached_articles + truly_new

        # Odstraníme duplicity podle URL
        unique_articles = list({a['url']: a for a in all_articles}.values())

        # Filtrujeme staré články
        cutoff_date = datetime.now() - timedelta(days=self.max_age_months * 30)
        filtered_articles = []

        for article in unique_articles:
            article_date = datetime.fromisoformat(article['date'])
            if article_date >= cutoff_date:
                filtered_articles.append(article)

        removed_count = len(unique_articles) - len(filtered_articles)
        if removed_count > 0:
            print(f"\nOdstraněno {removed_count} starých článků.")

        # Uložíme aktualizovanou cache
        # Připravíme články pro uložení (bez date_obj)
        articles_to_save = []
        for article in filtered_articles:
            article_copy = article.copy()
            article_copy.pop('date_obj', None)
            articles_to_save.append(article_copy)

        self.save_cache(articles_to_save)

        # Vygenerujeme RSS
        # Přidáme date_obj zpět pro generování RSS
        for article in filtered_articles:
            if 'date_obj' not in article:
                article['date_obj'] = datetime.fromisoformat(article['date'])

        self.generate_rss(filtered_articles)

        print("\n=== Hotovo ===")


def main():
    generator = H7oRSSGenerator()
    generator.run()


if __name__ == "__main__":
    main()
