# Architecture — BLACKMAMBA Weapon Assembly System

## 1. Regla principal

El asset 3D y la configuración del videojuego son capas distintas.

```text
Blender Asset Layer
        ↓
Canonical Socket Contract
        ↓
Build Configuration Data
        ↓
Game Runtime
```

Blender define geometría, pivotes, materiales, sockets y animaciones. El runtime decide qué módulos están activos y qué estadísticas de gameplay representan.

## 2. Identidad canónica

Plataforma inicial:

```text
BM-S7
```

Root de Blender:

```text
BM_SIDEARM_ROOT
```

Categorías válidas de módulos:

```text
CORE
TOP
FRONT
BOTTOM
MAG
COSMETICS
```

## 3. Contrato de sockets

Los nombres de sockets son parte de la API del asset y no deben cambiarse sin migración.

```text
SOCKET_TOP
SOCKET_BOTTOM
SOCKET_FRONT
SOCKET_MAG
SOCKET_GRIP
```

Cada socket debe cumplir:

- Transform local limpio.
- Escala `1,1,1`.
- Rotación aplicada cuando sea posible.
- Parent directo o indirecto de `BM_SIDEARM_ROOT`.
- Nombre único dentro de la plataforma.

## 4. Naming convention

### Objetos

```text
BM_<platform>_<category>_<name>
```

Ejemplos:

```text
BM_S7_CORE_frame
BM_S7_TOP_red_dot
BM_S7_BOTTOM_sensor
BM_S7_MAG_primary
BM_S7_COSMETIC_grip_panel
```

### Materiales

```text
BM_MAT_<name>
```

Ejemplos:

```text
BM_MAT_POLISHED_STEEL
BM_MAT_GRIP
BM_MAT_OPTIC_GLASS
BM_MAT_EMISSIVE_RED
```

### Empties / sockets

```text
SOCKET_<slot>
```

### Armature bones

```text
BONE_root
BONE_slide
BONE_mag
BONE_optic
BONE_sensor
```

## 5. Transform contract

Antes de exportar:

```text
Scale    = 1,1,1
Root     = 0,0,0
```

El origen del objeto debe representar su punto de animación, no simplemente el centro geométrico.

## 6. Assembly states

Cada módulo intercambiable puede representarse mediante tres transforms conceptuales:

```text
assembly_start
assembly_approach
assembly_end
```

El estado final debe coincidir exactamente con el socket correspondiente.

## 7. Build configuration

Una build es un documento de datos.

```json
{
  "schema_version": 1,
  "platform": "BM-S7",
  "modules": {
    "top": "MAMBA_RD01",
    "bottom": "X_TAC",
    "front": null,
    "mag": "DUAL"
  },
  "cosmetics": {
    "finish": "polished_black",
    "grip": "serpent_scale",
    "engraving": "BLACKMAMBA"
  }
}
```

## 8. Invariantes

Una configuración válida debe cumplir:

1. `platform` existe.
2. Cada módulo declara un slot válido.
3. Un socket sólo puede contener un módulo activo a la vez.
4. Cosmetics no alteran la topología necesaria para ensamblaje.
5. El runtime no depende de nombres de mesh arbitrarios fuera del contrato canónico.
6. Los stats de gameplay no se derivan de dimensiones físicas del modelo.

## 9. Scope

El sistema está diseñado para assets y comportamiento visual de un videojuego ficticio. No se modelan mecanismos internos funcionales ni instrucciones de fabricación de armas reales.
