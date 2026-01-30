# Variant Manager by havocado

> *What did variant B look like again?*

**Variant Manager by havocado** is a visual browser for USD variants in **Houdini Solaris**. See thumbnail previews of all variants side-by-side, compare them at a glance, and switch with one click. The tool handles all the LOP node creation behind the scenes.

This tool is for you if...

- Your scene has 50 prims with variants
- Was it `modelingVariant` or `modellingVariant`?
- You're comparing material options and forgetting what `bowl_metal_v3` looked like
- The team wants to see "all the options" right now
- You inherited a scene and have no idea what variants exist where

(TODO: fill this with screenshots)

## Core features

- Automatic scene graph scanning to find all prims with variant sets
- Viewport-based thumbnail generation for visual variant comparison
- One-click variant switching with automatic Set Variant LOP creation
- Centralized panel showing all variants across the scene
- Thumbnail gallery view for comparing multiple variants at once

## Requirements

- **Houdini 19.5 or newer** (any license)

The development was done on Houdini 21.0, but it should be compatible with any versions 19.5+.

## Installation

See [How-to-install.md](docs/How-to-install.md) for setup instructions.

## Tutorial

See [Tutorial.md](docs/Tutorial.md) to get started.