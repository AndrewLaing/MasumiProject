# Author:       Andrew Laing
# Email:        parisianconnections@gmail.com
# Last Updated: 17/02/2019
# Decription:   Main file for the Masumi ADHD Chatbot application.
# Changes:      Refactored and commented.

import pygame
from pygame.locals import *
import pyaiml
import subprocess
import time
import os
import re
import scripts.vars as sv
from scripts.TextRender import *
from scripts.ButtonClass import *
from comtypes.client import CreateObject
from comtypes.gen import SpeechLib
from datetime import datetime

# Set logConversation to 0 if you do not want to write conversations to file
logConversation = 1

if logConversation:
    # Get the path to the log file folder
    newpath = os.path.expanduser("~\Documents")
    newpath = newpath + "\MasumiChatLogs"

    # Create a folder for the log files in the Documents folder
    #  if it does not already exist
    if not os.path.exists(newpath):
        os.makedirs(newpath)

    # Create the path to the logfile
    now = datetime.now()
    logfilename = newpath + now.strftime("\logfile_%d%m%Y_%H%M.txt")
    print(logfilename)

SCREENSIZE = (1000, 600)

WHITE = (245, 245, 245)
RED = (255, 155, 155)
LIGHTRED = (255, 215, 225)
BLACK = (0, 0, 0)

TEXTPOS = (260, 570)


################################################################################
### AIML Related functions #####################################################

class MasumiBrain:
    """ Used to handle the application's use of the PyAIML library.

    Attributes:
        k: A PyAIML kernel.
        voice: A Microsoft SAPI voice.
    """

    def __init__(self):
        """ Initialises MasumiBrain. """
        self.loadBrain()

    def createNewBrain(self):
        """ Loads an AIML knowledge tree into the PyAIML kernel
            and saves it to a brain file (.brn) for faster loading
            the next time that the application is opened.
        """
        self.k = pyaiml.Kernel()
        self.k.bootstrap(learnFiles="alice-startup.xml")
        self.k.respond("load aiml b")

        # Set the predicates for the session
        self.k.setPredicate('name', 'Human')
        for a, b in sv.preds:
            self.k.setBotPredicate(a, b)

        self.k.saveBrain("scripts\\masumibrain.brn")


    def loadBrain(self):
        """ If a brain file (.brn) exists loads it into the PyAIML kernel,
            otherwise loads an AIML knowledge tree into the PyAIML kernel
            and saves it to a brain file (.brn) for faster loading
            the next time that the application is opened.
        """
        ''' Load or create the Bots brain. '''
        # Check first if the brain file exists
        (exitstatus, outtext) = subprocess.getstatusoutput('dir scripts\\masumibrain.brn')
        if exitstatus == 0:
            # Load the knowledge tree into the PyAIML Kernel
            self.k = pyaiml.Kernel()
            self.k.bootstrap(brainFile="scripts\\masumibrain.brn")
            # Set the predicates for the session
            self.k.setPredicate('name', 'Human')
            for a, b in sv.preds:
                self.k.setBotPredicate(a, b)
        else:
            self.createNewBrain()


    def saveBrain(self):
        """ Writes out the knowledge tree stored in the PyAIML kernel
            to a brain file (.brn).
        """
        self.k.saveBrain("scripts\\masumibrain.brn")


    def getBotResponse(self, inputText):
        """ Sends a text string to the PyAIML kernel for a response
            from the stored knowledge tree.

        :param inputText: A text string.
        :return: A tidied response to the text string.
        """
        ''' Get response and tidy it up. '''
        # Log the user's text
        if logConversation:
            with open(logfilename, "a") as myfile:
                myfile.write("\nUser: ")
                myfile.write(inputText)

        a = self.k.respond(inputText)

        # Tidy up the bot's response
        tidiedResponse = " ".join(a.split())
        tidiedResponse = re.sub(r'\s([?.!"](?:\s|$))', r'\1', tidiedResponse)
        tidiedResponse = tidiedResponse.capitalize()

        # Log the bot's response
        if logConversation:
            with open(logfilename, "a") as myfile:
                myfile.write("\nBot:  ")
                myfile.write(tidiedResponse)

        # If there was no response, change the subject :D
        if tidiedResponse=="":
            tidiedResponse="Lets talk about something else, please."

        return tidiedResponse


