#!/usr/bin/env python3
"""
actualizar_tablero.py
---------------------
Regenera tablero.html a partir de un export de WhatsApp.

Uso:
    python3 actualizar_tablero.py _chat.txt

Genera:
    tablero.html  (reemplaza el existente)

Qué extrae (y qué NO):
    SÍ  — fecha, hora, autor, tipo (inicio/finalización/recepción), número de sumario
    NO  — carátulas de causa, nombres de imputados/víctimas, reseñas

Después de correrlo, copiá el tablero.html a la carpeta compartida de red.
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime

CHAT_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('_chat.txt')
OUT_PATH  = Path(__file__).parent / 'tablero.html'
TPL_PATH  = Path(__file__).parent / 'tablero.template.html'


def parse_chat(text: str):
    """Extrae eventos del chat. NUNCA guarda carátulas."""
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

        am = re.search(r'\*?asunto\*?[:\*]*\s*([^\n\r]+)', body, re.IGNORECASE)
        if not am:
            continue
        asunto = am.group(1).lower()
        if   'recepci' in asunto or 'recibe' in asunto: tipo = 'recepcion'
        elif 'inicio'  in asunto or 'inici'  in asunto: tipo = 'inicio'
        elif 'final'   in asunto or re.search(r'\bfin\b', asunto) or 'finaliz' in asunto: tipo = 'finalizacion'
        else:
            continue

        sm = re.search(r'sumario\s+daypt[^\d]*(\d+/\d+)', body, re.IGNORECASE)

        events.append({
            'fecha':   f'{year:04d}-{int(mo):02d}-{int(day):02d}',
            'hora':    f'{int(h):02d}:{mi}',
            'sender':  sender.strip(),
            'tipo':    tipo,
            'sumario': sm.group(1) if sm else None,
        })
    events.sort(key=lambda e: (e['fecha'], e['hora']))
    return events


def main():
    if not CHAT_PATH.exists():
        print(f'✖ No encuentro el chat: {CHAT_PATH}', file=sys.stderr)
        print('  Pasá la ruta como argumento:  python3 actualizar_tablero.py /ruta/al/_chat.txt', file=sys.stderr)
        sys.exit(1)
    if not TPL_PATH.exists():
        print(f'✖ No encuentro la plantilla: {TPL_PATH}', file=sys.stderr)
        sys.exit(1)

    text = CHAT_PATH.read_text(encoding='utf-8')
    events = parse_chat(text)
    tpl = TPL_PATH.read_text(encoding='utf-8')
    out = tpl.replace('__EVENTS_JSON__', json.dumps(events, ensure_ascii=False, separators=(',', ':')))
    out = out.replace('__GENERATED_AT__', datetime.now().strftime('%Y-%m-%d %H:%M'))
    OUT_PATH.write_text(out, encoding='utf-8')

    # Resumen
    by_tipo = {}
    for e in events:
        by_tipo[e['tipo']] = by_tipo.get(e['tipo'], 0) + 1
    peritos = {e['sender'] for e in events if e['tipo'] != 'recepcion'}
    judiciales = {e['sender'] for e in events if e['tipo'] == 'recepcion'}

    print(f'✔ Tablero regenerado: {OUT_PATH}')
    print(f'  Eventos totales : {len(events)}')
    print(f'  Inicios         : {by_tipo.get("inicio", 0)}')
    print(f'  Finalizaciones  : {by_tipo.get("finalizacion", 0)}')
    print(f'  Recepciones     : {by_tipo.get("recepcion", 0)}')
    print(f'  Peritos         : {len(peritos)}')
    print(f'  Judiciales      : {len(judiciales)}')
    if events:
        print(f'  Rango de fechas : {events[0]["fecha"]}  →  {events[-1]["fecha"]}')


if __name__ == '__main__':
    main()
