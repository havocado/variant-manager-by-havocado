# Variant Manager by havocado

Visual USD variant management for Houdini with automated contact sheet generation.

(TODO: Screenshots)

## Requirements

- **Houdini 19.5 or newer** (any license)

## Installation

### Step 1: Download

Download the latest release:
- Go to the [Releases page](https://github.com/yourusername/variant-manager-by-havocado/releases)
- Download `variant-manager-by-havocado-vX.X.X.zip`
- Extract the zip file

You should see a folder called `variant-manager-by-havocado`

### Step 2: Find Your Houdini Folder

Open your Houdini preferences folder:

**Windows:**
```
C:\Users\YourName\Documents\houdini21.0\
```

**Mac:**
```
/Users/YourName/houdini21.0/
```

**Linux:**
```
/home/YourName/houdini21.0/
```

**Important:** Replace `21.0` with your Houdini version:
- Houdini 19.5 → `houdini19.5`
- Houdini 20.0 → `houdini20.0`
- Houdini 20.5 → `houdini20.5`
- Houdini 21.0 → `houdini21.0`

### Step 3: Install the Tool

1. Inside your Houdini folder, look for a folder called **`packages`**
   - If it doesn't exist, **create it**

2. Copy the **entire** `variant-manager-by-havocado` folder somewhere on your computer (e.g., `D:\Assets\Houdini Packages\`)

3. Copy **only** the `variant-manager-by-havocado.json` file into the `packages` folder

4. Edit the `variant-manager-by-havocado.json` file and change the `VARIANT_MANAGER` path to match where you placed the tool folder:

```json
{
	"name": "variant-manager-by-havocado",
	"version": "1.0.0",
	"description": "USD Variant Manager by havocado",
	"author": "Hailey Ahn",
	"enable": true,
	"env": [
		{
			"VARIANT_MANAGER": "D:/Assets/Houdini Packages/variant-manager-by-havocado"
		}
	],
	"path": "$VARIANT_MANAGER"
}
```

**Note:** Use forward slashes `/` in the path, even on Windows.

**Your final structure should look like this:**
```
houdini21.0/
└── packages/
    └── variant-manager-by-havocado.json   (points to where you installed the tool)

D:/Assets/Houdini Packages/   (or wherever you chose)
└── variant-manager-by-havocado/
    ├── python_panels/
    └── ...
```

### Step 4: Restart Houdini

1. **Close Houdini completely** (if it's running)
2. **Start Houdini**

### Step 5: Open the Panel

1. In Houdini, click on the menu: **Windows → Python Panel Editor**
2. Under interfaces, look for **Variant Manager by havocado**
3. Click it!

The panel should open showing "Variant Manager by havocado"

---

## Upcoming Features (not implemented)

### Variant Management
- Create variant sets visually
- Add/remove variants with a click
- Switch between variants in real-time
- No Python scripting needed

### Contact Sheets
- Generate review sheets automatically
- Capture all variants at once
- Professional layouts with metadata
- Export as PNG for easy sharing

---

## Troubleshooting

### Panel Doesn't Appear in Menu

**Check these:**
1. Did you restart Houdini after installing?
2. Is the JSON file in the right place?
   - Should be: `houdini21.0/packages/variant-manager-by-havocado.json`
3. Is the `VARIANT_MANAGER` path correct in the JSON file?
   - Open the JSON and verify the path points to the actual tool folder
   - Use forward slashes `/` even on Windows
4. Does the `packages` folder exist?

**Fix:** Make sure the JSON file points to the correct location of the tool folder, then restart Houdini.

### "No Prim Selected" Error

You need to be in **Solaris** (LOP context) and select a valid USD prim path.

**Fix:**
1. Create or load a USD asset in Solaris
2. Enter the prim path (like `/sphere1`) in the panel
3. Click "Select"

### Panel Shows Up But Gives Errors

**Fix:** 
1. Check both files exist:
   - `python_panels/variant_manager_by_havocado.py`
   - `python_panels/variant_manager_by_havocado.pypanel`
2. Make sure they're inside the package folder
3. Restart Houdini

### Contact Sheets Don't Generate

Make sure:
- You have variants created
- The viewport is visible (not minimized)
- You're in Solaris context

---

## What's a Variant?

If you're new to USD variants, here's the quick version:

**Variants let you store multiple versions of the same thing in one file.**

For example, a table asset could have:
- **Material variants:** wood, metal, glass
- **Damage variants:** pristine, scratched, broken
- **LOD variants:** high, medium, low

Instead of creating `table_wood.usd`, `table_metal.usd`, `table_glass.usd`...
You create one `table.usd` with all materials as variants!

This makes it easy to:
- Switch looks without reloading files
- Keep everything organized
- Submit assets for review
- Work with layout artists

---

## Tips for Artists

### Organizing Variants

**Good variant set names:**
- `materials` (wood, metal, plastic)
- `damage` (pristine, worn, destroyed)
- `LOD` (high, medium, low)
- `colors` (red, blue, green)

**Good variant names:**
- Use lowercase and underscores: `wood_oak`, `metal_rusty`
- Be descriptive: `damage_light` not just `01`
- No spaces or special characters

### Before Submitting for Review

1. **Test all variants** - Click through each one to make sure they work
2. **Generate a contact sheet** - Shows all variants on one page
3. **Save the USD** - Don't forget to save!
4. **Include the contact sheet** - Attach it to your review submission

### Working with Multiple Artists

- Save your USD files regularly
- Use version control (like Git) for your USD files
- Keep variant names consistent across assets
- Document your variant sets in your asset README

---

## Uninstalling

To remove the tool:

1. Close Houdini
2. Delete the JSON file:
   - `~/houdini21.0/packages/variant-manager-by-havocado.json`
3. Delete the tool folder from wherever you installed it
4. Restart Houdini

Done! The tool is completely removed.

---

## Updates

### Checking for Updates

1. Go to the [Releases page](https://github.com/yourusername/variant-manager-by-havocado/releases)
2. Check the version number
3. If there's a new version, download it

### Installing Updates

1. **Replace the tool folder** with the new version (wherever you installed it)
2. **Restart Houdini**

The JSON file in packages can stay the same as long as you keep the tool in the same location.

Your settings and preferences will be preserved.

---

## Credits

**Built with:** Python, PySide2


## Version

**Compatible with:** Houdini 19.5+

