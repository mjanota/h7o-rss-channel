# H7O RSS Generátor

RSS kanál pro články z webu [H7O - Časopis Host](https://www.h7o.cz/clanky).

## Funkce

- **První spuštění:** Stáhne všechny články za poslední 3 měsíce (maximálně 20 stránek)
- **Další spuštění:** Kontroluje nové články na první stránce, přidává je do RSS a automaticky odstraňuje staré
- **Výstup:** Generuje XML soubor ve formátu RSS 2.0 kompatibilní se všemi RSS čtečkami

## Instalace

Projekt používá [uv](https://github.com/astral-sh/uv) pro správu závislostí.

```bash
# Instalace závislostí
uv sync
```

## Použití

```bash
# Spuštění generátoru
uv run python rss_generator.py
```

### První spuštění
Při prvním spuštění skript:
- Stáhne až 20 stránek článků
- Filtruje pouze články novější než 3 měsíce
- Uloží je do cache (`articles_cache.json`)
- Vygeneruje RSS soubor (`h7o_feed.xml`)

### Další spuštění
Při dalších spuštěních skript:
- Načte uložené články z cache
- Zkontroluje první stránku webu pro nové články
- Přidá nové články do RSS
- Automaticky odstraní články starší než 3 měsíce
- Aktualizuje RSS soubor

## Výstupy

- `h7o_feed.xml` - RSS soubor pro čtečky (seřazený od nejnovějších)
- `articles_cache.json` - Cache stažených článků

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

RSS feed bude dostupný na:
```
https://USERNAME.github.io/rss-channel/h7o_feed.xml
```

### Automatická aktualizace

GitHub Actions automaticky:
- ✅ Aktualizuje RSS každý den v 6:00 UTC (7:00 CET)
- ✅ Publikuje změny na GitHub Pages
- ✅ Můžete spustit manuálně přes záložku "Actions" na GitHubu

## Lokální testování

Pro lokální testování můžete spustit HTTP server:

```bash
# Spustí server na http://localhost:8080
uv run server.py

# RSS pak bude dostupný na:
# http://localhost:8080/h7o_feed.xml
```
