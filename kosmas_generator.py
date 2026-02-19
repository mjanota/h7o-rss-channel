#!/usr/bin/env python3
"""
RSS Generator pro novinky z https://www.kosmas.cz/novinky/
- Při prvním spuštění stáhne novinky z prvních 10 stránek
- Při dalších spuštěních přidá nové novinky ze základní stránky
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
import json
import os
from urllib.parse import urljoin
from log_utils import RSSLogger


class KosmasRSSGenerator:

    def __init__(
        self,
        base_url="https://www.kosmas.cz/novinky/",
        cache_file="kosmas_cache.json",
        rss_file="kosmas_feed.xml",
        max_pages=10,
        log_file="kosmas_generator.log",
    ):
        self.base_url = base_url
        self.cache_file = cache_file
        self.rss_file = rss_file
        self.max_pages = max_pages
        self.log_file = log_file

    def log(self, message):
        """Zapíše zprávu do log souboru"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def load_cache(self):
        """Načte uložený stav novinek z cache souboru"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_cache(self, items):
        """Uloží aktuální stav novinek do cache souboru"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

    def fetch_page(self, page_num=1):
        """Stáhne a parsuje jednu stránku novinek"""
        if page_num == 1:
            url = self.base_url
        else:
            url = f"{self.base_url}?page={page_num}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Chyba při stahování stránky {page_num}: {e}")
            return None

    def extract_items_from_page(self, soup):
        """Extrahuje informace o novinkách z HTML stránky"""
        items = []
        seen_urls = set()

        # Najdeme hlavní kontejner
        container = soup.find('div', class_='grid-items__pagenumber')
        if not container:
            print("Kontejner grid-items__pagenumber nenalezen!")
            return items

        # Najdeme všechny grid-items
        grid_items = container.find_all('div', class_='grid-item')

        for grid_item in grid_items:
            try:
                # Najdeme nadpis
                title_elem = grid_item.find('h3', class_='g-item__title')
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)

                # Najdeme odkaz pod h3
                link_elem = title_elem.find('a', href=True)
                if not link_elem:
                    continue

                url = urljoin(self.base_url, link_elem['href'])

                if not title or not url or url in seen_urls:
                    continue

                # Najdeme autory
                authors = []
                author_span = grid_item.find('span', class_='titul-author')
                if author_span:
                    author_links = author_span.find_all('a')
                    authors = [a.get_text(strip=True) for a in author_links]

                # Vytvoříme description z title a autorů
                if authors:
                    description = f"{title} - {', '.join(authors)}"
                else:
                    description = title

                seen_urls.add(url)
                item = {
                    'title': title,
                    'url': url,
                    'description': description,
                    'authors': authors,
                    'date': datetime.now(timezone.utc).isoformat()
                }
                items.append(item)

            except Exception as e:
                print(f"Chyba při zpracování položky: {e}")
                continue

        return items

    def fetch_all_items(self, max_pages=None, cached_urls=None):
        """Stáhne novinky ze všech stránek (nebo do max_pages)"""
        if max_pages is None:
            max_pages = self.max_pages
        if cached_urls is None:
            cached_urls = set()

        all_items = []
        page_num = 1

        print(f"Stahuji novinky z Kosmas.cz...")
        print(f"Maximální počet stránek: {max_pages}")

        while page_num <= max_pages:
            print(f"Zpracovávám stránku {page_num}...", end=" ")
            soup = self.fetch_page(page_num)

            if not soup:
                print("Chyba při stahování.")
                break

            items = self.extract_items_from_page(soup)

            if not items:
                print("Žádné položky nenalezeny.")
                break

            # Kontrolujeme, zda některá položka již není v cache
            new_items = []
            cached_count = 0
            for item in items:
                if item['url'] in cached_urls:
                    cached_count += 1
                else:
                    new_items.append(item)

            all_items.extend(new_items)
            print(f"Nalezeno {len(new_items)} nových položek (přeskočeno {cached_count} již v cache).")

            # Pokud najdeme položku z cache, zastavíme - starší už máme
            if cached_count > 0:
                print(f"Nalezena položka již v cache, zastavuji stahování.")
                break

            # Kontrola, zda existuje další stránka
            # Hledáme tlačítko "Další" nebo podobné
            next_button = soup.find('a', string='Další')
            if not next_button and page_num >= max_pages:
                break

            page_num += 1

        if page_num > max_pages:
            print(f"Dosaženo maximálního počtu stránek ({max_pages}).")

        return all_items

    def generate_rss(self, items):
        """Generuje RSS XML soubor z novinek"""
        fg = FeedGenerator()
        fg.title('Kosmas.cz - Novinky')
        fg.link(href=self.base_url, rel='alternate')
        fg.description('RSS kanál novinek z Kosmas.cz')
        fg.language('cs')

        # Seřadíme položky podle data (nejnovější první)
        sorted_items = sorted(items, key=lambda x: x['date'], reverse=True)

        for item in sorted_items[:100]:  # Omezíme na 100 nejnovějších
            fe = fg.add_entry()
            fe.title(item['title'])
            fe.link(href=item['url'])
            fe.description(item['description'])
            fe.guid(item['url'], permalink=True)

            # Převedeme datum na datetime objekt pro RSS
            pub_date = datetime.fromisoformat(item['date'])
            fe.pubDate(pub_date)

        # Uložíme RSS do souboru
        fg.rss_file(self.rss_file, pretty=True)
        print(f"\nRSS soubor vytvořen: {self.rss_file}")
        print(f"Celkem položek v RSS: {min(len(sorted_items), 100)}")

    def run(self):
        """Hlavní funkce pro spuštění generátoru"""
        print("=== Kosmas.cz RSS Generator ===\n")

        logger = RSSLogger()
        new_items_titles = []

        try:
            # Načteme cache
            cached_items = self.load_cache()
            is_first_run = len(cached_items) == 0

            # Vytvoříme množinu URL z cache pro rychlé porovnání
            cached_urls = {item["url"] for item in cached_items}

            if is_first_run:
                print(
                    f"První spuštění - stahuji novinky z prvních {self.max_pages} stránek...\n"
                )
                # Stáhneme všechny novinky
                new_items = self.fetch_all_items(cached_urls=cached_urls)
            else:
                print(f"Nalezeno {len(cached_items)} položek v cache.")
                print("Kontroluji nové položky...\n")
                # Stáhneme jen první stránku pro kontrolu nových položek
                soup = self.fetch_page(1)
                if soup:
                    new_items = self.extract_items_from_page(soup)
                else:
                    new_items = []

            # Identifikujeme skutečně nové položky
            truly_new = [item for item in new_items if item["url"] not in cached_urls]
            new_items_titles = [item["title"] for item in truly_new]

            if truly_new:
                print(f"\nNalezeno {len(truly_new)} nových položek")
                if len(truly_new) <= 10:
                    for item in truly_new:
                        print(f"  - {item['title']}")
                else:
                    print(f"  (Zobrazuji prvních 10 z {len(truly_new)})")
                    for item in truly_new[:10]:
                        print(f"  - {item['title']}")
            else:
                print("\nŽádné nové položky nenalezeny.")

            # Sloučíme nové a cache položky
            all_items = cached_items + truly_new

            # Odstraníme duplicity podle URL
            unique_items = list({item["url"]: item for item in all_items}.values())

            # Omezíme počet na 200 nejnovějších (pro úsporu místa)
            if len(unique_items) > 200:
                sorted_by_date = sorted(
                    unique_items, key=lambda x: x["date"], reverse=True
                )
                unique_items = sorted_by_date[:200]
                print(f"\nOmezeno na 200 nejnovějších položek.")

            # Uložíme aktualizovanou cache
            self.save_cache(unique_items)

            # Vygenerujeme RSS
            self.generate_rss(unique_items)

            # Zalogujeme úspěšné spuštění
            logger.log_run(
                source_name="Kosmas.cz - Novinky",
                new_items_count=len(truly_new),
                new_items_titles=new_items_titles,
            )

        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ Chyba: {error_msg}")
            logger.log_run(
                source_name="Kosmas.cz - Novinky", new_items_count=0, error=error_msg
            )
            raise

        print("\n=== Hotovo ===")


def main():
    generator = KosmasRSSGenerator()
    generator.run()


if __name__ == "__main__":
    main()
