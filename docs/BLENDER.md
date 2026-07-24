# Blender Foundation — BM-S7

## Scene setup

```text
Units        Metric
Unit Scale   1.0
Forward      -Y
Up           Z
```

## Collections

```text
BM_S7
├── 00_ROOT
├── 10_CORE
├── 20_TOP
├── 30_FRONT
├── 40_BOTTOM
├── 50_MAG
├── 60_COSMETICS
├── 70_SOCKETS
├── 80_RIG
└── 90_GUIDES
```

## Required objects for the first blockout

```text
BM_SIDEARM_ROOT
BM_S7_CORE_frame
BM_S7_CORE_slide_shell
BM_S7_CORE_grip

SOCKET_TOP
SOCKET_BOTTOM
SOCKET_FRONT
SOCKET_MAG
SOCKET_GRIP
```

## Blockout rule

The first milestone is silhouette and modular separation only.

Do not add microdetail, screws, engravings or final materials until:

- root transform is clean;
- all module boundaries are obvious;
- every socket exists;
- origins are intentional;
- exploded view can be posed without geometry breaking visually.

## Modifier baseline

For hard-surface blockout:

```text
Mirror
Bevel
Weighted Normal
```

Keep destructive booleans out of the first blockout whenever possible.

## Material placeholders

```text
BM_MAT_POLISHED_STEEL
BM_MAT_GRIP
BM_MAT_OPTIC_GLASS
BM_MAT_EMISSIVE_RED
```

At blockout stage these can remain simple viewport materials.

## First animation test

Create one simple assembly action:

```text
0f    exploded
20f   approach
28f   alignment
34f   lock
40f   completed
```

Only the TOP module needs to move in the first test. The purpose is to validate the socket contract, not produce final animation.

## Definition of done — Phase 0 Blender

- [ ] `BM_Sidearm_MASTER.blend` exists.
- [ ] BM-S7 core silhouette exists.
- [ ] Root is at world origin.
- [ ] Scale is applied.
- [ ] Five canonical sockets exist.
- [ ] TOP test module snaps to `SOCKET_TOP`.
- [ ] Exploded and assembled poses are both readable.
- [ ] No internal functional mechanism is modeled.
