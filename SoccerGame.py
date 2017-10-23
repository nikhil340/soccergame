
import PIL
import math
from random import randrange
from PIL import Image,ImageTk
from tkinter import *
import winsound, sys

#images from giochisport.com


####################################
# customize these functions
####################################

def init(data):

    data.playBegins = 0                 # 1 ==> begin play, 0 otherwise. set to 2 after a round of shots to reset the canvas for next set of shots
    data.otherPlayersDrawn = 0          # 0 ==> draw other players, 1 ==> do not draw
    data.ballToGlove = 50               # max distance between ball and glove to find a blocked shot
    data.timeBetweenShots = 1000        # This value is used as time lag between two consecutive shots
    data.timeLog = 0                    # time from the begging of each shot (this value is compared with timeBetweenShots for next shot)
    data.maxBallSizeExit = 70           # Max size of ball before it is declared as GOAL
    data.maxBallSizeEntry = 40          # Min size of ball before gloves can reach it
    data.rotationAngle = 10             # ball spin angle
    data.minBallSize = 5                # min size for ball (reset to this size at start and at the end of retreat)
    data.gkScore = 0                    # Goal keepers score (1 point for each block)
    data.cpuScore = 0                   # Shooter's score (1 point for two consecutive GOALS)
    data.blocks = 0                     # Number of consecutive blocks       
    data.shotNumber = 1                 # Shot number counter
    data.MaxShots = 9                   # Max number of shots            
    #determines randomly the x direction of the ball, left or right
    data.xIncRand = 15					# use this to control game speed - larger increments for X coord ==> faster ball movement
    data.xInc = randrange(-data.xIncRand,data.xIncRand)       # used in projectile calculation - X coord is changed by this value and Y coord is computed using the quadratic formula
    #values for quadratic coefficients for ball movements
    data.aIni = 0.001
    data.bIni = 0.01
    data.cIni = 0.1
    data.a = data.aIni
    data.b = data.bIni
    data.c = data.cIni
    data.cRetreat = data.c * 2
    data.bRetreat = data.b * -2
    data.aRetreat = data.a * 1 

    data.xCenter = 500                  # X coord of canvas center
    data.yCenter = 250                  # Y coord of canvas center
    data.gloveX = data.xCenter          # glove start X coord  
    data.gloveY = data.yCenter          # golve start Y coord
    data.xShift = 0                     # Associated with projectile motion
    data.angle = 0                      # Associated with ball rotation
    data.difficultyLevel = 1            # 1 ==> Low, 2 ==> Medium, 3 ==> High
    data.save = False                   # flag indicating Goal or Block
    data.retreat = 1                    # 1 ==> forward motion of ball, -1 ==> retreat
    data.rInc = 1                       # Ball size increment
    data.xG = 0                         # glove x coord position at any given instant                      
    data.yG = 0                         # glove y coord position at any given instant 
    data.keys = []    

