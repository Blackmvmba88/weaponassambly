# BLACKMAMBA Weapon Assembly System

> **Una plataforma. Muchas configuraciones. Una sola lógica de ensamblaje.**

Sistema modular de armas **ficticias para videojuego táctico**, diseñado alrededor de Blender y una arquitectura de piezas intercambiables. El objetivo es construir assets visuales, animaciones de ensamblaje, configuraciones de loadout y datos de gameplay sin replicar mecanismos internos funcionales de armas reales.

## Visión

`weaponassambly` será la base del taller BlackMamba: una plataforma 3D donde un arma ficticia puede descomponerse visualmente en módulos, inspeccionarse, cambiar de configuración y volver a ensamblarse mediante sockets definidos.

```text
CORE + MODULE + SKIN + OPTIC + SENSOR = BUILD
```

## Plataforma inicial — BM-S7

```text
BM_SIDEARM_ROOT
│
├── CORE
│   ├── frame
│   ├── slide_shell
│   └── grip
│
├── TOP
│   ├── optic_mount
│   ├── red_dot
│   └── thermal_module
│
├── FRONT
│   └── cosmetic_front_module
│
├── BOTTOM
│   ├── rail
│   ├── light_module
│   └── sensor_module
│
├── MAG
│   ├── magazine_A
│   ├── magazine_B
│   └── coupler
│
└── COSMETICS
    ├── grip_panel
    ├── engraving
    ├── emblem
    └── skins
```

## Sockets canónicos

```text
SOCKET_TOP
SOCKET_BOTTOM
SOCKET_FRONT
SOCKET_MAG
SOCKET_GRIP
```

Cada módulo se conecta únicamente mediante su socket. La geometría no define la lógica de gameplay; la lógica vive en datos.

## Pipeline Blender

```text
blockout
→ silhouette
→ primary shapes
→ secondary shapes
→ modular split
→ materials
→ UV / bake
→ rig
→ assembly animation
→ LODs
→ game export
```

### Colecciones propuestas

```text
BLACKMAMBA_SIDEARM
├── BODY
├── OPTIC
├── SENSOR
├── MAGAZINES
├── DETAILS
└── RIG
```

## Animación de ensamblaje

Cada pieza intercambiable tendrá tres estados espaciales:

```text
assembly_start
assembly_approach
assembly_end
```

Timeline base:

```text
0f    exploded
20f   approach
28f   alignment
34f   lock
40f   completed
```

Esto permitirá construir una vista de taller con cámara cinematográfica, exploded view e inspección individual de módulos.

## Build data

Las configuraciones del juego se describen como datos y no como modelos duplicados.

```json
{
  "platform": "BM-S7",
  "finish": "polished_black",
  "optic": "MAMBA_RD01",
  "bottom_module": "X_TAC",
  "mag_style": "dual",
  "grip": "serpent_scale",
  "engraving": "BLACKMAMBA"
}
```

Ejemplos de variantes futuras:

```text
BM-S7 Phantom
BM-S7 Chrome
BM-S7 Viper
BM-S7 Nightfall
BM-S7 Royal
```

## Principios del proyecto

1. **La arquitectura sigue al sistema modular.** Ninguna pieza debe depender de coordenadas mágicas o geometría accidental.
2. **Un asset base, muchas builds.** Evitar duplicar modelos completos para cada variante.
3. **Sockets antes que animaciones.** Los puntos de ensamblaje son parte del contrato del asset.
4. **Datos antes que lógica visual.** Blender crea el asset; el juego decide la configuración.
5. **Diseño ficticio y no funcional.** El proyecto modela apariencia, interfaz y comportamiento de videojuego, no mecanismos internos reales.

## Estructura del repositorio

```text
weaponassambly/
├── blender/
│   ├── master/
│   ├── high/
│   └── game/
├── configs/
├── docs/
├── exports/
├── reference/
├── scripts/
└── textures/
```

## Roadmap inmediato

### Phase 0 — Foundation
- [x] Definir plataforma inicial BM-S7.
- [x] Definir jerarquía modular.
- [x] Definir sockets canónicos.
- [ ] Crear escena `BM_Sidearm_MASTER.blend`.
- [ ] Crear blockout del CORE.

### Phase 1 — Modular Asset
- [ ] Separar TOP / FRONT / BOTTOM / MAG / COSMETICS.
- [ ] Validar origins y sockets.
- [ ] Crear materiales BlackMamba base.
- [ ] Crear exploded view.

### Phase 2 — Assembly Runtime
- [ ] Definir esquema JSON de builds.
- [ ] Crear validador de configuraciones.
- [ ] Crear animación de ensamblaje.
- [ ] Preparar exportación a motor de juego.

### Phase 3 — Workshop
- [ ] Cámara orbital.
- [ ] Selección de módulos.
- [ ] Preview de skins.
- [ ] Estadísticas de gameplay desacopladas del mesh.
- [ ] Presets de builds.

## Estado

**v0.0.1 — Foundation**

Primer objetivo operativo: crear un blockout limpio de la BM-S7 con jerarquía, origins y sockets correctos antes de añadir detalle visual.
