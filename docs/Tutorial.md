<img width="769" height="508" alt="tutorial_2_lop_dropdown" src="https://github.com/user-attachments/assets/59c4573d-1de7-490b-a840-f351874872a7" /># How to use the Variant Manager

Table of contents:

- [0. Test scene setup](#0-test-scene-setup)
  - [0-1. Set up Houdini Solaris](#0-1-set-up-houdini-solaris)
- [1. Install the tool](#1-install-the-tool)
  - [Troubleshooting - Panel Doesn't Appear in Menu](#troubleshooting---panel-doesnt-appear-in-menu)
- [2. Choosing the LOP node path](#2-choosing-the-lop-node-path)
- [3. Scene graph](#3-scene-graph)
- [4. Quick Switch Variant](#4-quick-switch-variant)
- [5. Variants Preview](#5-variants-preview)

## 0. Test scene setup

This tutorial will use Pixar's Kitchen set as an example. If you already have your own, skip this section!

- Pixar's Kitchen Set USD download link: https://openusd.org/release/dl_downloads.html

### 0-1. Set up Houdini Solaris

If you already know solaris, you can skip this setup.

USD scenes can't be simply imported like other formats. Instead, we start by creating a LOP network node (tab >> LOP Network node). Double click to enter LOP.

<img width="1086" height="690" alt="scene_setup_1_lopnet_1" src="https://github.com/user-attachments/assets/b0006eb4-eaf2-441e-85ef-322e0fd554e2" />

Create an asset reference node, and set the file reference param to path to Kitchen_Set.usd.

- There are different ways to compose a USD scene, depending on the workflow. For example importing as a sublayer instead of as a reference is big difference, which this margin of this tutorial is too narrow to contain. We will keep it simply as a reference import.

<img width="1150" height="835" alt="scene_setup_2_node" src="https://github.com/user-attachments/assets/c540857a-cc9a-4fe1-a24a-b51827463e7e" />

Import is successful if you see the kitchen in the viewport. Make sure you are inside LOP.

## 1. Install the tool

Follow the installation guide: [How-to-install.md](How-to-install.md)

From one of the panels, click on the + button to import: New Pane Type >> Misc >> Python Panel.

<img width="837" height="561" alt="scene_setup_3_PythonPanel" src="https://github.com/user-attachments/assets/65e8d420-ee5d-4299-9820-ecaf935faf32" />

Click on the dropdown and select **Variant Manager by havocado.**

<img width="625" height="379" alt="scene_setup_4_variantManager" src="https://github.com/user-attachments/assets/a3e01367-e4bf-4477-bd0c-805c35e9be4b" />

Success if you see the tool loaded.

<img width="825" height="649" alt="scene_setup_5_success" src="https://github.com/user-attachments/assets/2014bd5f-d507-41c4-8dd2-8ca722731057" />

### Troubleshooting - Panel Doesn't Appear in Menu

1. Did you restart Houdini after installing the plugin?
2. Is the JSON file in the right place?
   - Should be: `houdini21.0/packages/variant-manager-by-havocado.json`
3. Is the `VARIANT_MANAGER` path correct in the JSON file?
   - Open the JSON file and verify the path points to the actual tool folder
   - Use forward slashes `/` even on Windows
4. Does the `packages` folder exist?

## 2. Choosing the LOP node path

The LOP node path is automatically set to the selected LOP node on opening the tool. To set the LOP path manually, use the dropdown:

<img width="769" height="508" alt="tutorial_2_lop_dropdown" src="https://github.com/user-attachments/assets/3600e420-5201-42e3-bfa1-410d46cba36e" />

## 3. Scene graph

The scene graph shows only the prims with variants. Click on the prim to see the details:

<img width="776" height="496" alt="tutorial_3_inspector" src="https://github.com/user-attachments/assets/7a729343-c40e-466c-a970-3db3ee3b4496" />

## 4. Quick Switch Variant

Click on the Switch button to switch variant.

<img width="733" height="459" alt="tutorial_4_switch" src="https://github.com/user-attachments/assets/096d4237-a02c-4e1c-81e5-bd213f621839" />

Check the LOP network to see the Set Variant Node created.

<img width="1187" height="756" alt="tutorial_5_switch" src="https://github.com/user-attachments/assets/1e27839b-8b94-469f-aa3f-e04aa0b9bb29" />

The switch button will create a new node every time it is clicked. The Variant Manager doesn't rely on the new node, so it allows the new node to be safely modified/deleted.

## 5. Variants Preview

With a prim selected, open the Comparison Tab and click on the Preview button.

<img width="728" height="548" alt="tutorial_6_preview" src="https://github.com/user-attachments/assets/ce73e8f7-518f-4c0b-a733-dcb2cff3cdae" />

<img width="1318" height="755" alt="tutorial_7_preview" src="https://github.com/user-attachments/assets/dfbe1176-a8fa-4ae5-9b80-3db4a543b339" />

This creates thumbnail view of the variant from the viewport camera. While it renders, viewport may show the variants changing while it captures each variants.

This may take a long time if you are using a slower renderer such as Karma inside the viewport (which is why you need to press the preview button every time)

There will be a set variant node inside the LOP reserved for preview captures. Please don't delete this node, it should delete itself on closing the tool. The created thumbnails will be auto deleted when the Variant Manager closes.

---

That's it for v1.0! Please report any bugs to [github issues](https://github.com/havocado/variant-manager-by-havocado/issues).

#### v2.0 ?

**Contact Sheet generation**
- This is the first thing on my list. The only problem is avoiding external libraries for working with pdf files, because I don't want to make installing more complicated than this.

**Auto Turntables export**
- I think this would be nice. Auto generate all variants turntables in 1-click! But it won't be done very soon, there will be a lot of configs to deal with.