def timerFired(data):

    # do the following at the beginning of the game when data.playBegins == 0 - set the screen....
    if data.playBegins == 0:

        data.r1 = data.minBallSize
        data.xStart = int(data.xCenter * randrange(6,14)*0.1)                   # Shooter's start X coord
        data.yStart = data.yCenter + 100 * randrange(8,12)*0.1                  # Shooter's start Y coord
        data.timerDelay=5*int((4-data.difficultyLevel)) 
        score = data.canvas.create_text(750,525,text =str(data.cpuScore),
            fill="Blue", font="EASPORTS15 26 bold",tag="cpuTag")    
        score = data.canvas.create_text(250,525,text =str(data.gkScore),
            fill="Yellow", font="EASPORTS15 26 bold",tag="gkTag")
        data.BackGround = BackGround(data.xCenter,data.yCenter,
            "SoccerField1.gif",data.canvas) 

    # "data.playBegins" is set to 2 after a round of shots are over. The following resets canvas for next set of shots
    if data.playBegins == 2:
    	data.cpuScore = 0
    	data.gkScore = 0
    	data.playBegins = 1
    	data.canvas.delete("WonTag")
    	data.canvas.delete("SorryTag")
	

    # Do the following only when playBegins == 1 and for each of the MaxShots
    if data.playBegins == 1 and data.shotNumber<=data.MaxShots:        

        data.canvas.delete("cpuTag")
        score = data.canvas.create_text(750,525,text =str(data.cpuScore),
            fill="Blue", font="EASPORTS15 26 bold",tag="cpuTag") 
        data.canvas.delete("gkTag")
        score = data.canvas.create_text(250,525,text =str(data.gkScore),
            fill="Yellow", font="EASPORTS15 26 bold",tag="gkTag")
        data.KickerSize = int(50 * (data.yStart-25)/data.yCenter)
        data.Kicker = Kicker(data.xStart+25,data.yStart-25,"tmp-0.gif",
            data.canvas,data.KickerSize)
        #data.Kicker.lowerPlayer(data.canvas)
        #data.Ref = Ref(data.xStart-10*randrange(-8,8),data.yStart,"ref1.gif",
            #data.canvas,data.KickerSize,"refTag")
        data.canvas.delete("ShotNum")
        score = data.canvas.create_text(580,530,fill='Green',
            font="Helvetica 26 bold",
            text=str(data.shotNumber)+"/"+str(data.MaxShots),tag="ShotNum")

        # Do the following (display other players) ONLY when "otherPlayersDrawn"
        # to 0, this value is reset after each shot
        if data.otherPlayersDrawn == 0:
            data.BackGround = BackGround(data.xCenter,data.yCenter,
                "SoccerField9.gif",data.canvas)
            data.gloves = Player(data.gloveX,data.gloveY,"glovesPic.gif",
                data.canvas)
            data.gloves.liftPlayer(data.canvas)

                     
            data.otherPlayersDrawn = 1       

        data.angle += data.rotationAngle    # rotate ball position
        data.timeLog += data.timerDelay     # time from the beginning of shot

        if data.timeLog > data.timeBetweenShots:
            #Quadratic for parabolic motion of ball
            data.xShift += data.xInc
            data.yShift = data.a*data.xShift**2 + data.b*data.xShift + data.c
            x1 = data.xStart + data.xShift
            y1 = data.yStart - data.yShift
            if x1 < 30 or x1 > 970 or y1 < 60:
                y1 = 1000

            data.KickerSize = int(50 * (data.yStart-25)/data.yCenter)
            data.Kicker = Kicker(data.xStart+25,data.yStart-25,"tmp-4.gif",
                data.canvas,data.KickerSize)
            data.AnimatedBall = AnimatedBall(x1,y1,data.r1,data.angle,
                "AnimBall.gif",data.canvas)
  
            # change ball size based on forward/retreat motion 
            data.r1 += data.rInc*data.retreat  

            #distance between ball and glove
            dist = ((x1-data.xG)**2+(y1-data.yG)**2)**0.5

            # When ball is BLOCKED
            if dist < data.ballToGlove and \
            (data.r1>data.maxBallSizeEntry and data.r1<=data.maxBallSizeExit):
                if not data.save:   
                    data.save = True
                    data.retreat = -1
                    data.a = data.aRetreat                    
                    data.b = data.bRetreat
                    data.c = data.cRetreat                    
                    data.timerDelay = int(data.timerDelay * 1.3)
                    # update player scores
                    data.blocks += 1
                    if data.blocks == 2:
                        data.gkScore += 1
                        data.blocks = 0
                    data.canvas.delete("gkTag")
                    score = data.canvas.create_text(250,525,
                        text =str(data.gkScore),fill="Yellow", 
                        font="EASPORTS15 26 bold",tag="gkTag")
                    # play cheering audio
                    soundfile = "cheer.wav"
                    winsound.PlaySound(soundfile, 
                        winsound.SND_FILENAME|winsound.SND_ASYNC)  
                    data.gloves.liftPlayer(data.canvas)

            # Ball size > data.maxBallSizeExit ==> GOAL
            if data.r1 > data.maxBallSizeExit:
                # update CPU score
                data.cpuScore += 1
                data.blocks = 0 
                data.canvas.delete("cpuTag")
                score = data.canvas.create_text(750,525,
                    text =str(data.cpuScore),fill="Blue", 
                    font="EASPORTS15 26 bold",tag="cpuTag") 
                soundfile = "applause.wav"
                winsound.PlaySound(soundfile, 
                    winsound.SND_FILENAME|winsound.SND_ASYNC)                                      

            # Reset data for next shot
            if (data.r1 < data.minBallSize and data.retreat<0) or \
            data.r1>data.maxBallSizeExit:
                data.canvas.delete("ShotNum")
                score = data.canvas.create_text(580,530,fill='Green',
                    font="EASPORTS15 26 bold",
                    text=str(data.shotNumber),tag="ShotNum")                 
                data.shotNumber += 1
                data.xShift = 0
                data.a = data.aIni
                data.b = data.bIni
                data.c = data.cIni             
                data.r1 = data.minBallSize
                data.angle = 0
                data.retreat = 1
                data.save = False
                data.xStart = int(data.xCenter * randrange(6,14)*0.1)
                data.yStart = data.yCenter + 100 * randrange(8,12)*0.1
                data.xInc = randrange(-data.xIncRand,data.xIncRand)
                data.AnimatedBall.kill(data.canvas)
                data.timerDelay=5*int((4-data.difficultyLevel)*randrange (10,
                    20)*0.1)
                data.timeLog = 0
                data.otherPlayersDrawn = 0
                data.gloves.liftPlayer(data.canvas)

            # check who won the game                
            if data.shotNumber > data.MaxShots:    
                if data.cpuScore < data.gkScore:
                    score = data.canvas.create_text(505,400,fill='Yellow',
                        font=("EA Font v1.5 by Ghettoshark", 26, ),
                        text="You Won!",tag="WonTag")
                else: 
                	score = data.canvas.create_text(500,400,fill='Red',
                        font=("EA Font v1.5 by Ghettoshark", 15, ),
                        text="Sorry, try again!",tag="SorryTag")

            data.gloves.liftPlayer(data.canvas)
            data.BackGround.lowerPlayer(data.canvas)

