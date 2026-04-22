# Tablero de Peritos — DAYPT

Tablero interno para visualizar la actividad de pericias reportadas al grupo de WhatsApp.

## Archivos

| Archivo                     | Qué es                                                                 |
| --------------------------- | ---------------------------------------------------------------------- |
| `tablero.html`              | **El tablero**. Copiar a la carpeta compartida. Todos abren este.      |
| `tablero.template.html`     | Plantilla base (no modificar). Se combina con el chat al regenerar.    |
| `actualizar_tablero.py`     | Script para regenerar el HTML con un export nuevo del chat.            |

## Qué guarda y qué NO

**Sí guarda:** fecha, hora, autor del mensaje, tipo (inicio/finalización/recepción), número de sumario DAYPT, cantidad de dispositivos peritados.

**No guarda:** carátulas de causas, nombres de imputados o víctimas, reseñas del hecho. El parser descarta esta información directamente — nunca entra al archivo HTML.

**Dispositivos:** se cuentan sumando todos los números en paréntesis de la reseña. Ejemplo: *"cinco (05) teléfonos celulares, un (1) pendrive, una (1) laptop"* → 7 dispositivos. El parser los trata como enteros sin guardar qué tipo son.

## Dónde ponerlo

Copiar `tablero.html` a una carpeta de red compartida del área. Cada perito lo abre con doble click desde su navegador. No requiere instalación, servidor, ni base de datos.

Primera apertura necesita internet (carga React, Tailwind y tipografías desde CDN; después quedan en caché del navegador).

## Cómo actualizar los datos

Cada semana (o cuando corresponda):

**1. Exportar el chat desde WhatsApp**

En el celular: abrir grupo → tocar el nombre arriba → Exportar chat → **Sin archivos adjuntos**.
Se recibe un archivo `_chat.txt` por mail o por transferencia interna.

**2. Regenerar el HTML**

En una PC con Python 3:
```
python3 actualizar_tablero.py _chat.txt
```

El script imprime un resumen:
```
✔ Tablero regenerado: tablero.html
  Eventos totales : 76
  Inicios         : 27
  Finalizaciones  : 20
  Recepciones     : 29
  Peritos         : 11
  Judiciales      : 4
  Rango de fechas : 2026-03-17  →  2026-04-21
```

**3. Reemplazar el archivo en la carpeta compartida.**

Listo. La próxima vez que cualquier perito abra el tablero, ve los datos nuevos.

## Interfaz solo lectura

El tablero es **solo visualización** para el equipo. Los peritos pueden:
- ✅ Ver todas las métricas y ranking
- ✅ Exportar datos a CSV si necesitan
- ❌ NO pueden importar ni modificar datos

**Solo el administrador actualiza** los datos corriendo el script Python con el export del chat. Esto evita confusión y asegura que todos vean la misma información oficial.

## Consideraciones operativas

- **Técnicos sin actividad:** Tres técnicos (Ariel Lopez, Ezequiel Vecino, Daniel Altamirano) aparecen siempre en el ranking aunque no hayan reportado pericias en el período. Se muestran con 0 puntos al final de la tabla. Si en el futuro reportan actividad, sus estadísticas se actualizarán normalmente.
- **Mensajes temporales de 7 días** están activos en el grupo. Si no se exporta al menos semanalmente, se pierden mensajes. Conviene fijar una rutina.
- **Duplicación:** el parser y la carga desde el tablero deduplican por `fecha + hora + autor + tipo + sumario`, así que se pueden superponer exports sin problema.
- **Formato:** el parser está probado con export iOS en español. Si aparece formato Android (sin corchetes, con guión), avisar para ajustar el regex.
- **Fórmula de puntaje:** inicio = 1 pt, finalización = 2 pts, dispositivo finalizado = 0.1 pt. Ejemplo: cerrar una pericia con 10 dispositivos = 2 + (10 × 0.1) = 3.0 puntos. Se puede modificar en `tablero.template.html` cambiando la constante `SCORE`.

## Reglas para una competencia sana

Sugerencia: que el criterio sea público desde el día uno. Si todos saben que finalizar vale el doble que iniciar, nadie va a abrir pericias vacías para inflar número. El panel de "sumarios únicos" también ayuda a detectar duplicaciones si alguien reporta el mismo sumario varias veces.
