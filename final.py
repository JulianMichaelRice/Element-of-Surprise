#---------------------------------------------------------------------------
"""
Julian Michael Rice

PyQt, PyAudio, OpenCV, Random, Numpy, Threading, and Classes

Project: Element of Surprise
Choose an attack type and try to take your opponent's HP to 0!
There are classes with different critical hit rates and different
rates in which their blocking moves succeed.
"""

#---------------------------------------------------------------------------
# MODULES 
#---------------------------------------------------------------------------
import sys, cv2, random, time, numpy, wave, pyaudio
from os import system, name
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from threading import Thread
from collections import deque

#---------------------------------------------------------------------------
# CONSTANTS 
#---------------------------------------------------------------------------

FIRE = 1 ;      WATER = 2 ;     GRASS = 3 ; #Moves (1/2)
HEAL = 4 ;      BLOCK = 5 ;     SWAP = 6  ; #Moves (2/2)
SWORDSMAN = 1 ; FORTRESS = 2 ;  ASSASSIN = 3 ;  MAGE = 4;           #Classes
HEALED = 0 ;    BLOCKED = 1 ;   NEGATED = 2 ;   FAIL_BLOCK = 3 ;    #Statuses
SWAPPED = 4;	SWAPPEDBY = 5;
MAXHEALTH = 100 ; #Stats (Add Stamina later?)
potentialTypes      = [ FIRE, WATER, GRASS ]
potentialOptions    = [ FIRE, WATER, GRASS, HEAL, BLOCK, SWAP ]
potentialClasses	= [ SWORDSMAN, FORTRESS, ASSASSIN, MAGE ]
dictionaryVal = dict([("1" , "FIRE"), ("2" , "WATER"), ("3" , "GRASS"), 
	("4" , "HEAL"), ("5" , "BLOCK"), ("6" , "SWAP")])