# Calling methods which in turn call canvas.coords
def angleCalc(xG,yG):
    opposite = -1 * (yG-500)
    adjacent = (xG-500)
    angle = 0
    try: angle = math.atan(opposite/(adjacent+1))*(180/math.pi)+90
    except ZeroDivisionError:
        pass  
    if xG>500:
        angle+=180
    return angle

def mousePressed(event, data):
    pass

def mouseMoved(event, data):
    if data.playBegins == 1:
        data.xG = event.x
        data.yG = event.y
        data.gloves.moveTo(data.xG, data.yG, data.canvas)
    else: pass
         
def keyPressed(event, data):
    if event.keysym not in data.keys:
        data.keys.append(event.keysym)

def keyReleased(event, data):
    if event.keysym in data.keys:
        data.keys.remove(event.keysym)

class Kicker(object):
    def __init__(self,x,y,filename,canvas,KickerSize):
        
        self.im = PIL.Image.open(filename)
        self.im = self.im.convert('RGBA')         
        self.im = self.im.resize((KickerSize, KickerSize), PIL.Image.ANTIALIAS)
        self.picture = ImageTk.PhotoImage(self.im)
        self.img = canvas.create_image(x, y, image = self.picture)  

    def lowerPlayer(self, canvas):
        canvas.lower(self.img)

class Ref(object):
    def __init__(self,x,y,filename,canvas,KickerSize,tagName1):
        
        self.im = PIL.Image.open(filename)
        self.im = self.im.convert('RGBA')         
        self.im = self.im.resize((KickerSize, KickerSize), PIL.Image.ANTIALIAS)
        self.picture = ImageTk.PhotoImage(self.im)
        canvas.delete(tagName1)        
        self.img = canvas.create_image(x, y, image = self.picture, tag=tagName1)  

    def lowerPlayer(self, canvas):
        canvas.lower(self.img)

class otherPlayers(object):
    def __init__(self,x,y,Dia,filename,canvas,tagName):
        
        self.im = PIL.Image.open(filename)
        self.im = self.im.convert('RGBA')        
        self.im = self.im.resize((Dia, Dia), PIL.Image.ANTIALIAS)
        self.picture = ImageTk.PhotoImage(self.im)
        label = Label(image=self.picture)
        label.image = self.picture # keep a reference!
        canvas.delete(tagName)
        self.img = canvas.create_image(x, y, image=self.picture, tag=tagName)
 
class AnimatedBall(object):
    def __init__(self,x,y,Dia,newAngle,filename,canvas):
        
        self.im = PIL.Image.open(filename)
        self.im = self.im.convert('RGBA')        
        self.im = self.im.resize((Dia, Dia), PIL.Image.ANTIALIAS)
        self.picture = ImageTk.PhotoImage(self.im.rotate(newAngle,expand=True))
        self.img = canvas.create_image(x, y, image = self.picture)

    def kill(self, canvas):
        canvas.delete(self.img)

    def liftPlayer(self, canvas):
        canvas.lift(self.img)

    def stopBall(self,x,y,canvas):
        self.draw(canvas,(x,y,30))
        
    def lowerPlayer(self, canvas):
        canvas.lower(self.img)
         
