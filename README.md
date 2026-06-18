# Forja Digital

Pipeline inicial de Forja Digital para ingesta manual de iniciativas desde una carpeta `inbox`.

## Alcance actual

- Ingesta manual de archivos `.md` en `inbox/`.
- Validacion de frontmatter YAML.
- Enrutado de archivos:
  - validos -> `archive/`
  - invalidos -> `rejected/`
- Creacion de iniciativa en `projects/<initiative_id>/`.

## Estructura esperada

```
forja-digital/
  inbox/
  processing/
  archive/
  rejected/
  projects/
```

## Frontmatter requerido

- `title`
- `problem`
- `target_user`
- `desired_outcome`
- `constraints`
- `budget_level`
- `urgency`
- `author`

## Uso

1. Instalar dependencias:

```powershell
python -m pip install -e .[dev]
```

2. Dejar uno o mas `.md` en `inbox/`.

3. Ejecutar la ingesta:

```powershell
python -m forja_digital_ingest.cli --base-dir .
```

## Ejemplo de archivo en inbox

```md
---
title: Sistema de reservas para pistas deportivas
problem: Los vecinos no tienen un sistema unico de reserva
target_user: Vecinos de la urbanizacion
desired_outcome: Reservas online y calendario comun
constraints: Presupuesto limitado y lanzamiento rapido
budget_level: low
urgency: medium
author: molero86
---

Descripcion libre del proyecto.
```