#---------------------------------------------------------------------------
# PERSON OBJECT 
#---------------------------------------------------------------------------
class Person():
	def __init__(self, name, mytype):
		"Initialize the person's private variables here"
		self.myName = name
		self.myHp = 100
		self.myID = random.randint(1, 1000)
		self.type = mytype
		self.currentMove = 0
		self.multiplier = 1
		self.critical = 1
		self.blockRate = 0
		self.criticalHit = False
		self.level = 1 #For another day

	def __str__(self):
		"Return player's name"
		return self.myName

	def setHp(self, hp):
		"Set the hp to the specified amount"
		self.myHp = hp

	def getHp(self):
		"Return player's HP"
		return self.myHp

	def setMove(self, move):
		"Set person's current move"
		self.currentMove = move

	def getMove(self):
		"Return the person's current move"
		return self.currentMove

	def getMoveString(self):
		"Return the person's current move as a string"
		return dictionaryVal[str(self.currentMove)]

	def getType(self):
		"Return the person's current type"
		return self.type;

	def setMultiplier(self, main, enemy):
		"Set the attack multiplier for the Person"
		self.multiplier = typeMultiplier(main, enemy)

	def isDead(self):
		"Returns true if the player is out of HP"
		if (self.myHp <= 0):
			self.myHp = 0
			return True
		else:
			return False

	def printOutput(self, damage, health, status, c):
		"Return output based on the moves made"
		if status[HEALED]:
			if self.myHp == MAXHEALTH:
				message = "Player " + self.myName + " fully healed!"
			else:
				message = "Player " + self.myName + " healed up and gained "\
				+ str(health) + " health!"
			message = "Player " + self.myName + " now has " + str(self.myHp) + " hp."

		elif status[BLOCKED]: 
			message = "Player " + self.myName + " blocked the attack!"

		elif status[NEGATED]: 
			message = "Player " + self.myName + "'s attack got negated!"

		elif status[FAIL_BLOCK]:
			message = "Player " + self.myName + " failed!"

		elif status[SWAPPED]:
			message = "Player " + self.myName + " swapped their element!"

		elif status[SWAPPEDBY]:
			message = "Player " + self.myName + " did not lose any health!"

		else:
			message = "Player " + self.myName + " got hit and lost "\
			+ str(damage) + " health!"
		if c:
			add = "CRITICAL! "
			message = add + message
		return message

	def typeEffect(self, enemyMove):
		"Player takes damage from the enemy"
		#Variable Initialization
		gainedHealth = 0 ; lostDamage = 0
		statuses = [ False, False, False, False, False, False ] 
		#[0] = HEAL, [1] = BLOCK, [2] = NEGATED [3] = FAILED 
		#[4] = SWAPPED, [5] SWAPPEDBY

		criticalHit = self.checkCritical()

		if (self.currentMove == HEAL):
			gainedHealth = random.randint(10, 30)
			statuses[HEALED] = True
			#Test if we are reaching past maximum HP
			if (self.myHp + gainedHealth <= MAXHEALTH):
				self.myHp += gainedHealth
			else:
				self.myHp = MAXHEALTH
			print("Worked!")

		elif (self.currentMove == BLOCK): #New condition
			result = random.randint(0, 100)
			if (result >= self.blockFail):
				lostDamage = 0
				statuses[BLOCKED] = True
			else:
				damageRate = typeMultiplier(enemyMove, self.type)
				lostDamage = int(damageRate * random.randint(10, 14))
				if criticalHit:
					lostDamage *= 2
				statuses[FAIL_BLOCK] = True
				self.myHp -= lostDamage

		elif (self.currentMove == SWAP):
			newElement = 0
			print("OLD ELEMENT: " + str(self.type))
			while newElement == self.type or newElement == 0:
				newElement = random.randint(1, 3)
			self.type = newElement
			print("NEW ELEMENT: " + str(self.type))
			statuses[SWAPPED] = True
			damageRate = typeMultiplier(enemyMove, self.type)
			lostDamage = int(damageRate * random.randint(10, 14))
			if criticalHit:
				lostDamage *= 2
			self.myHp -= lostDamage
			message = self.printOutput(lostDamage, 0, statuses, criticalHit)

		else: 
			damageRate = typeMultiplier(enemyMove, self.type)
			if enemyMove != BLOCK and enemyMove != SWAPPED:
				lostDamage = int(damageRate * random.randint(10, 14))
				if criticalHit:
					lostDamage *= 2
			elif enemyMove == BLOCK:
				result = random.randint(0, 100)
				if (result <= self.blockFail):
					lostDamage = 0
					statuses[FAIL_BLOCK] = True
					lostDamage = int(damageRate * random.randint(10, 14))
					if criticalHit:
						lostDamage *= 2
			elif enemyMove == SWAPPED: 
				statuses[SWAPPEDBY] = True
			self.myHp -= lostDamage

		message = self.printOutput(lostDamage, gainedHealth, statuses, criticalHit)
		return message

	def checkCritical(self):
		"Check if a critical hit was made. If so, return true"
		number = random.randint(1, 100)
		print("Critical Rate: " + str(self.critical))
		print("Number: " + str(number))
		if number <= self.critical:
			return True
		else:
			return False

#---------------------------------------------------------------------------
# SUBCLASSES OBJECT (Player Types)
#---------------------------------------------------------------------------
class Swordsman(Person):
	def __init__(self, name, myType):
		super(Swordsman, self).__init__(name, myType)
		self.critical = 5 #5 percent
		self.blockFail = 25
		self.className = "SWORDSMAN"

	def getClassName(self):
		return self.className

class Fortress(Person):
	def __init__(self, name, myType):
		super(Fortress, self).__init__(name, myType)
		self.critical = 2 #2 percent
		self.blockFail = 10
		self.className = "FORTRESS"

	def getClassName(self):
		return self.className

class Assassin(Person):
	def __init__(self, name, myType):
		super(Assassin, self).__init__(name, myType)
		self.critical = 15 #15 percent
		self.blockFail = 70
		self.className = "ASSASSIN"

	def getClassName(self):
		return self.className

class Mage(Person):
	def __init__(self, name, myType):
		super(Mage, self).__init__(name, myType)
		self.critical = 8 #8 percent
		self.blockFail = 40
		self.className = "MAGE"

	def getClassName(self):
		return self.className

