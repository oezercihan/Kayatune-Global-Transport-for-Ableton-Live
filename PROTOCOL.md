# Kayatune-Protokoll

Bestätigte relevante SysEx-Struktur:

```text
F0 43 10 7F 1C 07 00 00 01 VV F7
```

`VV` kodiert den absoluten Transpose-Wert mit Offset `0x40`:

```text
3F = -1
40 =  0
41 = +1
42 = +2
```

Berechnung:

```text
transpose = VV - 0x40
```

An Launchpad Duo Sync Pro wird gesendet:

```text
LDS1:<transpose>
```
