# houdiniCompare
A simple python script to compare between two Houdini Scenes

Delighted to share a personal project I've been diligently crafting during my spare moments.

This Python script serves as a handy tool for identifying alterations within your scenes by performing a detailed comparison between two files.

----------------------------------------------------

INSTALLATION:

Option 1:

Download the main.py file and store it in a folder of your choosing (I recommend your Houdini user preference folder).

Create a shelf button and paste the provided code under ShelfPython.py file under the script tab of your new shelf tool (ensure the script language is set to Python).

Save it


Option 2:

Copy the code in main.py

Create a shelf button and paste the copied code under the script tab (ensure the script language is set to Python).

Save it

-----------------------------------------------------------

HOW TO USE:

Click the shelf button.

For your initial comparison, click "CREATE SOURCE."

This will execute the following steps:

A) Save your current scene (be sure to increment the version to avoid overwriting).

B) Open the target hip file for comparison and generate a corresponding .JSON file in the same directory.

C) Load your original working scene and initiate the comparison process.

Subsequent comparisons will only require you to SELECT "source" after clicking the shelf button.

The script accomplishes two primary tasks:

Identifying changes: It highlights nodes where parameters have been altered, providing details such as the modified parameter, its original value, and the current value.

Detecting new nodes: Any nodes present in the target scene but absent in the reference scene are flagged.

CAVEATS:

Deleted nodes: The script won't flag nodes that have been removed from the scene.
Ramp parameters: Currently, ramp parameters are not taken into account during the comparison process.