#---------------------------------------------------------------------------
# GUI INTERFACE OBJECT
#---------------------------------------------------------------------------
class Game(QDialog):
	keyPressed = QtCore.pyqtSignal(int)

	def __init__(self, song):
		super(Game, self).__init__()
		loadUi('final.ui', self)
		self.song = song
		nameP1 = askName(1) 	; nameP2 = askName(2)
		typeP1 = askType() 		; clear()
		typeP2 = askType()		; clear()
		classP1 = askClass(1)	; clear()
		classP2 = askClass(2)	; clear()

		if classP1 == SWORDSMAN:
			self.player1 = Swordsman(nameP1, typeP1)
		elif classP1 == FORTRESS:
			self.player1 = Fortress(nameP1, typeP1)
		elif classP1 == ASSASSIN:
			self.player1 = Assassin(nameP1, typeP1)
		elif classP1 == MAGE:
			self.player1 = Mage(nameP1, typeP1)
		else:
			print("Unknown Error... quitting now")
			quit()

		if classP2 == SWORDSMAN:
			self.player2 = Swordsman(nameP2, typeP2)
		elif classP2 == FORTRESS:
			self.player2 = Fortress(nameP2, typeP2)
		elif classP2 == ASSASSIN:
			self.player2 = Assassin(nameP2, typeP2)
		elif classP2 == MAGE:
			self.player2 = Mage(nameP2, typeP2)
		else:
			print("Unknown Error... quitting now")
			quit()

		self.mode = True ; self.turns = 0
		self.image = None
		#self.loadButton.clicked.connect(self.loadClicked)
		self.initUI()


	def initUI(self):
		#Clicking an option sets the attack up, but does not initiate it
		self.buttonFire.clicked.connect(lambda: self.setAttack(FIRE, self.player1, self.player2, self.mode, self.buttonFire))
		self.buttonWater.clicked.connect(lambda: self.setAttack(WATER, self.player1, self.player2, self.mode, self.buttonWater))
		self.buttonGrass.clicked.connect(lambda: self.setAttack(GRASS, self.player1, self.player2, self.mode, self.buttonGrass))
		self.buttonHeal.clicked.connect(lambda: self.setAttack(HEAL, self.player1, self.player2, self.mode, self.buttonHeal))
		self.buttonBlock.clicked.connect(lambda: self.setAttack(BLOCK, self.player1, self.player2, self.mode, self.buttonBlock))
		self.buttonSwap.clicked.connect(lambda: self.setAttack(SWAP, self.player1, self.player2, self.mode, self.buttonSwap))

		#Customization: Fire Button
		self.buttonFire.setIcon(QtGui.QIcon('fire.png'))
		self.buttonFire.setIconSize(QtCore.QSize(64, 32))
		self.buttonFire.setStyleSheet('color: white; background-color: #C73333; border-radius: 20px;')
		
		#Customization: Water Button
		self.buttonWater.setIcon(QtGui.QIcon('water.png'))
		self.buttonWater.setIconSize(QtCore.QSize(64, 32))
		self.buttonWater.setStyleSheet('color: white; background-color: #66CCCC; border-radius: 20px;')
		
		#Customization: Grass Button
		self.buttonGrass.setIcon(QtGui.QIcon('grass.png'))
		self.buttonGrass.setIconSize(QtCore.QSize(64, 32))
		self.buttonGrass.setStyleSheet('color: white; background-color: #53A122; border-radius: 20px;')
		
		#Customization: Heal Button
		self.buttonHeal.setIcon(QtGui.QIcon('heal.png'))
		self.buttonHeal.setIconSize(QtCore.QSize(64, 32))
		self.buttonHeal.setStyleSheet('color: white; background-color: #F98B7F; border-radius: 20px;')

		#Customization: Block Button
		self.buttonBlock.setIcon(QtGui.QIcon('shield.png'))
		self.buttonBlock.setIconSize(QtCore.QSize(64, 32))
		self.buttonBlock.setStyleSheet('color: white; background-color: #3A2254; border-radius: 20px;')

		#Customization: Swap Button
		self.buttonSwap.setIcon(QtGui.QIcon('swap.png'))
		self.buttonSwap.setIconSize(QtCore.QSize(64, 32))
		self.buttonSwap.setStyleSheet('color: white; background-color: darkgreen; border-radius: 20px;')

		#Quit Button Connection
		self.keyPressed.connect(self.onKey)

		#Customization: Stat Description (Initial text)
		self.moveP.setStyleSheet('color: red; background-color: black; padding: 10px; border: 2px solid white; border-radius:10px')
		self.moveP.setText("Waiting for a move...")

		#Customization: Start Game (Player 1 starts!)
		self.startGame.clicked.connect(lambda: self.gameStart(self.player1, self.player2))
		self.startGame.setStyleSheet('color: white; background-color: #0080B8; border: 2px solid #0080B8; border-radius: 10px;')
		self.startGame.setText("Move! (P1)")
		
		#Customization: Quit game quits the game
		self.quitGame.setStyleSheet('color: white; background-color: #3C3C3C; border: 2px solid #3C3C3C; border-radius: 10px;')
		self.quitGame.clicked.connect(quit)

		#Customization: Play song again (restart the song, cause I do not know how to loop yet)
		self.playMusic.setStyleSheet('color: white; background-color: darkblue; border: 2px solid #3C3C3C; border-radius: 10px;')
		self.playMusic.clicked.connect(lambda: self.playSong(self.song))

		#Customization: Shoot an image of yourself that will act as a background photo! Cool?
		self.shoot.clicked.connect(self.profile)
		self.shoot.setStyleSheet('color: white; background-color: #808080; border: 2px solid #808080; border-radius: 10px;')

		#Health styles for the players (P1 and P2)
		healthStyleP1 = "background-color: #0080B8; color: white; padding: 5px; border: 2px solid white; border-radius: 10px;"
		healthStyleP2 = "background-color: #D61C1C; color: white; padding: 5px; border: 2px solid white; border-radius: 10px;"
		self.player1health.setText("P1 HP: 100 / 100")
		self.player1health.setStyleSheet(healthStyleP1)
		self.player2health.setText("P2 HP: 100 / 100")
		self.player2health.setStyleSheet(healthStyleP2)

		#Setting the turn style (P1 and P2)
		turnStyle = "background-color: white; color: red; border: 2px solid black; padding: 5px; border-radius: 10px;"
		self.playerTurn.setStyleSheet(turnStyle)

	def profile(self):
		"Takes a cropped photo of the player and sets them as the game background"
		cam = cv2.VideoCapture(0)
		ret, frame = cam.read()

		#Image name will be set to profile.jpg
		imgName = "profile.jpg"
		cv2.imwrite(imgName, frame)

		#This is the cropped version using a numpy array, I think
		final = cv2.imread("profile.jpg")
		final = final[50:650, 300:900]

		#Setting the background image to the background
		self.bg.setStyleSheet("background-image: url('profile.jpg'); background-position: center; background-attachment: fixed;")
		print("Photo done!")
		cam.release()

		#This is a good idea
		cv2.destroyAllWindows()

	def gameStart(self, player1, player2):
		#PLAYER 1 TURN
		if self.mode:
			#Button Styling
			self.playerTurn.setText("Player 1's Turn")
			self.startGame.setStyleSheet('color: white; background-color: #D61C1C; border: 2px solid #D61C1C; border-radius: 10px;')
			self.startGame.setText("Move! (P2)")
			self.playerStats.setText("Player 2: " + player2.getClassName() + "\nElement: " + dictionaryVal[str(player1.getType())])
			self.playerStats.setStyleSheet("background-color: black; color: red; border: 2px solid white; border-radius: 10px;")
			self.moveP.setText("  ")
			
			#Print text in status box
			self.statusOutput(player1, player2)

			#Get player 1's move and set it
			currentMoveP1 = player1.getMove()
			player1.setMove(currentMoveP1)

			#Change turn to player 2
			self.playerTurn.setText("Player 2's Turn")
			self.playerStats.setText("")
			time.sleep(1)
			self.playerStats.setText("Player 2: " + player2.getClassName() + "\nElement: " + dictionaryVal[str(player1.getType())])
			self.mode = False
		
		#PLAYER 2 TURN
		else:
			#Button Styling
			self.startGame.setStyleSheet('color: white; background-color: #0080B8; border: 2px solid #0080B8; border-radius: 10px;')
			self.startGame.setText("Move! (P1)")
			self.playerStats.setText("Player 1: " + player1.getClassName() + "\nElement: " + dictionaryVal[str(player2.getType())])
			self.playerTurn.setText("Player 2's Turn")
			self.moveP.setText("")

			#Print text in status box
			self.statusOutput(player1, player2)

			#Get player 2's move and set it
			currentMoveP2 = player2.getMove()
			player2.setMove(currentMoveP2)
		
			#Produce status box messages and calculate damage done
			stats = self.calculateDamage(player1, player2)
			self.moveP.setText(stats)

			#Reprint the health status again
			self.statusOutput(player1, player2)

			#Check for player deaths and end the game if so
			if player1.isDead():
				player1.setHp(0)
				self.player1health.setText("Player 1 HP: 0 / 100") #No need to use getHp
				self.chooseMove.setText("Player 2 Wins! Congrats! \n Close with Q")
			elif player2.isDead():
				player2.setHp(0)
				self.player2health.setText("Player 2 HP: 0 / 100") #No need to use getHp
				self.chooseMove.setText("Player 1 Wins! Congrats! \n Close with Q")

			#Switch turns back to player 1
			self.playerTurn.setText("Player 1's Turn")
			self.playerStats.setText("")
			time.sleep(1)
			self.playerStats.setText("Player 1: " + player1.getClassName() + "\nElement: " + dictionaryVal[str(player2.getType())])
			self.mode = True

	def statusOutput(self, player1, player2):
		"Dynamically output the current health of both players"
		currentHp = player1.getHp()
		currentHp2 = player2.getHp()
		self.player1health.setText("Player 1 HP: " + str(currentHp) + " / 100")
		self.player2health.setText("Player 2 HP: " + str(currentHp2) + " / 100")

	def quit():
		"Quit the game"
		quit()

	def setAttack(self, typed, p1, p2, mode, qbutton):
		"Set the attack for a player, but do not confirm it"
		#PLAYER 1
		if mode:
			p1.setMove(typed)
			self.selected(type, qbutton)
		
		#PLAYER 2
		else:
			#Set the move they they have chosen as their self.currentMove
			p2.setMove(typed)
			self.selected(type, qbutton) #This isn't working for some reason... maybe I should try hover
	
	def selected(self, type, button):
		"Change the button styling when clicked for a split second, then change it back"
		#Does not work for now... lol
		oldData = button.styleSheet()
		button.setStyleSheet('color: black; background-color: yellow; border: 2px solid yellow; border-radius: 10px;')
		button.setStyleSheet(oldData)
		print("Worked")

	def keyPressEvent(self, event):
		"Signals for a key press event"
		super(Game, self).keyPressEvent(event)
		self.keyPressed.emit(event.key())

	def onKey(self, key):
		"If Q is pressed, the game automatically ends."
		#Consider this the: I am losing and want to rage quit - button
		if key == QtCore.Qt.Key_Q:
			print("\nQuitting the game...\n")
			quit()
		else:
			print("Press Q to quit the game.")

	def calculateDamage(self, player1, player2):
		"Calculate the damage done to each player or the status"
		print("Ok P2: " + str(player2.getMove()) + "\n")
		print("Ok P1: " + str(player1.getMove()) + "\n")
		message1 = player1.typeEffect(player2.getMove())
		message2 = player2.typeEffect(player1.getMove())
		result = message1 + "\n" + message2 #This will get put in moveP (status text)
		return result

	def playSong(self, a):
		"Stop the song wherever it is and play it"
		a.stop()
		a.play('song')

