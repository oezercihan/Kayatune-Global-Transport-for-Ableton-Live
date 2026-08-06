# Installation – Kayatune Global Transpose

## Voraussetzungen

- Ableton Live mit Max for Live
- Kayatune
- MIDI-Verbindung vom Kayatune-Signalweg zum Mac/PC
- Installiertes **Launchpad Duo Sync Pro**

## 1. Max-for-Live-Device installieren

Kopiere den gesamten Ordner:

```text
Max MIDI Effect
```

an einen dauerhaften Ort oder in deine Ableton User Library, zum Beispiel:

### macOS

```text
~/Music/Ableton/User Library/Presets/MIDI Effects/Max MIDI Effect/Kayatune Global Transpose/
```

### Windows

```text
Dokumente/Ableton/User Library/Presets/MIDI Effects/Max MIDI Effect/Kayatune Global Transpose/
```

Wichtig: Diese beiden Dateien zusammenlassen:

```text
Kayatune Global Transpose.amxd
kayatune_sysex_parser.js
```

## 2. Device laden

1. Erstelle in Ableton eine MIDI-Spur.
2. Ziehe `Kayatune Global Transpose.amxd` auf diese Spur.
3. Wähle als `MIDI From` den USB-MIDI-Adapter oder MIDI-Port, über den die Kayatune-SysEx-Daten ankommen.
4. Stelle `Monitor` auf `In`.

## 3. MIDI-Port in Ableton aktivieren

Unter:

```text
Einstellungen → Link, Tempo & MIDI
```

muss beim verwendeten MIDI-Eingang `Track` aktiviert sein.

## 4. Funktion prüfen

Ändere am Kayatune den Transpose-Wert.

Erwartetes Verhalten:

- Die Anzeige im M4L-Device ändert sich.
- Ableton-Clips werden durch Launchpad Duo Sync Pro transponiert.
- Beide Launchpads zeigen den aktuellen Wert an.

## 5. Device-Abhängigkeiten einbetten

Öffne das Device im Max-Editor und nutze, sofern verfügbar:

```text
Freeze Device / Collect All and Save
```

Danach erneut speichern. Dadurch kann der JavaScript-Parser in das Device eingebettet werden.

## Optionaler Companion-Fallback

Nur verwenden, wenn der direkte Max-for-Live-SysEx-Weg nicht genutzt werden soll.

1. Ordner `Optional Companion` öffnen.
2. `Install.command` einmal starten.
3. Danach `Start.command` oder `Start Console.command` starten.
4. Das Max-for-Live-Device in diesem Fall nicht gleichzeitig senden lassen.

## Fehlerbehebung

### Device zeigt keinen Wert

- MIDI-Spur: `Monitor = In`
- korrekter MIDI-Eingang ausgewählt
- `Track` für den Eingang aktiviert
- `sysexin all` im Patch vorhanden
- Max Console auf fehlende `kayatune_sysex_parser.js` prüfen

### Max meldet fehlende JavaScript-Datei

Lege `kayatune_sysex_parser.js` direkt neben die `.amxd`, lade das Device neu und speichere es anschließend mit eingebetteten Abhängigkeiten.

### Launchpads reagieren nicht

Prüfe, ob Launchpad Duo Sync Pro geladen ist und im Log auf `127.0.0.1:45831` lauscht.
