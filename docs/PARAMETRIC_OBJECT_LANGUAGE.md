# BlackMamba Parametric Object Language

## Core idea

The project is not fundamentally about one weapon, one prop, or one Blender scene.

It is about building a reusable geometric language where a small canonical primitive can describe, seed, constrain, or generate many unrelated objects.

A simple cylinder-like primitive may become the reference for:

- a drum
- a cartridge-shaped game prop
- a drinking glass
- a bed leg
- a table leg
- a bottle
- a piston-like sci-fi prop
- a lamp body
- a speaker enclosure
- a knob
- a wheel hub
- a column
- a pipe segment
- a container
- a handle
- a structural support
- an ornamental piece

The important asset is therefore not the final mesh. The important asset is the **parametric description** that can be reused across domains.

## Principle

> Model the rule before modeling the object.

Instead of storing only geometry, every canonical primitive should expose a compact semantic and parametric contract.

Example:

```json
{
  "primitive": "axial_body",
  "profile": "cylindrical",
  "height": 1.0,
  "radius_top": 0.25,
  "radius_bottom": 0.25,
  "wall": 0.03,
  "segments": 32,
  "cap_top": true,
  "cap_bottom": true,
  "taper": 0.0,
  "bevel": 0.02,
  "material_role": "generic"
}
```

That description can be interpreted by different generators, styles, and domains without changing the underlying geometric logic.

## Canonical primitive families

The first object library should be intentionally small.

### 1. Axial body

Cylinders, tubes, tapered columns, shells and rotational bodies.

Possible uses:

- glass
- bottle
- leg
- drum
- pipe
- barrel-shaped fictional prop
- flashlight body
- speaker body

### 2. Box body

Rectangular and chamfered volumes.

Possible uses:

- furniture
- electronics
- crates
- housings
- architectural blocks
- game props

### 3. Profile extrusion

A 2D profile extruded along one axis.

Possible uses:

- rails
- trims
- beams
- handles
- brackets
- structural pieces

### 4. Revolved profile

A radial profile revolved around an axis.

Possible uses:

- cups
- vases
- knobs
- wheels
- decorative legs
- containers

### 5. Sweep

A profile following a path.

Possible uses:

- cables
- tubing
- handles
- branches
- frames
- decorative curves

### 6. Surface shell

A thin surface with optional thickness.

Possible uses:

- panels
- covers
- body shells
- leaves
- fabric-like rigid surfaces

## Geometry is separated from meaning

The same generated geometry can receive different semantic identities.

```text
axial_body
   |
   +-- semantic: glass
   +-- semantic: furniture_leg
   +-- semantic: drum
   +-- semantic: sci_fi_prop
   +-- semantic: bottle
```

Meaning should not be hardcoded into the mesh generator.

This allows the system to reuse one generator while changing:

- proportions
- materials
- naming
- connectors
- interaction rules
- animation
- physics metadata
- rendering style
- LOD policy

## Object descriptor

Every generated object should eventually be describable through a common descriptor.

```json
{
  "id": "OBJ_0001",
  "family": "axial_body",
  "semantic": "glass",
  "parameters": {},
  "connectors": [],
  "materials": [],
  "modifiers": [],
  "metadata": {}
}
```

The descriptor becomes the source of truth.

The Blender mesh is an output of the descriptor, not the descriptor itself.

## Transformation pipeline

```text
semantic intent
      ↓
primitive family
      ↓
parameter set
      ↓
canonical generator
      ↓
modifier stack
      ↓
material/style layer
      ↓
connectors + metadata
      ↓
Blender / game engine / renderer / manufacturing-safe visualization
```

## Reference objects

The first objects should be deliberately simple because their purpose is to validate the language rather than impress visually.

Suggested progression:

```text
01 axial cylinder
02 hollow cup
03 tapered leg
04 closed container
05 radial drum
06 box body
07 profile extrusion
08 swept tube
```

From these few reference objects, many higher-level assets can be composed.

## Composition

Complex objects should be assemblies of descriptors rather than monolithic meshes.

Example:

```text
TABLE
├── top: box_body
├── leg_01: axial_body
├── leg_02: axial_body
├── leg_03: axial_body
└── leg_04: axial_body
```

```text
BED
├── frame: profile_extrusion
├── leg_01: axial_body
├── leg_02: axial_body
├── leg_03: axial_body
├── leg_04: axial_body
└── panels: surface_shell
```

The exact same `axial_body` generator can therefore participate in furniture, architecture, props, vehicles, or fictional equipment.

## Parametric inheritance

Objects should be able to derive from a base descriptor and override only what changes.

```text
AXIAL_BODY_BASE
    ↓
GLASS_BASE
    ↓
WHISKEY_GLASS
```

or

```text
AXIAL_BODY_BASE
    ↓
FURNITURE_LEG_BASE
    ↓
BED_LEG_CLASSIC
```

This avoids duplicated geometry definitions.

## Constraints

Parameters should support constraints rather than arbitrary coordinates.

Examples:

```text
height > 0
radius_top > 0
radius_bottom > 0
wall < min(radius_top, radius_bottom)
bevel >= 0
segments >= minimum_quality
```

Later, constraints may relate several objects:

```text
leg.height = bed.frame.clearance
connector.position = parent.bounds.bottom_center
cup.wall = clamp(radius * 0.05)
```

## AI role

AI should operate primarily on descriptors and relationships, not raw vertex editing.

An instruction such as:

> make this wider, shorter, hollow and suitable as a glass

should ideally become a structured change such as:

```json
{
  "semantic": "glass",
  "parameters": {
    "height": 0.65,
    "radius_top": 0.38,
    "radius_bottom": 0.32,
    "wall": 0.025,
    "cap_top": false
  }
}
```

This creates reproducibility, undoability and deterministic regeneration.

## Long-term direction

The eventual system can become a universal object authoring layer:

```text
natural language
      ↓
semantic object graph
      ↓
parametric descriptors
      ↓
geometry generators
      ↓
Blender scene
      ↓
renderer / game engine / visualization
```

The first cylinder is therefore not just a cylinder.

It is the first word in the BlackMamba geometric language.