class BackGround(object):
    def __init__(self,x,y,filename,canvas):
        
        self.im = PIL.Image.open(filename)
        self.im = self.im.resize((1000, 500), PIL.Image.ANTIALIAS)
        self.picture = ImageTk.PhotoImage(self.im)
        self.img = canvas.create_image(x, y, image = self.picture)  

    def lowerPlayer(self, canvas):
        canvas.lower(self.img)

class Player(object):

    def __init__(self, x, y, filename, canvas):
        self.im = PIL.Image.open(filename)
        self.im = self.im.convert('RGBA')         
        self.im = self.im.resize((98, 75), PIL.Image.ANTIALIAS)
        self.picture = ImageTk.PhotoImage(self.im)        
        self.img = canvas.create_image(x, y, image = self.picture)  

    def moveDelta(self, dx, dy, canvas):
        self.x += dx
        self.y += dy
        canvas.coords(self.img, self.x, self.y )    

    def moveTo(self, x, y, canvas):
        self.angle = angleCalc(x,y)
        self.picture = ImageTk.PhotoImage(self.im.rotate(self.angle,
            expand=True))  
        self.img = canvas.create_image(x, y, image = self.picture)  
        canvas.coords( self.img, x, y )

    def liftPlayer(self, canvas):
        canvas.lift(self.img)

    def lowerPlayer(self, canvas):
        canvas.lower(self.img)

    def kill(self, canvas):
        canvas.delete(self.img)

class Ball(object):
    def __init__(self,x,y,r,canvas):
        self.x = x
        self.y = y
        self.r = r
        self.smallR = r/4
        self.canvas = canvas
        self.ballSpot = canvas.create_oval(x-self.smallR,
         y-self.smallR, x+self.smallR, y+self.smallR, fill="black")
        self.ball = canvas.create_oval(self.x-self.r, self.y-self.r, 
            elf.x+self.r, self.y+self.r, fill="white")        
        
    def draw(self,canvas,increments):
        self.increments = increments 
        (x,y,r) = self.increments   
        spotR = r/4   
        self.ballSpot = canvas.create_oval(x-spotR,y-spotR,
            x+spotR,y+spotR,fill="black")
        self.ball = canvas.create_oval(x-r,y-r,x+r,y+r,fill="white")     

    def kill(self, canvas):
        canvas.delete(self.ball)
        canvas.delete(self.ballSpot)

    def liftPlayer(self, canvas):
        canvas.lift(self.ball)
        canvas.lift(self.ballSpot)
        # lift can be called on the handle to any canvas drawing

    def stopBall(self,x,y,canvas):
        self.draw(canvas,(x,y,30))

    def moveSpot(self,dx,canvas):
        pass        

class BallSpin(object):
    def __init__(self,x,y,r,canvas):
        self.x = x
        self.y = y
        self.r = r/4
        self.canvas = canvas
        self.ball = canvas.create_oval(x-r, y-r, x+r, y+r, fill="black")

    def draw(self,canvas,increments,dx):
        self.increments = increments 
        (x,y,r) = self.increments      
        r=4
               
        self.ball = canvas.create_oval(x-r,y-r,x+r,y+r,fill="black")
        x+=dx
        canvas.coords(self.ball,x-r,y-r,x+r,y+r)

    def moveDelta(self, dx, dy, canvas):
        (x,y,r) = self.increments
        x+=dx        
        canvas.coords(self.ball,x-r,y-r,x+r,y+r)

    def kill(self, canvas):
        canvas.delete(self.ball)

    def liftPlayer(self, canvas):
        canvas.lift(self.ball)

    def stopBall(self,x,y,canvas):
        self.draw(canvas,(x,y,30),0)
    
