# How to use the Variant Manager

## 0. Test scene setup

This test scene is just for easy testing. If you already have your own, skip this section!

We will use Pixar's Kitchen set. It is made by the same company that created USD - Pixar.

(image: Pixar's Kitchen set)

- Download link: https://openusd.org/release/dl_downloads.html

To import this scene to Houdini Solaris:

### 0-1. Import to Houdini Solaris

Start by creating a LOP network node. Double click to enter LOP.

(screenshot 1)

Create an asset reference node, and set the file reference param to path to Kitchen_Set.usd.

- There are different ways to compose the file, depending on the workflow; importing as sublayer versus reference has a big difference, which this margin of this tutorial is too narrow to contain. We will keep it simply as a reference file.

(screenshot 2)

Import is success if you see the kitchen in the viewport. Make sure you are inside LOP!

## 1. Install the tool

Follow the installation guide: (todo: link)

From one of the panels, click on the + button to import: New Pane Type >> Misc >> Python Panel.

(screenshot 3)

Click on the dropdown and select **Variant Manager by havocado.**

(screenshot 4)

Success if you see the tool loaded.

(screenshot 5)


## 2. Choosing the LOP node path

The LOP node path is automatically set to the selected LOP node on opening the tool. However, in cases such as opening the scene after loading the tool, you may need to set the LOP path manually.

(screenshot of lop node path dropdown)

## 3. Scene graph

The scene graph shows only the prims with variants.

Clicking on the prim to see their existing variants.