#---------------------------------------------------------------------------
# AUDIO PROCESSING OBJECT 
#---------------------------------------------------------------------------
class process_audio(Thread):
    def __init__(self, name, length_in_samples = 180 * 60 * 44100):
        Thread.__init__(self)
        self.daemon = True
        self.n = name
        self.l = length_in_samples
        self.play = True
        self.wf = wave.open(name+'.wav','rb')  

        byte_depth_of_sample = self.wf.getsampwidth()
        sample_rate_per_chan = self.wf.getframerate()
        channels = self.wf.getnchannels()
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format = self.p.get_format_from_width(byte_depth_of_sample), 
                                  channels = channels, rate = sample_rate_per_chan, 
                                  output = True)
        
    def run(self):
        chunk_size = 1024
        data = self.wf.readframes(chunk_size)
        
        i = 0
        while self.play and (i < self.l / chunk_size) and len(data) > 0:
            self.stream.write(data)
            data = self.wf.readframes(chunk_size)
            i += 1
        
        self.play = False
        
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        
    def stop(self):
        self.play = False

class multiple_audio():
	def __init__(self):
		self.a = deque()

	def cleanup(self):
		while len(self.a) > 0 and not(self.a[0].play):
			self.a.popleft()

	def play(self, name, length_in_samples = 180 * 60 * 44100, printlen = False):
		self.cleanup()
		self.a.append( process_audio(name, length_in_samples) )
		self.a[-1].start()

		if printlen:
			print(str(len(self.a)) + " note(s) playing")

	def stop(self, printlen = False):
		self.cleanup()
		if len(self.a) > 0:
			self.a[0].stop()
			self.a.popleft()

		if printlen:
			print(str(len(self.a)) + " note(s) playing")

	def rewind_last(self, printlen = False):
		self.cleanup()    
		if len(self.a) > 0:
			n, l = self.a[-1].n, self.a[-1].l
			self.a[-1].stop()
			self.a.pop()
			self.a.append( process_audio(n,l) )
			self.a[-1].start()
		if printlen:
			print(str(len(self.a)) + " note(s) playing")

