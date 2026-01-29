<img width="1318" height="964" alt="image" src="https://github.com/user-attachments/assets/57024fcf-5e81-4a03-8dc5-2a650f7ce79a" /># How to use the Variant Manager

Table of contents:

(todo: add table of contents)

## 0. Test scene setup

This tutorial will use Pixar's Kitchen set as an example. If you already have your own, skip this section!

- Pixar's Kitchen Set USD download link: https://openusd.org/release/dl_downloads.html

### 0-1. Set up Houdini Solaris

If you already know solaris, you can skip this setup.

USD scenes can't be simply imported like other formats. Instead, we start by creating a LOP network node (tab >> LOP Network node). Double click to enter LOP.

<img width="1086" height="731" alt="scene_setup_1_lopnet_1" src="https://github.com/user-attachments/assets/ed4abbd3-ae87-44d3-b01f-7c25a747480a" />

Create an asset reference node, and set the file reference param to path to Kitchen_Set.usd.

- There are different ways to compose a USD scene, depending on the workflow. For example importing as a sublayer instead of a reference is big difference, which this margin of this tutorial is too narrow to contain. We will keep it simply as a reference import.

<img width="1150" height="955" alt="scene_setup_2_node" src="https://github.com/user-attachments/assets/accf7449-268d-4bce-af13-89f31501f48b" />

Import is success if you see the kitchen in the viewport. Make sure you are inside LOP.

## 1. Install the tool

Follow the installation guide: (todo: link)

From one of the panels, click on the + button to import: New Pane Type >> Misc >> Python Panel.

<img width="1358" height="989" alt="scene_setup_3_PythonPanel" src="https://github.com/user-attachments/assets/a95d711c-1295-4b32-9b1f-49dfc23e4ea9" />

Click on the dropdown and select **Variant Manager by havocado.**

<img width="1144" height="955" alt="scene_setup_4_variantManager" src="https://github.com/user-attachments/assets/8aa116f2-d52d-4846-b7e4-e661ce905baa" />

Success if you see the tool loaded.

<img width="1459" height="955" alt="scene_setup_5_success" src="https://github.com/user-attachments/assets/eebade60-94d4-497f-9255-5b0deb669366" />

## 2. Choosing the LOP node path

The LOP node path is automatically set to the selected LOP node on opening the tool. To set the LOP path manually, use the dropdown:

<img width="1187" height="964" alt="tutorial_2_lop_dropdown" src="https://github.com/user-attachments/assets/1e76106f-fc1f-412c-ad2e-2dcf6f8f6507" />

## 3. Scene graph

The scene graph shows only the prims with variants. Click on the prim to see the details:

<img width="1187" height="964" alt="tutorial_3_inspector" src="https://github.com/user-attachments/assets/b16bfae9-8467-4dfc-b3fc-b65a441aaa50" />

## 4. Quick Switch Variant

Click on the Switch button to switch variant.

<img width="733" height="459" alt="tutorial_4_switch" src="https://github.com/user-attachments/assets/2f75df22-acab-483b-990d-82bc6401ad5e" />

Check the LOP network to see the Set Variant Node created.

<img width="1187" height="964" alt="tutorial_5_switch" src="https://github.com/user-attachments/assets/c0ee37ea-b2fd-4c76-aa34-a78adaf99132" />

The switch buttons will create a new node every time it is clicked. The Varaiant Manager doesn't rely on the new node, so it allows the new node to be safely modified/deleted.

## 5. Variants Preview

With a prim selected, open the Comparison Tab and click on the Preview button.

<img width="728" height="548" alt="tutorial_6_preview" src="https://github.com/user-attachments/assets/d0384f1c-5c61-42bd-af08-5f3a2dda6116" />

<img width="1318" height="964" alt="tutorial_7_preview" src="https://github.com/user-attachments/assets/446727cc-dc65-4d60-8119-c6b4da0a068b" />

This creates thumbnail view of the variant from the viewport camera. While it renders, viewport may show the variants changing while it captures each variants.

This may take a long time if using a slower renderer such as Karma inside the viewport (which is why you need to press the preview button every time)

There will be a set variant node inside the LOP reserved for preview captures. Please don't delete this node, it should delete itself on closing the tool. The created thumbnails will be auto deleted when the Variant Manager closes.

---

That's it for v1.0! Please report any bugs to github issues.

#### v2.0 ?

**Contact Sheet generation**
- This is the first thing on my list. The only problem is avoiding external libraries for working with pdf, because I don't want to make installing more complicated than this.

**Auto Turntables export**
- I think this would be nice. Auto generate all variants turntables in 1-click! But it won't be done very soon, there will be a lot of configs to deal with.
