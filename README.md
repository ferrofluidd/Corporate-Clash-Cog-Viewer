# Clash-Cog-Viewer
Corporate Clash Cog Viewer / Cog Render Maker

# Info
Hi! This tool is mainly used for viewing Corporate Clash Cogs as well as making renders for them.

# Pre-requisites
* [Panda3D](https://www.panda3d.org/download/)
* [Python](https://www.python.org/downloads/)

# Changelogs (Last Updated: April 28, 2026)
* Added Auto-file mounting, to skip the extracting process entirely. (you will be prompted upon launch whether or not you'd like to load from the phase files directly or through the resources folder.)
* Added Environments Tabber (this tabber lets you load in a model that acts as the "environment". you can also load additional models to act as background props.)
* Added Battle Effects Tabber (contains Enraged, Soaked, Stunned, Sued, Zapped, Insured, Chilled and Frozen.)
* Added a Make Skelecog toggle (by that effect, removed standalone Skelecog actors from the list.)
* Added a Make GIF button (pressing this will screenshot all of the frames of the current Cog animation that is playing and compiles it all into a gif.)
* Take Screenshot now auto-trims the screenshot (you no longer need to use an external photo manipulation program to trim them or download external apps like ImageMagick.)
* Added an FOV Slider
* Added a Cog Rotation Slider
* Added a Random Cog button (this button will randomly pick a Cog, randomly pick an animation, a head animation (if applicable) and screenshots it.)
* Fixed Skelecogs and Zapped Skelecogs not moving when Make GIF is pressed.
* probably introduced a ton of bugs too
  
## How to Download Updates
* Simply download both the updated main.py and updated globals.py found in the src folder and replace the old main.py and old globals.py found in your Cog Viewer src folder.

## How to use (only do this if you chose the option to use the resources folder.)
<b>FIRST ADD CORPORATE CLASH'S FILES:</b>
* Paste all of your Corporate Clash .mf files in the resources folder.
* Run extract.bat in the resources folder. This will unpack all your multifiles into phase folders. You can remove the .mf files afterwards
* Do not delete the ICONS folder, ever.

<b>STARTING THE COG VIEWER:</b>
* Go to the scripts folder and double click on start.bat
* Alternatively, you can open main.py in the src folder and run it through a Python IDE.

## Sections:
Section             | Location | Definition
-------------   | ------------- | -------------
Cog | Top Left (First Tab) | Allows you to select a Cog actor, organized by Department.
Props | Top Left (Second Tab) | Allows you to apply props to the Cog actor.
Main | Bottom Left (First Tab) | Allows you to toggle miscellaneous attributes of the Cog Actor and camera.
Animation | Bottom Left (Second Tab) | Allows you to adjust the animation frames and playback.
Suit Library | Bottom Left (Third Tab) | Allows you to apply and adjust different suit textures/models/model parts.
Head HPR | Bottom Left (Fourth Tab) | Allows you to set the position and size of the Cog's head.
Set Scale | Bottom Left (Fifth Tab) | Allows you to set the scale and dimensions of the Cog actor/head.
Set Color | Bottom Left (Sixth Tab) | Allows you to apply colors to the Cog actor/background.

## Button Definitions:
### Cog List
Tab             | Action
-------------   | -------------
Department Tabber  | Where the Cogs are listed, simply click on the button to load them in.
Body Animations | Shows all the available body animations to the Cog body that can be applied.
Head Animations | Will only appear when the Cog loaded has an animated head, shows all available head animations.

### Props
Tab             | Action
-------------   | -------------
Prop 1 | Props for the Cog's right hand. Double click a prop to load it in, double click to remove it. Use the search bar if you're looking for a specific prop.
Prop 2 | Props for the Cog's left hand. Double click a prop to load it in, double click to remove it. Use the search bar if you're looking for a specific prop.

### Toggles (Main)
Button             | Action
-------------   | -------------
Autoplay Animations | Makes animations play automatically when selected
Toggle Shadow | Toggles the Cog's shadow.
Toggle Body | Toggles the Cog's body. Useful for Cog head renders.
Toggle Virtualize | Virtualizes the Cog, clicking the button multiple times will cycle through the different Virtualized colors, until getting turned off.
Cycle Health Meter | Cycles through the hp value meters of a Cog.
Reset Camera | Resets the camera to default values.
Reset Camera Roll | Reset's the camera's roll.
Upload Accessory | Prompts you to upload a bam file when pressed.
Upload Suit Texture | Prompts you to upload a png file. Applied to the Cog's suit model.
Upload Head Texture | Prompts you to upload a png file. Applied to the Cog's head model.
Take Screenshot | Takes a screenshot and saves it in the screenshots folder.
Render Frames | Renders all the frames in a Cog's body animation, each frame is saved in the screenshots folder.
Add Pie Splat | Adds a pie splatter to the Cog, selected randomly. Can be used up to 3 times on a single Cog.
Clear Pie Splats | Removes all the pie splatters from the Cog.
Toggle Costume (Managers Only) | Toggles a Manager's halloween costume (if they have one).

### Suit Toggles (Main)
Button             | Action
-------------   | -------------
Make Executive | Turns the Cog into an Executive.
Make Fired | Turns the Cog into a fired Cog.
Make Waiter (Bossbots Only) | Turns the Cog into a waiter.

### Animation
Button             | Action
-------------   | -------------
Body Animation Slider | Allows you to drag a slider to go through the frames of the selected body animation. Press play to loop said animation.
Head Animation Slider | Allows you to drag a slider to go through the frames of the selected body animation. Press play to loop said animation.

### Suit Library
Tab             | Action
-------------   | -------------
Standard (Texture) | Select a suit texture to apply to the Cog. Includes: Department/Executive/Waiter/Unemployed/Desk Jockey suit textures.
Manager (Texture) | Select a suit texture to apply to the Cog. Includes: All Manager/Contractor-unique suit textures.
Halloween (Texture) | Select a suit texture to apply to the Cog. Includes: All Manager Halloween-costume suit textures.
Skelecog (Texture) | Select a Skelecog texture to apply to the Cog. Includes: All Skelecog body textures. Using this on a generic Skelecog model will also alter their head texture.
Suit Models | Select a suit model to apply to the Cog. Organized by Suit A (buff) > Suit B (thin) > Suit C (fat) > Skelecog
Emblems | Select a department emblem to apply to the Cog. Also includes health light and no emblem.
Neckties | Select a necktie model to apply to the Cog. Suit models that conflict with neckties have this feature disabled.

### Head HPR
Button             | Action
-------------   | -------------
Left/Right | Control's the Cog head's position on the X-axis. 
Front/Back | Control's the Cog head's position on the Y-axis. 
Up/Down | Control's the Cog head's position on the Z-axis. 
Heading | Control's the Cog head's vertical rotation.
Pitch | Control's the Cog head's horizontal rotation.
Roll | Control's the Cog head's rotation.
Scale | Control's the Cog head's size.
Reset All | Reset's all sliders to default values.

### Set Scale
Button             | Action
-------------   | -------------
Profile (Sx) | Control's the scale of the Cog/head on the X-axis.
Portrait (Sy) | Control's the scale of the Cog/head on the Y-axis.
Height (Sz) | Control's the scale of the Cog/head on the Z-axis.
Reset All | Reset's all sliders to default values.

### Set Color
Button             | Action
-------------   | -------------
Hex (#RRGGBB): | Allows you to select the color to be used (via hex code or color picker).
Set Cog ColorScale | Sets the color scale of the entire Cog.
Set Head Color | Applies the color to the Cog's head.
Set Hand Color | Changes the color of the Cog's hands. Does not work with Skelecog/Cog Boss bodies.
Reset Cog Colors | Removes all Color changes applied to the Cog.
Set Background Color | Changes the color of the background.
Reset Background Color | Resets the color of the background to default.

### Prop 1 HPR / Prop 2 HPR
Button             | Action
-------------   | -------------
Left/Right | Control's the left/right prop's position on the X-axis. 
Front/Back | Control's the left/right prop's position on the X-axis. 
Up/Down | Control's the left/right prop's position on the Z-axis.
Heading | Control's the left/right prop's vertical rotation.
Pitch | Control's the left/right prop's horizontal rotation.
Roll | Control's the left/right prop's rotation.
Scale | Control's the size of the left/right prop.
Reset All | Reset's all sliders to default values.

### Accessory HPR (Only visible when an accessory is loaded)
Button             | Action
-------------   | -------------
Left/Right | Control's the accessory's position on the X-axis. 
Front/Back | Control's the accessory's position on the X-axis. 
Up/Down | Control's the accessory's position on the Z-axis.
Heading | Control's the accessory's vertical rotation.
Pitch | Control's the accessory's horizontal rotation.
Roll | Control's the accessory's rotation.
Scale | Control's the size of the accessory.
Reset All | Reset's all sliders to default values.

### Camera Controls
Key             | Action
-------------   | -------------
Control+Z	    | Optional keybind to reset the camera.

### Limitations
* You can only have one accessory (via Upload Accessory) and up to two props loaded at once.
* Props are reparented to the Cog's left/right hand only.
* Many toggle features do not work on Boss Cog bodies.
* Pie Splatters will get cleared when choosing a new suit model from Suit Library.

### Known Bugs
* Toggle virtualize can cause transparency issues. Examples include VP/Multislacker's lightbulb, Cog Boss HP lights, CLO's body shadow, and CEO's eyes.
* When switching from a Manager with unique toggles (e.g. toggle costume, suit toggles) to a Boss Cog, these unique toggle options will persist.

# Acknowledgements
* [BoggTech's](https://github.com/BoggTech/) [VisorView](https://github.com/BoggTech/VisorView/tree/main) was used as a base and main inspiration for this program. Our utmost gratitude goes towards them.
* Special thanks to Panda3D and Python and their contributors. 
* Toontown Online and Toontown Corporate Clash assets all belong to their respective owners. Thank you to all of the talented artists and talented animators for their breathtaking contributions. Thank you for keeping Toontown's legacy alive!

ferrofluid - hi
diggins