################################################################################
### TTS Related Functions ######################################################

class MasumiVoice:
    """ Used to handle the application's Text-to-Speech functionality.

    Attributes:
        engine: A SAPI SpVoice Interface object.
        voice: A Microsoft SAPI voice.
    """

    def __init__(self, voice):
        """ Initialises MasumiVoice with a Microsoft SAPI voice.

        :param voice: A Microsoft SAPI voice description.
        """
        self.voice = voice
        self.engine = CreateObject("SAPI.SpVoice")

    def convertTextToSpeech(self, textToSpeak):
        """ Creates a temporary Text-to-Speech WAV of a text, plays it
            then deletes it

            :param textToSpeak: A line of text to convert to speech.
        """
        if self.voice:
            self.createWAV(textToSpeak)
            try:
                soundObj = pygame.mixer.Sound('temp.wav')
                soundObj.play()  # Continues code during sound playing
                subprocess.getoutput('del temp.wav')
            except:  # If there is an error create an audio error message
                self.createWAV("Program Error")
                soundObj = pygame.mixer.Sound('temp.wav')
                soundObj.play()
                subprocess.getoutput('del temp.wav')


    def createWAV(self, textToSpeak):
        """ Creates a Text-to-Speech WAV from a text string.

        :param textToSpeak: A line of text to convert to speech.
        """

        # If there is no response (for example, because of recursion depth exceeded error)
        if len(textToSpeak) <= 1:
            textToSpeak = "Lets talk about something else, please."

        # Windows pronounces bot's name as Mahjewmi
        textToSpeak = textToSpeak.replace("masumi", "Massoomi")

        # Write text out to speech wav
        stream = CreateObject("SAPI.SpFileStream")
        outfile = "temp.wav"
        stream.Open(outfile, SpeechLib.SSFMCreateForWrite)
        self.engine.AudioOutputStream = stream

        # Add voice tags to select the TTS voice
        textToSpeak = sv.voiceTags + textToSpeak
        self.engine.speak(textToSpeak)
        stream.Close()


################################################################################
### Interface Related ##########################################################

