#!/usr/bin/env python3
"""
Utility pro logování běhů RSS generátorů
"""

import os
from datetime import datetime, timedelta, timezone


class RSSLogger:
    def __init__(self, log_file="rss_update_log.md"):
        self.log_file = log_file
        self._ensure_log_exists()
    
    def _ensure_log_exists(self):
        """Vytvoří log soubor s hlavičkou, pokud neexistuje"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("# 📊 RSS Feed Update Log\n\n")
                f.write("Automaticky generovaný log aktualizací RSS feedů.\n")
                f.write("Uchovává záznamy za poslední týden.\n\n")
                f.write("---\n\n")
    
    def _clean_old_entries(self):
        """Odstraní záznamy starší než 7 dní"""
        if not os.path.exists(self.log_file):
            return
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Najdeme hlavičku (první 5 řádků)
        header_lines = []
        content_lines = []
        in_header = True
        
        for i, line in enumerate(lines):
            if in_header and (i < 5 or line.strip() == "---"):
                header_lines.append(line)
                if line.strip() == "---":
                    in_header = False
            else:
                content_lines.append(line)
        
        # Filtrujeme staré záznamy
        filtered_lines = []
        current_entry = []
        skip_entry = False
        
        for line in content_lines:
            # Začátek nového záznamu
            if line.startswith("## 🕐 "):
                # Zpracujeme předchozí záznam
                if current_entry and not skip_entry:
                    filtered_lines.extend(current_entry)
                
                # Začneme nový záznam
                current_entry = [line]
                # Extrahujeme datum ze záznamu
                try:
                    # Formát: ## 🕐 2026-02-19 14:30:15 UTC
                    date_str = line.split("🕐 ")[1].strip().replace(" UTC", "")
                    entry_date = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
                    skip_entry = entry_date < cutoff_date
                except:
                    skip_entry = False
            else:
                current_entry.append(line)
        
        # Přidáme poslední záznam
        if current_entry and not skip_entry:
            filtered_lines.extend(current_entry)
        
        # Zapíšeme zpět
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.writelines(header_lines)
            f.writelines(filtered_lines)
    
    def log_run(self, source_name, new_items_count, new_items_titles=None, error=None):
        """
        Zaloguje spuštění generátoru
        
        Args:
            source_name: Název zdroje (např. "H7O", "Kosmas.cz")
            new_items_count: Počet nových položek
            new_items_titles: Seznam titulů nových položek
            error: Chybová zpráva, pokud nastala
        """
        self._ensure_log_exists()
        self._clean_old_entries()
        
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Načteme existující obsah
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Najdeme konec hlavičky (řádek s "---")
        header_end = 0
        for i, line in enumerate(lines):
            if line.strip() == "---":
                header_end = i + 1
                break
        
        # Vytvoříme nový záznam
        new_entry = []
        new_entry.append("\n")
        new_entry.append(f"## 🕐 {timestamp} UTC\n\n")
        new_entry.append(f"**Zdroj:** {source_name}\n\n")
        
        if error:
            new_entry.append(f"**Status:** ❌ Chyba\n\n")
            new_entry.append(f"**Chybová zpráva:**\n```\n{error}\n```\n\n")
        else:
            new_entry.append(f"**Status:** ✅ Úspěch\n\n")
            new_entry.append(f"**Nové položky:** {new_items_count}\n\n")
            
            if new_items_count > 0 and new_items_titles:
                new_entry.append("**Tituly nových položek:**\n\n")
                for i, title in enumerate(new_items_titles[:20], 1):  # Max 20
                    new_entry.append(f"{i}. {title}\n")
                
                if len(new_items_titles) > 20:
                    new_entry.append(f"\n... a dalších {len(new_items_titles) - 20} položek\n")
                new_entry.append("\n")
        
        new_entry.append("---\n")
        
        # Vložíme nový záznam hned za hlavičku
        new_content = lines[:header_end] + new_entry + lines[header_end:]
        
        # Zapíšeme zpět
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.writelines(new_content)
        
        print(f"📝 Log zapsán do {self.log_file}")