#---------------------------------------------------------------------------
# REGULAR FUNCTION DEFINITIONS 
#---------------------------------------------------------------------------

def typeMultiplier(attack, defense):
	"Find the type multiplier"
	if attack == FIRE and defense == GRASS:
		return 1.5
	if attack == FIRE and defense == FIRE:
		return 1
	if attack == FIRE and defense == WATER:
		return 0.5
	if attack == WATER and defense == GRASS:
		return 0.5
	if attack == WATER and defense == FIRE:
		return 1.5
	if attack == WATER and defense == WATER:
		return 1
	if attack == GRASS and defense == GRASS:
		return 1 
	if attack == GRASS and defense == FIRE:
		return 0.5
	if attack == GRASS and defense == WATER:
		return 1.5
	return 1
	#For the future, use lists and membership for many many types!

def askType():
	"Ask for the player's type"
	print("1 = FIRE | 2 = WATER | 3 = GRASS")
	while True:
		myType = int(input("Please enter your desired element: "))
		if myType in potentialTypes:
			break
		else:
			print("This is not an option. Choose 1-3 (Fire)")
		clear()
	return myType

def askClass(player):
	"Ask for the player's class"
	chosenClass = 0
	print("Choose your desired class, P" + str(player) + ": ")
	print(">> 1 = Swordsman \nCritical Rate : ••••------\nBlock Rate    : ••••••----")
	print(">> 2 = Fortress \nCritical Rate : ••--------\nBlock Rate    : •••••••••-")
	print(">> 3 = Assassin \nCritical Rate : ••••••••--\nBlock Rate    : •---------")
	print(">> 4 = Mage \nCritical Rate : ••••••----\nBlock Rate    : ••••------")
	while chosenClass not in potentialClasses:
		chosenClass = int(input("Enter your class (1/2/3/4): "))
	return chosenClass

def askName(num):
	"Ask for the player's name"
	name = input("Enter your username (P"+ str(num) +"): ")
	return name

def clear():
	"Clear the screen"
	if name == 'nt':
		_ = system('cls')
	else:
		_ = system('clear')

#---------------------------------------------------------------------------
# START PROGRAM 
#---------------------------------------------------------------------------
song = multiple_audio()
app = QApplication(sys.argv)
screenResolution = app.desktop().screenGeometry()
width, height = screenResolution.width() / 2, screenResolution.height() / 2
window = Game(song)
window.setWindowTitle("Element of Surprise: PIC 16 FINAL")
window.setGeometry(width - 250, height - 250, 500, 500) #change to screen's middle
song.play('song')
window.show()

sys.exit(app.exec_())

#---------------------------------------------------------------------------