class MasumiInterface:
    """ Used to display the application GUI, handle user input,
        handle events, and write texts to a log file.

    Attributes:
        blinkActive: True if the blink animation is active, otherwise False.
        blinkImages: A list of the blink/default animation images
        blinkIndex : Index of the blink/default animation image being displayed.
        blinkRate: How often the blink animation should be displayed (e.g., every 3 seconds)
        Brain: An instance of the MasumiBrain class
        btn_1: A user feedback button.
        btn_2: A user feedback button.
        btn_3: A user feedback button.
        btn_4: A user feedback button.
        btn_5: A user feedback button.
        btn_6: A user feedback button.
        btn_exit: A button used to close the application.
        clock: Timer used for the PyGame game loop.
        currentMannerism: The mannerism currently being animated.
                          (0 – default/blink, 1 – head nod/move, 2 – mannerism2)
        currentTime: The current time.
        is_speaking: True if TTS is playing, otherwise False.
        lenPromptText: The length of the input prompt text.
        logoFont: Font used to display the application log.
        logoSurface: PyGame surface used to hold the logo text.
        mannerism2Active: True if the mannerism2 animation is active, otherwise False.
        mannerism2ImageList: A list of the mannerism2 animation images.
        mannerism2Index: The index of the mannerism2 image being displayed.
        miniResponseFont: Font used for response when it is too long to fit on the screen.
        mouthIndex: The index of the mouth image being displayed.
        mouthImages: A list of mouth images used for the speaking animation.
        mouthMoveImageList: A list of mouth images for the current reply being spoken with TTS.
        nodActive: True if the head nod/move animation is active, otherwise False.
        nodImageList: A list of the images used for the head nod/move animation.
        nodIndex: The index of the head nod/move image being displayed.
        nodStart: A time used to regulate the head nod/move animation's frequency.
        promptText: A string used as a prompt in the user input box.
        responseFont: Font used for the bot's response text.
        screen: A PyGame screen object.
        startTime: A time used to regulate mannerism selection.
        textForResponseBox: A string to display in the response box.
        userInputFont: The font used to display the user's input text.
        userText: A string input by the user.
        Voice: A MasumiVoice instance.
    """

    def __init__(self):
        """ Initialises MasumiInterface. """
        self.initialiseBrain()
        self.initialiseVoice()
        self.initialiseVariables()
        self.initialiseInterface()

        if logConversation:
            self.createLogfile()


    def initialiseBrain(self):
        """ Initialises an instance of MasumiBrain. """
        self.Brain = MasumiBrain()


    def initialiseImageLists(self):
        """ Loads the images used to display the chatbot's avatar animations. """
        self.loadBaseMasumiImages()
        self.loadHeadMovementImages()
        self.loadMouthShapeImages()
        self.loadMannerism2Images()
        self.mouthMoveImageList = None  # Holds images to animate Masumi's mouth when she speaks


    def initialiseInterface(self):
        """ Initialises the user interface. """
        pygame.init()
        self.createFonts()
        self.initialiseScreen()
        self.createButtons()
        self.initialiseImageLists()


    def initialiseScreen(self):
        """ Initialises the GUI screen. """
        self.screen = pygame.display.set_mode(SCREENSIZE)
        pygame.display.set_caption('Masumi')
        self.screen.fill(BLACK)

        # Change the pygame icon
        iconImage = pygame.image.load('img/mini_masumi.ico')
        pygame.display.set_icon(iconImage)

        # Add the Logo
        self.logoSurface = self.logoFont.render('Masumi', True, RED)


    def initialiseVariables(self):
        """ Initialises MasumiInterface variables. """
        self.clock = None
        self.startTime = None
        self.nodStart = None
        self.currentTime = None

        self.textForResponseBox = ''    # Text for the bot response Box
        self.blinkIndex = 0             # Index of the current Masumi base image being displayed
        self.mouthIndex = 0             # Index of the current mouth shape image being displayed
        self.nodIndex = 0               # Index of the current Masumi head move image being displayed
        self.mannerism2Index = 0        # Index of the current Mannerism 2 image being displayed

        self.is_speaking = False            # 1 if the bot is speaking, otherwise 0

        # Masumi blink routine
        self.blinkRate = 3  # blink every three seconds

        # Used to denote whether animations are active or not (1 or 0)
        self.blinkActive = False
        self.nodActive = False
        self.mannerism2Active = False

        # Set the current mannerism being used to default blink
        self.currentMannerism = 0

        # Text Input Box.
        self.promptText = "Type :"
        self.lenPromptText = len(self.promptText)
        self.userText = self.promptText


    def initialiseVoice(self):
        """ Initialises an instance of MasumiVoice. """
        try:
            self.Voice = MasumiVoice(1)
            self.Voice.engine.speak(sv.nonBotVoiceTags + "Welcome to the Massoomi ADHD chat bot application.")
        except:
            self.Voice = MasumiVoice(0)


    def startTimers(self):
        """ Initialises timers for the PyGame game loop. """
        self.clock = pygame.time.Clock()
        self.startTime = time.time()
        self.nodStart = time.time()


    def createButtons(self):
        """ Creates the user feedback buttons. """
        self.btn_1 = Button("Changed the Subject",
                            (760, 30, 220, 60), (780, 52),
                            'fonts/notepad.ttf', 18)
        self.btn_2 = Button("Did not understand",
                            (760, 110, 220, 60), (785, 132),
                            'fonts/notepad.ttf', 18)
        self.btn_3 = Button("Nonsense Answer",
                            (760, 190, 220, 60), (797, 212),
                            'fonts/notepad.ttf', 18)
        self.btn_4 = Button("Forgot what I said",
                            (760, 270, 220, 60), (795, 292),
                            'fonts/notepad.ttf', 18)
        self.btn_5 = Button("Repeated Answer",
                            (760, 350, 220, 60), (800, 372),
                            'fonts/notepad.ttf', 18)
        self.btn_6 = Button("Program Error",
                            (760, 430, 220, 60), (815, 452),
                            'fonts/notepad.ttf', 18)
        self.btn_exit = Button("EXIT",
                               (760, 510, 220, 60), (835, 525),
                               'fonts/notepad.ttf', 32)


    def createFonts(self):
        """ Creates the fonts used to display text on-screen. """
        self.miniResponseFont = pygame.font.Font('fonts/notepad.ttf', 13)
        self.userInputFont = pygame.font.Font('fonts/notepad.ttf', 18)
        self.responseFont = pygame.font.Font('fonts/notepad.ttf', 22)
        self.logoFont = pygame.font.Font('fonts/Beyond_Wonderland.ttf', 150)


    def createMouthMoveImageList(self, text):
        """ Populates the list used for animating the bot's response texts.

        :param text: A text string.
        """
        moveList = []

        if len(text) == 0:
            self.mouthMoveImageList = [7, 7, 7]
            return

        text = text.lower()
        for letter in text:
            if letter in sv.mshape:
                moveList.append(sv.mshape[letter])
                moveList.append(sv.mshape[letter])
            else:
                if len(moveList) > 0:
                    moveList.append(moveList[-1])  # hold the previous mouth shape
                else:
                    moveList = [7]

        self.mouthMoveImageList = moveList


    def loadBaseMasumiImages(self):
        """ Loads the blink/default images for the chatbot's avatar animation. """
        self.blinkImages = []
        for img in range(17):
            filename = "img\\blink\\neko%s.png" % str(img + 1)
            self.blinkImages.append(pygame.image.load(filename).convert())


    def loadHeadMovementImages(self):
        """ Loads the images to animate the chatbot's head nod/move animation. """
        n_1 = pygame.image.load('img/shake/neko0.png').convert_alpha()
        n_2 = pygame.image.load('img/shake/neko2.png').convert_alpha()
        self.nodImageList = [n_1, n_1, n_1, n_1, n_1, n_1, n_1, n_1, n_1,
                             self.blinkImages[0], self.blinkImages[0], self.blinkImages[0],
                             self.blinkImages[0], self.blinkImages[0],
                             n_2, n_2, n_2, n_2, n_2, n_2, n_2, n_2, n_2,
                             self.blinkImages[0], self.blinkImages[0], self.blinkImages[0],
                             self.blinkImages[0], self.blinkImages[0]]


    def loadMannerism2Images(self):
        """  Loads the images for the Mannerism2 animation (a mouth movement resembling
             a goldfish which is activated after a long period of user inactivity).
        """
        m2_1 = self.mouthImages[5]
        m2_2 = self.mouthImages[6]
        self.mannerism2ImageList = [m2_1, m2_1, m2_1, m2_1, m2_2, m2_2,
                                    m2_2, m2_2, m2_1, m2_1, m2_1, m2_1, 0, 0, 0, 0, 0, 0,
                                    m2_1, m2_1, m2_1, m2_1, m2_2, m2_2,
                                    m2_2, m2_2, m2_1, m2_1, m2_1, m2_1, 0, 0, 0, 0, 0, 0]


    def loadMouthShapeImages(self):
        """ Loads the images used for the chatbot's speech animation. """
        mouthshapes = ['img\\talk\\FV.png', 'img\\talk\\TS.png', 'img\\talk\\E.png',
                       'img\\talk\\LN.png', 'img\\talk\\A.png', 'img\\talk\\UQ.png',
                       'img\\talk\\O.png', 'img\\talk\\WR.png', 'img\\talk\\MBP.png']
        self.mouthImages = []

        for img in mouthshapes:
            self.mouthImages.append(pygame.image.load(img).convert_alpha())  # sprite in png format


    def checkForButtonPress(self, event):
        """ Checks for a feedback button or exit button press.
            Writes feedback button text to the log file.

        :param event: A PyGame event.
        :return: True if the exit button was pressed, otherwise False.
        """
        if self.btn_1.button_was_pressed(event):
            self.writeButtonPressToLogFile(self.btn_1.caption)
        elif self.btn_2.button_was_pressed(event):
            self.writeButtonPressToLogFile(self.btn_2.caption)
        elif self.btn_3.button_was_pressed(event):
            self.writeButtonPressToLogFile(self.btn_3.caption)
        elif self.btn_4.button_was_pressed(event):
            self.writeButtonPressToLogFile(self.btn_4.caption)
        elif self.btn_5.button_was_pressed(event):
            self.writeButtonPressToLogFile(self.btn_5.caption)
        elif self.btn_6.button_was_pressed(event):
            self.writeButtonPressToLogFile(self.btn_6.caption)
        elif self.btn_exit.button_was_pressed(event):
            self.closeApplicationCleanly()
            return True
        return False


    def keyPressCallback(self, event):
        """ Checks for a key press event and deals with it appropriately.

        :param event: A PyGame event.
        """
        if event.key == K_RETURN:
            userSays = (self.userText[self.lenPromptText:]).lower()
            self.userText = self.promptText  # clear user input text

            if userSays == "save brain":
                self.Brain.saveBrain()
                self.textForResponseBox = "My brain has been saved."
            elif userSays == "exit program":
                self.closeApplicationCleanly()
                return
            else:
                self.textForResponseBox = self.Brain.getBotResponse(userSays)
                self.userText = self.promptText  # clear user input text

            self.Voice.convertTextToSpeech(self.textForResponseBox)

            # If there is no response (for example, because of recursion depth exceeded error)
            if len(self.textForResponseBox) <= 1:
                if logConversation:
                    with open(logfilename, "a") as myfile:
                        myfile.write("\nBot:  <<< OUTPUT ERROR!!! >>>")

        elif event.key == K_BACKSPACE:
            if len(self.userText) > self.lenPromptText:
                self.userText = self.userText[:-1]

        elif event.key == K_ESCAPE:
            self.closeApplicationCleanly()
            return

        else:
            carac = event.dict['unicode']
            if carac in sv.allowed:
                self.userText = self.userText + carac


    def setCurrentMannerism(self):
        """ Used to detect the current animation mannerism to display. """
        nodTime = self.currentTime - self.nodStart
        if (nodTime > 6 and nodTime < 10) or (nodTime > 16 and nodTime < 20) or (nodTime > 26 and nodTime < 40):
            self.currentMannerism = 1
        elif nodTime > 40 and nodTime < 46:
            self.nodActive = False
            self.currentMannerism = 2
            self.mannerism2Active = True
        elif nodTime > 46:
            self.mannerism2Active = False
            self.currentMannerism = 0
            self.nodStart = self.currentTime
        elif nodTime > 10:
            self.currentMannerism = 0
            self.nodActive = False


    def renderBlinkAnimation(self):
        """ Determines which blink/default animation image to display
            and blits it to the PyGame surface.
        """

        # Set blink to active if appropriate
        if self.currentTime - self.startTime > self.blinkRate:
            self.blinkActive = True

        # Set the appropriate blink image
        if self.blinkActive:
            self.blinkIndex += 1
            if self.blinkIndex > 16:
                self.blinkIndex = 0
                self.blinkActive = False
                self.startTime = self.currentTime

        # Only blink if head is not moving
        if not self.nodActive:
            Masumi_IMG = self.blinkImages[self.blinkIndex]
            self.screen.blit(Masumi_IMG, (0, 160))


    def renderBotResponseText(self):
        """ Renders the chatbot's response text on-screen. """
        my_rect = pygame.Rect((280, 200, 480, 360))
        try:
            rendered_text = TextRender.render_textrect(self.textForResponseBox, self.responseFont,
                                            my_rect, WHITE, BLACK, 0)
            if rendered_text:
                self.screen.blit(rendered_text, my_rect.topleft)
        except:
            rendered_text = TextRender.render_textrect(self.textForResponseBox, self.miniResponseFont,
                                            my_rect, WHITE, BLACK, 0)
            if rendered_text:
                self.screen.blit(rendered_text, my_rect.topleft)


    def renderButtons(self):
        """ Renders the user feedback buttons on-screen. """

        # Add buttons to the screen
        self.btn_1.render(self.screen)
        self.btn_2.render(self.screen)
        self.btn_3.render(self.screen)
        self.btn_4.render(self.screen)
        self.btn_5.render(self.screen)
        self.btn_6.render(self.screen)
        self.btn_exit.render(self.screen)


    def renderHeadMoveAnimation(self):
        """ Determines which head nod/move animation image to display
            and blits it to the PyGame surface.
        """
        if not self.is_speaking and not self.blinkActive and self.currentMannerism == 1:
            self.nodIndex += 1
            if self.nodIndex > 27:
                self.nodIndex = 0
                self.nodActive = True
            self.screen.blit(self.nodImageList[self.nodIndex], (0, 160))
        else:
            self.nodActive = False
            self.nodIndex = 0


    def renderLogo(self):
        """ Renders the logo text on-screen. """
        self.screen.blit(self.logoSurface, (190, 10))


    def renderMannerism2Animation(self):
        """ Determines which mannerism2 animation image to display
            and blits it to the PyGame surface.
        """
        if self.mannerism2Active and not self.is_speaking:
            m2IMG = self.mannerism2ImageList[self.mannerism2Index]
            if m2IMG != 0:
                self.screen.blit(m2IMG, (0, 160))

            self.mannerism2Index += 1

            if self.mannerism2Index > 35:
                self.mannerism2Index = 0


    def renderMouthShape(self):
        """ Determines which speaking animation image to display
            and blits it to the PyGame surface.
        """
        if self.is_speaking:
            # Do not move head or use mannerism 2 whilst speaking
            self.currentMannerism = 0
            self.mannerism2Active = False
            self.mannerism2Index = 0

            self.nodStart = self.currentTime
            if self.mouthMoveImageList == None:
                self.createMouthMoveImageList(self.textForResponseBox)
            if len(self.mouthMoveImageList) > 0:
                self.mouthIndex = self.mouthMoveImageList.pop(0)
            mouthImg = self.mouthImages[self.mouthIndex]
            self.screen.blit(mouthImg, (0, 160))
        else:
            self.mouthMoveImageList = None


    def renderTextInputBox(self):
        """ Renders the text input box on-screen """
        text = self.userInputFont.render(self.userText, True, LIGHTRED)
        self.screen.blit(text, TEXTPOS)


    def createLogfile(self):
        """ Create a logfile for the session. """
        with open(logfilename, "a") as myfile:
            myfile.write("\n\n------------------------------------------\n")
            myfile.write("   Session started: ")
            myfile.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            myfile.write("\n------------------------------------------\n")


    def writeButtonPressToLogFile(self, message):
        """ Writes the text of the button pressed to the logfile.

        :param message: The button's caption text.
        """
        """ """
        with open(logfilename, "a") as myfile:
            myfile.write("\n   BUTTON PRESS: ")
            myfile.write(message)


    def writeClosingTimeToLogFile(self):
        """ Writes the time that the application closed to the logfile. """
        with open(logfilename, "a") as myfile:
            myfile.write("\n\n------------------------------------------\n")
            myfile.write("   Session closed: ")
            myfile.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            myfile.write("\n------------------------------------------\n")


    def closeApplicationCleanly(self):
        """ Speaks the closing text.
            Saves any changes to the brain file.
            Writes the closing time to the log file.
            Closes the application
        """
        pygame.display.quit() # Stop displaying the GUI
        engine = CreateObject("SAPI.SpVoice")
        engine.speak(sv.nonBotVoiceTags + "Closing the program. We hope you have enjoyed using the chat bot application.")
        self.Brain.saveBrain()
        self.writeClosingTimeToLogFile()


    def runLoop(self):
        """ The main PyGame game loop used to display the GUI. """

        # Start the timers
        self.startTimers()

        while 1:
            # Update the current time
            self.currentTime = time.time()

            # Determine current mannerism
            self.setCurrentMannerism()

            # Check if the voice is being used for animating the mouth
            if pygame.mixer.get_busy() == 1:
                self.is_speaking = True
            else:
                self.is_speaking = False

            # Check for events
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.closeApplicationCleanly()
                    return
                elif event.type == KEYDOWN:
                    self.keyPressCallback(event)
                else:  # event listeners for button events
                    if self.checkForButtonPress(event) == 1: #returns 1 if exit is pressed
                        return

            # Update the screen
            self.screen.fill(BLACK)
            self.renderLogo()
            self.renderBotResponseText()
            self.renderButtons()
            self.renderTextInputBox()
            self.renderHeadMoveAnimation()
            self.renderBlinkAnimation()
            self.renderMannerism2Animation()
            self.renderMouthShape()

            pygame.display.update()
            self.clock.tick(30)


def main():
    Interface = MasumiInterface()
    Interface.runLoop()


if __name__ == '__main__':
    main()
