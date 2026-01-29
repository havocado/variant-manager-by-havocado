# Variant Manager by havocado

Visual USD variant management for Houdini.



(TODO: fill this with screenshots)

## Requirements

- **Houdini 19.5 or newer** (any license)

The development was done on Houdini 21.0, but it should be compatible with any versions 19.5+.

## Installation

There are a few steps to make! Sorry, this is the simplest method to install an unofficial Python Panel.

### Step 1: Download

Download the latest release:
- Go to the [Releases page](https://github.com/havocado/variant-manager-by-havocado/releases)
- Download `variant-manager-by-havocado-vX.X.X.zip`
- Extract the zip file

You should see a folder called `variant-manager-by-havocado`

### Step 2: Find Houdini Packages Folder

Find your Houdini preferences folder. For example:

**Windows:**
```
C:\Users\YourName\Documents\houdini19.5\
```

**Mac:**
```
/Users/YourName/houdini19.5/
```

**Linux:**
```
/home/YourName/houdini19.5/
```

Replace `19.5` with your Houdini version:
- Houdini 19.5 → `houdini19.5`
- Houdini 20.0 → `houdini20.0`
- Houdini 20.5 → `houdini20.5`
- Houdini 21.0 → `houdini21.0`

Then add find a folder **`packages`**. If it doesn't exist, **create it**.

### Checklist before moving on to the next step:

- [ ] Downloaded `variant-manager-by-havocado-vX.X.X.zip`
- [ ] Found the folder `/path/to/houdiniXX.X/packages` (or created one)


### Step 3: Extract files


1. Extract the `variant-manager-by-havocado.zip` somewhere on your computer (e.g., `D:\Assets\Houdini Packages\`, or wherever you want)

3. Copy **only** the `variant-manager-by-havocado.json` file into the `packages` folder. (Copy only, don't delete the extracted folder!)

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
			"VARIANT_MANAGER": "change/this/path/to/variant-manager-by-havocado"
		}
	],
	"path": "$VARIANT_MANAGER"
}
```

- [ ] Make sure the path ends with `/variant-manager-by-havocado`

- [ ] Use forward slashes `/` in the path, even on Windows.

**Your final structure should look like this:**
```
houdini21.0/
└── packages/
    └── variant-manager-by-havocado.json   (points to where you installed the tool)

D:/Assets/Houdini Packages/   (or wherever you chose)
└── variant-manager-by-havocado/
    ├── python_panels/
    ├── README.md
    └── variant-manager-by-havocado.json
```

### Step 4: Restart Houdini

Restart Houdini.

### Step 5: Open the Panel

1. In Houdini, click on the menu: **Windows → Python Panel Editor**
2. Under interfaces, look for **Variant Manager by havocado**
3. Click it!

The panel should open showing "Variant Manager by havocado"

(todo: gif here)

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

---

## Uninstalling

To remove the tool:

1. Close Houdini
2. Delete the JSON file:
   - `~/houdini21.0/packages/variant-manager-by-havocado.json`
3. Delete the tool folder from wherever you installed it
4. Restart Houdini

