# RSS Generátory pro H7O a Kosmas.cz

RSS kanály pro:
- [H7O - Časopis Host](https://www.h7o.cz/clanky)
- [Kosmas.cz - Novinky](https://www.kosmas.cz/novinky/)

## Funkce

### H7O RSS Generator
- **První spuštění:** Stáhne všechny články za poslední 3 měsíce (maximálně 20 stránek)
- **Další spuštění:** Kontroluje nové články na první stránce, přidává je do RSS a automaticky odstraňuje staré
- **Výstup:** `h7o_feed.xml`

### Kosmas.cz RSS Generator
- **První spuštění:** Stáhne novinky z prvních 10 stránek
- **Další spuštění:** Kontroluje nové položky na první stránce
- **Výstup:** `kosmas_feed.xml`

## Instalace

Projekt používá [uv](https://github.com/astral-sh/uv) pro správu závislostí.

```bash
# Instalace závislostí
uv sync
```

## Použití

```bash
# Generování všech RSS feedů najednou
uv run python generate_all.py

# Nebo jednotlivě:
uv run python rss_generator.py      # Pouze H7O
uv run python kosmas_generator.py   # Pouze Kosmas.cz
```

### První spuštění
- H7O: Stáhne až 20 stránek článků za poslední 3 měsíce
- Kosmas: Stáhne prvních 10 stránek novinek
- Uloží je do cache (`articles_cache.json`, `kosmas_cache.json`)
- Vygeneruje RSS soubory (`h7o_feed.xml`, `kosmas_feed.xml`)

### Další spuštění
- Načte uložené položky z cache
- Zkontroluje první stránku webu pro nové položky
- Přidá nové položky do RSS
- H7O: Automaticky odstraní články starší než 3 měsíce
- Kosmas: Omezí cache na 200 nejnovějších položek
- Aktualizuje RSS soubory

## Výstupy

- `h7o_feed.xml` - RSS feed pro H7O články
- `kosmas_feed.xml` - RSS feed pro Kosmas.cz novinky  
- `articles_cache.json` - Cache H7O článků
- `kosmas_cache.json` - Cache Kosmas novinek

## Konfigurace

Můžete upravit parametry při vytváření instance `H7oRSSGenerator`:

```python
generator = H7oRSSGenerator(
    base_url="https://www.h7o.cz/clanky",
    cache_file="articles_cache.json",
    rss_file="h7o_feed.xml",
    max_age_months=3  # Stáří článků v měsících
)
```

## Publikování RSS přes GitHub Pages

### 1. Vytvořte GitHub repository

```bash
# Přidejte remote repository (nahraďte USERNAME svým GitHub uživatelským jménem)
git remote add origin https://github.com/USERNAME/rss-channel.git
git push -u origin main
```

### 2. Aktivujte GitHub Pages

1. Jděte na **Settings** → **Pages** ve vašem GitHub repository
2. V sekci **Source** vyberte **GitHub Actions**
3. Uložte nastavení

### 3. Hotovo!

RSS feedy budou dostupné na:
```
https://USERNAME.github.io/rss-channel/h7o_feed.xml
https://USERNAME.github.io/rss-channel/kosmas_feed.xml
```

### Automatická aktualizace

GitHub Actions automaticky:
- ✅ Aktualizuje oba RSS feedy každý den v 6:00 UTC (7:00 CET)
- ✅ Publikuje změny na GitHub Pages
- ✅ Můžete spustit manuálně přes záložku "Actions" na GitHubu

## Lokální testování

Pro lokální testování můžete spustit HTTP server:

```bash
# Spustí server na http://localhost:8080
uv run server.py

# RSS feedy pak budou dostupné na:
# http://localhost:8080/h7o_feed.xml
# http://localhost:8080/kosmas_feed.xml
```
