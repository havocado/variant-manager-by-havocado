## Installation

There are a few steps to make! Sorry, this is the simplest method to install an unofficial Python Panel.

## Requirements

- **Houdini 19.5 or newer** (any license)

### Step 1: Download

Go to the [Releases page](https://github.com/havocado/variant-manager-by-havocado/releases) and download `variant-manager-by-havocado-vX.X.X.zip`

### Step 2: Find the houdini packages folder

Find your Houdini preferences folder. For example:

**Windows:**
```
C:\Users\YourName\Documents\houdini19.5\packages\
```

**Mac:**
```
/Users/YourName/houdini19.5/packages/
```

**Linux:**
```
/home/YourName/houdini19.5/packages/
```

Replace `19.5` with your Houdini version:
- Houdini 19.5 → `houdini19.5`
- Houdini 20.0 → `houdini20.0`
- Houdini 20.5 → `houdini20.5`
- Houdini 21.0 → `houdini21.0`

If **`packages`** doesn't exist in the path, just create it. It is safe to create the folder.

### Checklist before moving on to the next step:

- [ ] Downloaded `variant-manager-by-havocado-vX.X.X.zip`?
- [ ] Found the folder `/path/to/houdiniXX.X/packages` (or created one)?


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
    ├── ...
    └── variant-manager-by-havocado.json
```

### Step 4: Restart Houdini

Restart Houdini.

---

You are all set! Move on to Tutorial.md (todo: link) to get started.

---

## Uninstalling

To remove the tool:

1. Close Houdini
2. Delete the JSON file:
   - `~/houdini21.0/packages/variant-manager-by-havocado.json`
3. Delete the tool folder from wherever you installed it
4. Restart Houdini