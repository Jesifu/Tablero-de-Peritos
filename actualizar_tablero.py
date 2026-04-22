#!/usr/bin/env python3
import re
import json
import sys
from pathlib import Path
from datetime import datetime

CHAT_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('_chat.txt')
OUT_PATH  = Path(__file__).parent / 'tablero.html'
TPL_PATH  = Path(__file__).parent / 'tablero.template.html'

def parse_chat(text: str):
    msg_start = re.compile(
        r'^\[(\d{1,2})/(\d{1,2})/(\d{2,4}),\s*(\d{1,2}):(\d{2}):(\d{2})\]\s+([^:]+?):\s?',
        re.MULTILINE,
    )
    matches = list(msg_start.finditer(text))
    events = []
    
    for i, m in enumerate(matches):
        day, mo, yr, h, mi, s, sender = m.groups()
        year = 2000 + int(yr) if len(yr) == 2 else int(yr)
        start = m.end()
        end   = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body  = text[start:end].strip()

        # Detectar Asunto
        am = re.search(r'\*?asunto\*?[:\*]*\s*([^\n\r]+)', body, re.IGNORECASE)
        if not am: continue
        asunto = am.group(1).lower()
        
        if   'recepci' in asunto or 'recibe' in asunto: tipo = 'recepcion'
        elif 'inicio'  in asunto or 'inici'  in asunto: tipo = 'inicio'
        elif 'final'   in asunto or re.search(r'\bfin\b', asunto) or 'finaliz' in asunto: tipo = 'finalizacion'
        else: continue

        # Extraer Sumario
        sm = re.search(r'sumario\s+daypt[^\d]*(\d+/\d+)', body, re.IGNORECASE)
        
        # Extraer Dispositivos de la RESEÑA (busca números entre paréntesis)
        # Ej: "un (01) teléfono", "cinco (05) celulares" [cite: 26, 33]
        reseña_match = re.search(r'RESEÑA:?\s*(.*)', body, re.IGNORECASE | re.DOTALL)
        cant_disp = 0
        if reseña_match:
            reseña_text = reseña_match.group(1)
            numeros = re.findall(r'\((\d+)\)', reseña_text)
            cant_disp = sum(int(n) for n in numeros)
        
        # Si no encontró números en paréntesis, pero es una pericia, asume 1
        if cant_disp == 0 and tipo != 'recepcion':
            cant_disp = 1

        events.append({
            'fecha':   f'{year:04d}-{int(mo):02d}-{int(day):02d}',
            'hora':    f'{int(h):02d}:{mi}',
            'sender':  sender.strip(),
            'tipo':    tipo,
            'sumario': sm.group(1) if sm else None,
            'dispositivos': cant_disp
        })
    
    events.sort(key=lambda e: (e['fecha'], e['hora']))
    return events

def main():
    if not CHAT_PATH.exists() or not TPL_PATH.exists():
        print("✖ Faltan archivos (_chat.txt o tablero.template.html)")
        sys.exit(1)

    events = parse_chat(CHAT_PATH.read_text(encoding='utf-8'))
    tpl = TPL_PATH.read_text(encoding='utf-8')
    
    out = tpl.replace('__EVENTS_JSON__', json.dumps(events, ensure_ascii=False, separators=(',', ':')))
    out = out.replace('__GENERATED_AT__', datetime.now().strftime('%Y-%m-%d %H:%M'))
    OUT_PATH.write_text(out, encoding='utf-8')
    print(f'✔ Tablero regenerado con éxito.')

if __name__ == '__main__':
    main()
