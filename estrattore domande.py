#!/usr/bin/env python3
"""
Script 'Diventa Prof' per Calcolatori Elettronici
Modalità interattiva per studio con domande e risposte
A cura di Gabriele D. Cambria (https://github.com/Gabriele-D-Cambria/)
"""

import re
import os
import random
from pathlib import Path

class Professore:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.domande_file = self.base_path / "Domande e Risposte.md"
        self.current_question = None
        
        # Verifica la presenza del file principale prima di procedere
        if not self._verifica_file_domande():
            raise FileNotFoundError(f"Il file '{self.domande_file.name}' è necessario per il funzionamento dello script.")
        
        # Filtra i file markdown escludendo quelli con "README" o "prof" nel nome
        all_md_files = list(self.base_path.glob("*.md"))
        self.markdown_files = [f for f in all_md_files 
                              if not any(keyword.lower() in f.name.lower() 
                                       for keyword in ["readme", "prof"])]
        
    def _verifica_file_domande(self):
        """Verifica l'esistenza del file Domande e Risposte.md e fornisce informazioni utili"""
        if self.domande_file.exists():
            file_size = self.domande_file.stat().st_size
            print(f"✅ File trovato: {self.domande_file.name} ({file_size} bytes)")
            return True
        else:
            print(f"❌ File non trovato: {self.domande_file.name}")
            print(f"📁 Directory corrente: {self.base_path}")
            
            # Cerca file simili nella directory
            md_files = list(self.base_path.glob("*.md"))
            if md_files:
                print("📄 File .md trovati nella directory:")
                for f in md_files:
                    print(f"   - {f.name}")
            else:
                print("📄 Nessun file .md trovato nella directory.")
            
            print(f"💡 Assicurati che il file '{self.domande_file.name}' esista prima di eseguire lo script.")
            print(f"🔗 Puoi scaricarlo da: https://github.com/Gabriele-D-Cambria/Appunti-Calcolatori-Elettronici-2024-2025/blob/master/Domande%20e%20Risposte.md")
            return False
        
    def welcome(self):
        print("🎓" + "="*50 + "🎓")
        print("   MODALITÀ PROFESSORE ATTIVATA")
        print("   Corso: Calcolatori Elettronici A.A. 2024-2025")
        print("🎓" + "="*50 + "🎓")
        print()
        print("📚 File disponibili per consultazione:")
        for f in self.markdown_files:
            print(f"   - {f.name}")
        print()
        
    def find_unanswered_questions(self):
        """Trova tutte le domande senza risposta"""
        if not self.domande_file.exists():
            return []
            
        content = self.domande_file.read_text(encoding='utf-8')
        # Trova domande senza "(answered)" nel titolo
        pattern = r'### (Domanda \d+\.\d+)(?!\s*\(answered\))'
        matches = re.finditer(pattern, content)
        
        questions = []
        for match in matches:
            start = match.start()
            # Trova la fine della domanda (prossima ### o fine file)
            next_question = content.find('###', start + 1)
            if next_question == -1:
                question_text = content[start:]
            else:
                question_text = content[start:next_question]
            
            questions.append({
                'title': match.group(1),
                'content': question_text.strip(),
                'line_pos': content[:start].count('\n') + 1,
                'answered': False
            })
        
        return questions
    
    def find_answered_questions(self):
        """Trova tutte le domande con risposta"""
        if not self.domande_file.exists():
            return []
            
        content = self.domande_file.read_text(encoding='utf-8')
        # Trova domande con "(answered)" nel titolo
        pattern = r'### (Domanda \d+\.\d+)\s*\(answered\)'
        matches = re.finditer(pattern, content)
        
        questions = []
        for match in matches:
            start = match.start()
            # Trova la fine della domanda (prossima ### o fine file)
            next_question = content.find('###', start + 1)
            if next_question == -1:
                question_text = content[start:]
            else:
                question_text = content[start:next_question]
            
            questions.append({
                'title': match.group(1),
                'content': question_text.strip(),
                'line_pos': content[:start].count('\n') + 1,
                'answered': True
            })
        
        return questions
    
    def select_random_question(self):
        """Seleziona una domanda casuale con risposta"""
        questions = self.find_answered_questions()
        if not questions:
            print("❌ Non ci sono domande con risposta!")
            return None
        
        self.current_question = random.choice(questions)
        return self.current_question
    
    def select_random_unanswered_question(self):
        """Seleziona una domanda casuale senza risposta"""
        questions = self.find_unanswered_questions()
        if not questions:
            print("❌ Non ci sono domande senza risposta!")
            return None
        
        self.current_question = random.choice(questions)
        return self.current_question
    
    def show_question(self, question=None):
        """Mostra solo la domanda corrente senza la risposta"""
        if question is None:
            question = self.current_question
            
        if question is None:
            print("❌ Nessuna domanda selezionata!")
            return
            
        print("📝 DOMANDA SELEZIONATA:")
        print("=" * 30)
        print(f"📍 {question['title']} (Linea {question['line_pos']})")
        print()
        
        # Estrai solo la parte della domanda (fino alla prima **Risposta:** o fine)
        lines = question['content'].split('\n')
        for line in lines[1:]:  # Salta il titolo
            if line.strip().startswith('**Risposta:**'):
                break
            if line.strip() == "" and any('**Risposta:**' in l for l in lines[lines.index(line)+1:]):
                break
            if line.startswith('###'):
                break
            print(line)
        print()
        
        # Indica se la domanda ha risposta o no
        if question.get('answered', False):
            print("✅ Questa domanda ha una risposta disponibile (usa 'risposta' per vederla)")
        else:
            print("❓ Domanda ancora senza risposta ufficiale")
        print()
    
    def show_answer(self):
        """Mostra la risposta della domanda corrente se disponibile"""
        if self.current_question is None:
            print("❌ Nessuna domanda selezionata!")
            return
            
        if not self.current_question.get('answered', False):
            print("❓ Domanda ancora senza risposta ufficiale")
            return
            
        print("📝 RISPOSTA:")
        print("=" * 30)
        
        # Estrai la parte della risposta
        lines = self.current_question['content'].split('\n')
        show_response = False
        
        for line in lines:
            if line.strip().startswith('**Risposta:**'):
                show_response = True
                print(line)
                continue
            if show_response:
                if line.startswith('###') and 'Domanda' in line:
                    break
                print(line)
        print()
    
    def show_available_commands(self):
        """Mostra i comandi disponibili"""
        print("💡 COMANDI DISPONIBILI:")
        print("  📝 'risposta' (r)       → Mostro la risposta (solo per domande answered)")
        print("  🔄 'cambia' (c/n)       → Seleziono nuova domanda con risposta")  
        print("  🆕 'senza-risposta' (z) → Seleziono domanda senza risposta")
        print("  ❓ 'question' (d)       → Ristampo la domanda corrente")
        print("  📊 'unanswered' (u)     → Mostro tutte le domande senza risposta")
        print("  ✅ 'answered' (a)       → Mostro tutte le domande con risposta")
        print("  📈 'stato' (s)          → Mostro statistiche domande per sezione")
        print("  📚 'files' (f)          → Lista file del corso")
        print("  💡 'help' (h)           → Mostro questa guida")
        print("  ❌ 'exit' (e/q)         → Termino la sessione")
        print()
    
    def list_unanswered_questions(self):
        """Lista tutte le domande senza risposta"""
        questions = self.find_unanswered_questions()
        print(f"📋 DOMANDE SENZA RISPOSTA ({len(questions)} totali):")
        print("-" * 40)
        for i, q in enumerate(questions, 1):
            print(f"{i:2d}. {q['title']}")
        print()
    
    def list_answered_questions(self):
        """Lista tutte le domande con risposta"""
        questions = self.find_answered_questions()
        print(f"✅ DOMANDE CON RISPOSTA ({len(questions)} totali):")
        print("-" * 40)
        for i, q in enumerate(questions, 1):
            print(f"{i:2d}. {q['title']}")
        print()
    
    def get_sections_stats(self):
        """Calcola le statistiche delle domande per sezione"""
        if not self.domande_file.exists():
            return []
        
        content = self.domande_file.read_text(encoding='utf-8')
        
        # Trova tutte le sezioni (## numero. Nome sezione)
        section_pattern = r'^## (\d+)\. (.+)$'
        sections = []
        
        lines = content.split('\n')
        current_section = None
        
        for i, line in enumerate(lines):
            section_match = re.match(section_pattern, line)
            if section_match:
                if current_section:
                    # Salva la sezione precedente
                    sections.append(current_section)
                
                # Inizia nuova sezione
                current_section = {
                    'number': section_match.group(1),
                    'name': section_match.group(2),
                    'start_line': i,
                    'questions_answered': 0,
                    'questions_total': 0
                }
            elif current_section and line.startswith('### Domanda'):
                # Conta le domande nella sezione corrente
                current_section['questions_total'] += 1
                if '(answered)' in line:
                    current_section['questions_answered'] += 1
        
        # Non dimenticare l'ultima sezione
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def show_sections_status(self):
        """Mostra lo stato delle domande per sezione in formato tabellare"""
        sections = self.get_sections_stats()
        
        if not sections:
            print("❌ Nessuna sezione trovata!")
            return
        
        print("📊 STATO DOMANDE PER SEZIONE:")
        print("=" * 80)
        
        # Header della tabella
        print(f"{'Nome sezione':<35} | {'Con risposta':<13} | {'Totali':<7} | {'Completamento':<12}")
        print("-" * 80)
        
        total_answered = 0
        total_questions = 0
        
        for section in sections:
            answered = section['questions_answered']
            total = section['questions_total']
            total_answered += answered
            total_questions += total
            
            if total > 0:
                percentage = (answered / total) * 100
                percentage_str = f"{percentage:.1f}%"
            else:
                percentage_str = "N/A"
            
            section_name = f"{section['number']}. {section['name']}"
            if len(section_name) > 34:
                section_name = section_name[:31] + "..."
            
            print(f"{section_name:<35} | {answered:<13} | {total:<7} | {percentage_str:<12}")
        
        # Totali
        print("-" * 80)
        overall_percentage = (total_answered / total_questions) * 100 if total_questions > 0 else 0
        print(f"{'TOTALE':<35} | {total_answered:<13} | {total_questions:<7} | {overall_percentage:.1f}%")
        print()
    
    def run(self):
        """Esegue il loop principale"""
        self.welcome()
        
        # Seleziona prima domanda con risposta
        if self.select_random_question():
            self.show_question()
            self.show_available_commands()
        
        while True:
            try:
                comando = input("🤔 Cosa desideri fare? ").strip().lower()
                print()
                
                if comando in ['exit', 'quit', 'esci', 'q', 'e']:
                    print("👋 Arrivederci! Buono studio!")
                    break
                    
                elif comando in ['risposta', 'r']:
                    self.show_answer()
                    
                elif comando in ['cambia', 'c', 'nuova', 'n']:
                    if self.select_random_question():
                        self.show_question()
                
                elif comando in ['senza-risposta', 'sr', 'no-answer', 'z']:
                    if self.select_random_unanswered_question():
                        self.show_question()
                
                elif comando in ['question', 'd']:
                    self.show_question()
                    
                elif comando in ['unanswered', 'u']:
                    self.list_unanswered_questions()
                
                elif comando in ['answered', 'a']:
                    self.list_answered_questions()
                    
                elif comando in ['stato', 'status', 's']:
                    self.show_sections_status()
                    
                elif comando in ['files', 'f']:
                    print("📚 FILE MARKDOWN DISPONIBILI:")
                    for f in self.markdown_files:
                        print(f"   - {f.name}")
                    print()
                    
                elif comando in ['help', 'h']:
                    self.show_available_commands()
                    
                else:
                    print(f"❓ Comando '{comando}' non riconosciuto. Digita 'help' per i comandi disponibili.")
                    
            except KeyboardInterrupt:
                print("\n👋 Arrivederci! Buono studio!")
                break
            except Exception as e:
                print(f"❌ Errore: {e}")

if __name__ == "__main__":
    # Ottieni automaticamente il path della directory dove si trova questo script
    script_dir = Path(__file__).parent.absolute()
    
    try:
        prof = Professore(script_dir)
        prof.run()
    except FileNotFoundError as e:
        print(f"❌ Errore di inizializzazione: {e}")
        print("🔧 Lo script non può continuare senza il file richiesto.")
        exit(1)
    except Exception as e:
        print(f"❌ Errore inaspettato: {e}")
        exit(1)
