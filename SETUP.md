# 🚀 GitHub Pages Setup

## Krok 1: Vytvořte GitHub repository

1. Jděte na https://github.com/new
2. Nastavte:
   - **Repository name:** `rss-channel` (nebo jakékoliv jiné jméno)
   - **Visibility:** Public (nutné pro GitHub Pages zdarma)
3. **NEVYTVÁŘEJTE** README, .gitignore ani license (už je máme)
4. Klikněte na **Create repository**

## Krok 2: Pushněte kód na GitHub

GitHub vám ukáže instrukce. Použijte tyto příkazy (nahraďte `USERNAME` svým GitHub uživatelským jménem):

```bash
git remote add origin https://github.com/USERNAME/rss-channel.git
git push -u origin main
```

**Poznámka:** Pokud máte nastavený SSH klíč, můžete použít:
```bash
git remote add origin git@github.com:USERNAME/rss-channel.git
git push -u origin main
```

## Krok 3: Aktivujte GitHub Pages

1. Jděte do vašeho repository na GitHubu
2. Klikněte na **Settings** (záložka nahoře)
3. V levém menu klikněte na **Pages**
4. V sekci **Source** vyberte:
   - **Source:** GitHub Actions
5. Uložte (pokud je potřeba)

## Krok 4: Počkejte na deployment

1. Jděte na záložku **Actions** v repository
2. Měli byste vidět workflow "Deploy to GitHub Pages"
3. Počkejte, až se dokončí (zelená fajfka ✅)
4. První build může trvat 1-2 minuty

## Krok 5: Hotovo! 🎉

Váš RSS feed je dostupný na:

```
https://USERNAME.github.io/rss-channel/h7o_feed.xml
```

A webové rozhraní na:

```
https://USERNAME.github.io/rss-channel/
```

## Automatická aktualizace

- RSS se automaticky aktualizuje každý den v 6:00 UTC
- Můžete také spustit aktualizaci manuálně:
  1. Jděte na **Actions** → **Update RSS Feed**
  2. Klikněte na **Run workflow**
  3. Klikněte na zelené tlačítko **Run workflow**

## Problémy?

### GitHub Actions nefungují
- Zkontrolujte, že repository je **Public**
- Jděte do **Settings** → **Actions** → **General**
- Ujistěte se, že je povoleno "Allow all actions and reusable workflows"
- V sekci "Workflow permissions" vyberte "Read and write permissions"

### Pages se nenačítají
- Počkejte 5-10 minut po prvním push
- Zkontrolujte **Actions** zda workflow úspěšně proběhl
- Zkuste hard refresh: Ctrl+F5 (Windows) nebo Cmd+Shift+R (Mac)
