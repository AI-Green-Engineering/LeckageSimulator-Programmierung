# LeckageSimulator-Programmierung

Dieses Repository enthält erste Python-Prototypen zur seriellen Ansteuerung eines Leckage-Simulators (Ventil/Antrieb), inkl. einfacher CLI-Skripte, eines kleinen Flask-Servers und Prototyp-Skripten für Referenzfahrt/Baseline-Ermittlung.

## Projektziel (aktuell)
- Serielle Kommunikation mit dem Prototyp sicherstellen.
- Grundlegende Befehlslogik für **Öffnen/Schließen/Referenzieren** testen.
- Erste Automatisierungsschritte für Baseline-Messläufe aufbauen.
- Leckageverläufe simulieren, indem der Leckagesimulator für die **schrittweise Öffnung eines Drosselventils mittels Schrittmotor** programmiert wird.

## Struktur des Repos
- `leakage.py`  
  Minimales interaktives CLI-Tool: sendet beliebige Eingaben über Serial an das Gerät.
- `bearing.py`  
  Sendet Startbefehl `S` und liest danach kontinuierlich Zeilen vom Serial-Port.
- `server.py`  
  Einfacher Flask-Server mit zwei Buttons (`open`/`close`), die Serial-Kommandos senden.
- `prototype_leakage/find_reference_point.py`  
  Interaktive Kommandoprüfung (Regex), lokale `stepCounter`-Verfolgung, Senden validierter Kommandos.
- `prototype_leakage/collectBaseline.py`  
  Prototyp für sequenzielles Öffnen in festen Schritten mit Wartezeit.

## Aktuelle Entwicklungen (Stand: 2026-03-24)
- Erste End-to-End-Verbindung über einen fest verdrahteten USB-Serial-Pfad vorhanden.
- Ein einfacher HTTP-Einstiegspunkt zur manuellen Bedienung ist über `server.py` vorhanden.

## Nächste To-dos
1. Generelle Überarbeitung und Kommentierung des Codes.
2. Zehn Rampen entsprechend der Weibullverteilung einprogrammieren, die einem typischen Degradationsverlauf entsprechen.
3. Wartungsbuch bzw. Logbuch für die Experimentdurchführung ergänzen.

## Hintergrundinfos
- **Zielhardware:** Raspberry Pi zur Ansteuerung eines Schrittmotors; der Schrittmotor gibt die Schritte zum Öffnen/Schließen eines Drosselventils in einer Pneumatikleitung vor.
- **Sicherheitsgrenzen:** vorläufige Orientierung bei ca. 2500 Schritten; finale Grenzen werden noch festgelegt.
- **Zweck der Programmierung:** Der Code in diesem Repo soll wiederverwendbar und mehrfach nutzbar sein, um Verläufe und Leckageentwicklungen darzustellen.

---

Wenn du möchtest, kann ich als nächsten Schritt die To-dos direkt in konkrete Arbeitspakete mit Reihenfolge und Aufwandsschätzung aufteilen.