####################################
# use the run function as-is
####################################
def run(width=800, height=800):
   
    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)

    def mouseMovedWrapper(event, canvas, data):
        mouseMoved(event, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)

    def keyReleasedWrapper(event, canvas, data):
        keyReleased(event, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
        if data.shotNumber > data.MaxShots:        # Options to be displayed after game over
        	button1.lift()                         # show play button
        	radioButton1.lift()                    # show radio buttons
        	radioButton2.lift()                    
        	radioButton3.lift()
        	button2.lift()                         # show instructions button
    	
    def skillLevelIndex():      # Attached to radio buttons, called when a radio button is selected
        data.difficultyLevel = v.get()

    def startPlay():            # when Play button is pressed on the opening screen
        data.playBegins = 1     # Used in timerFired
        button1.lower()         # Hide play bu    
        radioButton1.lower()    # Hide radio buttons
        radioButton2.lower()
        radioButton3.lower()
        data.shotNumber = 1
        data.playBegins = 2     # Allows for resetting some values in TimerFired
        button2.lower()         # Hide instructions button
        lab1.lower()            # Hide instructions label

    def instructionsDisplay():  # Instructions related 
        lab1.lift()             # Show instructions label

    # Set up data and call init
    class Struct(object): pass
    root = Tk()    
    v = IntVar()                # v is an array element for radio button data
    v.set(2)                    # set defult difficulty level to Medium    
    data = Struct()
    data.width = width
    data.height = height
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # Create a button on the opening screen and place text at the bottom
    button1 = Button(text = "Play", command=startPlay,
    font=("EA Font v1.5 by Ghettoshark", 26, ))                    # calls startPlay() when clicked on this button
    button1.configure(width = 5,relief=RAISED)
    button1_window = canvas.create_window(550, 170, anchor=NW, window=button1)
    # Create a button on the opening screen and place text at the bottom
    button2 = Button(text = "Instructions", command=instructionsDisplay,
    font=("EA Font v1.5 by Ghettoshark", 16, ))  # calls instructionsDisplay() when clicked on this button
    button2.configure(width = 15,relief=RAISED)
    button2_window = canvas.create_window(405, 300, anchor=NW, window=button2)
    lab1 = Label(text="Select difficulty level and click on Play. Player (CPU) shoots the ball after a brief pause and you are supposed to block the shot by moving your gloves. You need to block two CONSECUTIVE shots to score a point. Player scores a point for each completed shot. There will be a total of 9 shots. Good luck!")
    lab1.configure(width = 80,relief=FLAT,wraplength=500, justify=LEFT)
    lab1_window = canvas.create_window(220,370,anchor=NW,window=lab1)
    lab1.lower()
    # Create rectangle boxes at the bottom of the screen and write text
    canvas.create_rectangle(0, 600, 350, 500, width=0, fill='blue')  #.create_rectangle(x0, y0, x1, y1, option, ...)
    canvas.create_rectangle(650, 600, 1000, 500, width=0, fill='yellow')    
    canvas.create_text(60,530,fill='Yellow',font=("EA Font v1.5 by Ghettoshark",
     15, ),text="Goalkeeper")
    canvas.create_text(940,530,fill='Blue',font=("EA Font v1.5 by Ghettoshark",
     15, ),text="Player (CPU)")  
    canvas.create_text(515,528,fill='Green',font=("EA Font v1.5 by Ghettoshark",
     26, ),text="Shot #")
    # setup radio buttons for skill level selection
    radioButton1=Radiobutton(text="Difficulty Level: Low", variable=v, value=1,
    command=skillLevelIndex,justify=RIGHT)   # calls skillLevel() when clicked on this button
    radioButton1.configure(width = 20,relief=RAISED)
    radioButton2=Radiobutton(text="Difficulty Level: Medium", variable=v,
     value=2,command=skillLevelIndex,justify=LEFT) # calls skillLevel() when clicked on this button
    radioButton2.configure(width = 20,relief=RAISED)
    radioButton3=Radiobutton(text="Difficulty Level: High", variable=v,
     value=3,command=skillLevelIndex,justify=LEFT)   # calls skillLevel() when clicked on this button
    radioButton3.configure(width = 20,relief=RAISED)
    radioButton1_window = canvas.create_window(300, 150, anchor=NW,
     window=radioButton1)
    radioButton2_window = canvas.create_window(300, 200, anchor=NW,
     window=radioButton2)
    radioButton3_window = canvas.create_window(300, 250, anchor=NW,
     window=radioButton3)  

    data.canvas = canvas                    # Save canvas in data so any fn can access it
    init(data)                              # Make sure to call init AFTER data.canvas
    
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Motion>", lambda event:
                            mouseMovedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    root.bind("<KeyRelease>", lambda event:
                            keyReleasedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1000, 550)