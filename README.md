# Blender-Motion-Export-Addon
Export addon for scientific use of Blender motion tracking data.
The digital 3D software suite Blender is published under GPL and provides a bunch of powerful tools for modelling, animation and movie editing (see https://www.blender.org/features/ for more information).
The motion tracking system of Blender is very sophisticated and still every version improvements for the algorithms are included.
To use the ready-to-run motion tracking system of Blender (e.g. for kinematics, motion studies or even dynamic shape analysis) this addon provides the simple functionality to export the acquired data in simple csv-files. These can easily be processed by most of the data tools in scientific context (R, SciPy etc.).
To start you just need to download Blender from https://www.blender.org/ and the addon script.

The current version of the addon includes:

- new Export Script Panel in the Tools section of the Movie Clip Editor
- all necessary functions in one toolbar (easy-to-use setup)
- selection of export path and optional log file
- export of selected or every marker

INSTALLATION

To install the addon open Blender and switch to the "Motion Tracking" perspective (select the drop-down menu "Default" at the top of the screen").
Next move your mouse cursor over the big central part of the screen and press Ctrl + UpArrow to maximize the "Movie Clip Editor".
By clicking on the small movie icon in the lower left corner you can open up the "Text Editor".
Open up the downloaded script by navigating to the file with the "Open Button". Run the Script with the appropriate button and switch back to the "Movie Clip Editor".
By pressing 't' on your keyboard (or clicking on the '+' sign at the left edge of the screen) you can show up the toolbar.
Here you will find the "Tracking and Export" section added.

USAGE

Open up your movie with the "Open" button. Press the "Add" button to add a marker at your mouse position (left mouse button).
By using right mouse button you can select other markers to change their name in the toolbar.
Using the "Tracking" section the automated or manual tracking is started and refined.
After finishing the motion tracking select the export path for the datafiles and adjust the start/stop frame to fit your movie length.
Hit one of the export buttons to create the csv files at the specified location.

CONTACT

Contact me via GitHub or talk to me in person if you meet me.
I would be glad about criticism, ideas, improvements - everything you got for me.

FUTURE

There is a bunch of things to do:
- Adding comments to the script (it was written overnight)
- Adding a tutorial video to explain all the possibilities of Blender motion tracking and usage of the script
- Adding merge functionality to allow export of multiple markers into one file
- Improvements of the inner layout and cleanup of the code
