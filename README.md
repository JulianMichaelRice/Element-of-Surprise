# Element of Surprise
Turn-based 2 Player Text + GUI RPG
[ Julian Rice 2018 | December 2018 ]

### Summary
Element of Surprise is a game where two players try to reveal each other's type and take advantage of that information to try to take their opponent's HP down to 0. Outside of types, there are unique critical and block failure rates for FOUR different classes in the game, along with options to heal, block, and swap one's type. Each player starts with 100 HP and has an elemental type and physical class that they have chosen.

### Features
* __Elemental Types__ -> There are three types: Fire, Water, and Grass. These types interact in a triangular sense, where fire is effective against grass, water is effective against fire, and grass is effective against water. Each player chooses their elemental type at the start of the game, and can switch their type to some other random type (that will definitely be different) by using the SWAP command.
* __Physical Types__ -> There are four classes: Swordsman, Fortress, Assassin, and Mage. Swordsman and Mage classes are more balanced with decent critical rates and a low blocking fail rate. On the other side, Fortress is an amazing class for ensuring that most all blocks will work, with sacrificing the chance at getting a critical hit. Assassin is just the opposite of Fortress in this case.
* __Cheese!__ -> If you click the Shoot! button on the GUI, my work on the OpenCV will be initiated. The webcam on your computer (assuming you have one) will be turned on for a split second, take a photo of you, crop the image using Numpy, then set the image as the background of the game. Pretty cool stuff right? Give it a go!
* __6 Moves__ -> The six options that can be made by the player are [1] Fire [2] Water [3] Grass [4] Heal [5] Block [6] Swap. The first three moves are used to test out and see what element the opponent is, and take advantage of the information you gain from choosing one of those moves. If you feel that your opponent knows your type and you do not know theirs, then it might be a wise decision to randomly switch your elemental type with Swap sometime. You still take damage from the enemy attack when using Swap, so be careful of that. Healing is self explanatory - it heals between 10 and 30 HP each time, which is kind of broken; I will likely add a feature where healing can fail (or take up stamina) and have that be another defining feature for each of the classes. Finally, you can block any attack with [5], but there is a likelihood that the block will fail. This completely depends on a random number generator and your class' block failure percentage. 
* __Replay Music__ -> The button on the top left of the GUI allows for the music that I composed for this project to be replayed. I still do not know the complete mechanics to looping music, but that is something I can work on adding in a future update.
* __Statuses__ -> To differentiate what text gets displayed on the status box after player 2 makes their moves, I used a boolean list of different statuses that would get activated depending on the moves that each player makes.
---
### Contents
##### final.py
This is the main file - it contains all of the class definitions for PyAudio / multithreading, derived physical classes, the general Person class, and the PyQt5 GUI class / object. It's nearly 700 lines long and contains a good amount of comments explaining what is going on! Read them!

##### final.ui
This is the UI file made using Qt Designer. It contains location details for all of the buttons and some (but not all) stylesheets for some of the buttons. This is also where some of the button names are defined.

##### fire, water, grass, heal, block, shield.png
These are the image files for each button. Think of them as icons, as their sizes have been adjusted accordingly (to 64px if I recall correctly).

##### profile.jpg
This is simply a background photo I took using the Shoot! button functionality at the airport. The photo is kind of blue for some reason, but that might be a problem with my kind of broken webcam.

##### song.wav.zip
This is a zipped file of the song for the game, which apparently cannot be uploaded to Github as a binary wav file due to its size being over 25 MB. I made the track using MuseScore 2 and decided not to master it using Garageband, which is why it might sound like a midi track.

##### DesignDocument.pdf
This is the design document I wrote for submission to a professor who I respect to a great degree. Feel free to read it for more details about final.py, as there are a couple of cool, interesting things that I wrote on there but omitted here.
#
---
