from cmu_graphics import *
import cv2
from PIL import Image
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math
import random

def distance(x0, y0, x1, y1):
    return ((x1 - x0)**2 + (y1 - y0)**2)**0.5

#Do – fist
def Do(points): 
    #fingertip landmarks
    tips = [8, 12, 16, 20]
    middle = [6, 10, 14, 18]
    wrist = points[0]
    
    for i in range(len(tips)):
        tipX, tipY = points[tips[i]]
        middleX, middleY = points[middle[i]]
        wristX, wristY = wrist
        tipDist = distance(tipX, tipY, wristX, wristY)
        knuckleDist = distance(middleX, middleY, wristX, wristY)

        if tipDist > knuckleDist:
            return False
    
    thumbTipY = points[4][1]
    thumbMiddleY = points[3][1]
    thumbJointY = points[2][1]

    if not (thumbTipY < thumbMiddleY):
        return False

    return True


#Re – upward palm
# all fingers and thumb in straight upward line
def Re(points): 

    tips = [8, 12, 16, 20]
    joints = [5, 9, 13, 17]
    wrist = points[0]

    for i in range(len(tips) - 1):
        tipX, tipY = points[tips[i]]
        nextTipX, nextTipY = points[tips[i+1]]
        if abs(tipX - nextTipX) > 0.05:
            return False

    for i in range(len(tips)):
        tipX, tipY = points[tips[i]]
        jointX, jointY = points[joints[i]]
        wristX, wristY = wrist
        tipDist = distance(tipX, tipY, wristX, wristY)
        jointDist = distance(jointX, jointY, wristX, wristY)

        if tipDist < jointDist:
            return False
        
        if points[tips[i]][1] > points[joints[i]][1]:
            return False

        thumbTipX, thumbTipY = points[4]
        thumbJointX, thumbJointY = points[2]

        if thumbTipY > thumbJointY:
            return False
        if distance(thumbTipX, thumbTipY, wristX, wristY) < distance(thumbJointX, thumbJointY, wristX, wristY):
            return False
    
    return True


#Mi – flat palm
def Mi(points):
    tips = [8, 12, 16, 20]
    joints = [5, 9, 13, 17]

    for i in range(len(tips) - 1):
        tipX = points[tips[i]][0]
        tipY = points[tips[i]][1]
        jointX = points[joints[i]][0]
        jointY = points[joints[i]][1]
        nextTipY = points[tips[i + 1]][1]
        nextJointY = points[joints[i + 1]][1]

        if abs(tipY - jointY) > 0.05 or abs(nextJointY - jointY) > 0.07:
            return False
        
        elif abs(tipX - jointX) < 0.1:
            return False
        
        elif abs(nextTipY - tipY) > 0.04:
            return False
    
    return True

#Fa – thumb down
def Fa(points):
    tips = [8, 12, 16, 20]
    joints = [5, 9, 13, 17] # Base knuckles for distance comparison
    wrist = points[0]

    # 4 fingers are curled (Fist-like)
    for i in range(len(tips)):
        tipX, tipY = points[tips[i]]
        jointX, jointY = points[joints[i]]
        wristX, wristY = wrist
        tipDist = distance(tipX, tipY, wristX, wristY)
        jointDist = distance(jointX, jointY, wristX, wristY)

        if tipDist > jointDist:
            return False

    # Check the Thumb
    thumbTipY = points[4][1]
    thumbJointY = points[2][1]
    thumbMiddleY = points[3][1] 
    
    # tip must be > joint.
    if not (thumbTipY > thumbMiddleY > thumbJointY):
        return False
        
    return True


# Sol – flat palm
def Sol(points): 
    tips = [4, 8, 12, 16, 20]
    joints = [2, 5, 9, 13, 17]

    for i in range(len(tips) - 1): 
        tipX = points[tips[i]][0]
        tipY = points[tips[i]][1]
        nextTipY = points[tips[i + 1]][1]
        jointX = points[joints[i]][0]
        jointY = points[joints[i]][1]

        if nextTipY < tipY:
            return False
        elif abs(tipY - jointY) > 0.2:
            return False
        
    return True


#La – downward arched hand
def La(points):
    tips = [8, 12, 16, 20]
    middle = [6, 10, 14, 18]
    joints = [5, 9, 13, 17]

    #fingers point down
    for i in range(len(tips)): 
        tipY = points[tips[i]][1]
        middleY = points[middle[i]][1]
        jointY = points[joints[i]][1]

        if not tipY > middleY > jointY:
            return False
    
    #thumb is lower than fingers and points down
    thumbTipY = points[4][1]
    thumbJointY = points[2][1]
    thumbMiddleY = points[3][1] 
    indexTipY = points[8][1]
    if not thumbTipY > indexTipY:
        return False
    elif not thumbTipY > thumbMiddleY > thumbJointY:
        return False

    return True


#Ti – upward point
def Ti(points): 
    #fist fingertip landmarks
    tips = [12, 16, 20]
    joints = [10, 14, 18]
    
    # check fist
    for i in range(len(tips)):
        tipX = points[tips[i]][0]
        jointX = points[joints[i]][0]
        tipY = points[tips[i]][1]
        jointY = points[joints[i]][1]
        dist = distance(tipX, tipY, jointX, jointY)
        # if tip of last 3 fingers is higher than the join or distance between two are is big
        if tipY < jointY or dist > 0.5:
            return False
    
    # check index finger
    indexTip = points[8]
    indexMiddle = points[6]
    indexJoint = points[5]
    if (indexTip[1] > indexMiddle[1] or indexTip[1] > indexJoint[1] or
        indexMiddle[1] > indexJoint[1]):
        return False

    return True



##################################################################################################


def onAppStart(app):

    app.status = 'start'
    app.readyToStart = False
    app.music = True
    backgroundMusic = 'backgroundMusic.wav'
    app.backgroundMusic = Sound(backgroundMusic)
    if app.music: 
        app.backgroundMusic.play()


    app.width = 800
    app.height = 700

    app.backgroundImage = 'background.png'

    app.gestureGuide = 'Screenshot 2026-04-21 at 23.35.26.png'
    app.images = ['piano.png', 'flute.png', 'violin.png', 
                  'trumpet.png', 'marimba.png', 'sax.png']

    app.instrumentLeftTop = [(30, 300), (30+160, 300), (30+160*2, 300), 
                            (30, 470), (30+160, 470), (30+160*2, 470)]
    
    # image dimensions
    app.instrumentWidth = getImageSize('piano.png')[0] / 4
    app.instrumentHeight = getImageSize('piano.png')[1] / 4

    # instrument sounds
    app.pianoSounds = {'Do': 'Piano_Do.wav', 'Re': 'Piano_Re.wav', 'Mi': 'Piano_Mi.wav', 
                       'Fa': 'Piano_Fa.wav', 'Sol': 'Piano_Sol.wav', 'La': 'Piano_La.wav', 
                       'Ti': 'Piano_Ti.wav'}
    app.fluteSounds = {'Do': 'Flute_Do.wav', 'Re': 'Flute_Re.wav', 'Mi': 'Flute_Mi.wav', 
                       'Fa': 'Flute_Fa.wav', 'Sol': 'Flute_Sol.wav', 'La': 'Flute_La.wav', 
                       'Ti': 'Flute_Ti.wav'}
    app.violinSounds = {'Do': 'Violin_Do.wav', 'Re': 'Violin_Re.wav', 'Mi': 'Violin_Mi.wav', 
                       'Fa': 'Violin_Fa.wav', 'Sol': 'Violin_Sol.wav', 'La': 'Violin_La.wav', 
                       'Ti': 'Violin_Ti.wav'}
    app.trumpetSounds = {'Do': 'Trumpet_Do.wav', 'Re': 'Trumpet_Re.wav', 'Mi': 'Trumpet_Mi.wav', 
                       'Fa': 'Trumpet_Fa.wav', 'Sol': 'Trumpet_Sol.wav', 'La': 'Trumpet_La.wav', 
                       'Ti': 'Trumpet_Ti.wav'}
    app.marimbaSounds = {'Do': 'Marimba_Do.wav', 'Re': 'Marimba_Re.wav', 'Mi': 'Marimba_Mi.wav', 
                       'Fa': 'Marimba_Fa.wav', 'Sol': 'Marimba_Sol.wav', 'La': 'Marimba_La.wav', 
                       'Ti': 'Marimba_Ti.wav'}
    app.saxSounds = {'Do': 'Sax_Do.wav', 'Re': 'Sax_Re.wav', 'Mi': 'Sax_Mi.wav', 
                       'Fa': 'Sax_Fa.wav', 'Sol': 'Sax_Sol.wav', 'La': 'Sax_La.wav', 
                       'Ti': 'Sax_Ti.wav'}

    app.instrumentIndex = ['piano', 'flute', 'violin', 
                            'trumpet', 'marimba', 'sax']
    app.instrumentSoundIndex = [app.pianoSounds,  app.fluteSounds, app.violinSounds, 
                                app.trumpetSounds, app.marimbaSounds, app.saxSounds]
    
    app.instrument = 'piano'
    app.instrumentSound = app.pianoSounds
    app.note = None
    app.lastNote = None

    app.sound = None

    app.showCam = True



# THE FOLLOWING BLOCK OF CODE IS 90% AI (cool webcam stuff but dk how to do :( )
# GEMINI PRO
####################################################################################################

    # Initialize the webcam
    app.camera = cv2.VideoCapture(0)
    app.currentFrame = None
    # Set step rate to roughly 30 FPS
    app.stepsPerSecond = 30

    # Hand landmarks:
    app.pointsToDraw = []
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        running_mode=vision.RunningMode.VIDEO)
    app.detector = vision.HandLandmarker.create_from_options(options)
 
    #Buffer:
    app.currentlyHeldNote = None 
    app.heldCounter = 0
    app.lastPlayedNote = None
    
    # 0.2 seconds at 30 sps is 6 steps
    app.requiredHoldTime = 6

####################################################################################################



def redrawAll(app):

    imageWidth, imageHeight = getImageSize(app.backgroundImage)
    drawImage(app.backgroundImage, app.width / 2 + 200, app.height / 2 - 10, 
              width=imageWidth / 1.2, height=imageHeight / 1.2, 
              align = 'center', opacity = 50)



    if app.status == 'start': 

        drawLabel('Wave For Music', app.width / 2, 300, 
                size = 80, font = 'cursive', 
                fill = gradient('rosyBrown', 'wheat', 'black', start = 'right-bottom'), 
                border = 'dimGray', borderWidth = 1)

        drawRect(app.width / 2, app.height / 2 + 100, 350, 70, align = 'center', 
                 fill = gradient('cornSilk', 'wheat', 'rosyBrown', start = 'center'))
        
        #border: 
        borderWid = 5 if app.readyToStart is True else 2
        borderLength = 360 if app.readyToStart is True else 350
        borderHeight = 80 if app.readyToStart is True else 70
        opac = 100 if app.readyToStart is True else 60

        drawRect(app.width / 2, app.height / 2 + 100, borderLength, borderHeight, 
                 align = 'center', fill = None, border = 'darkKhaki', 
                 borderWidth = borderWid, opacity = opac)

        drawRect(app.width / 2, app.height / 2 + 100, 330, 50, align = 'center', 
                 fill = None, border = 'darkKhaki', borderWidth = 2, opacity = opac)
        
        drawLabel('Click To Make Music', app.width / 2, app.height / 2 + 100, 
                size = 30, font = 'cursive')
        

    elif app.status == 'game': 
        imageWidth, imageHeight = getImageSize(app.gestureGuide)
        drawImage(app.gestureGuide, 650, 470, align = 'center', 
                width=imageWidth/3.5, height=imageHeight/3.5, 
                border ='gold', borderWidth = 4, opacity = 95)

        drawLabel('Wave For Music', app.width / 2 - 120, 45, 
                size = 60, font = 'cursive', 
                fill = gradient('gray', 'rosyBrown', 'wheat', 'black', start = 'right-bottom'), 
                border = 'dimGray', borderWidth = 1)
        
        drawLabel('Make note gesture with right hand in front', app.width / 2 - 120, 110, 
                size = 22, font = 'cursive')
        
        drawLabel('of your webcam to play note', app.width / 2 - 120, 145, 
                size = 22, font = 'cursive')
        
        drawLabel("Press 'p' to paused music", 280, 190, size = 16, 
                  fill = 'mediumVioletRed', font = 'cursive', border = 'mediumVioletRed', borderWidth = 0.5)
        drawLabel("Press 'c' to hide/unhide camera", 280, 215, size = 16, 
                  fill = 'mediumVioletRed', font = 'cursive', border = 'mediumVioletRed', borderWidth = 0.5)

        drawLabel('Pick your instrument', 270, 260, size = 30, font = 'cursive')

        drawRect(120, 660, 170, 40, fill = 'white', opacity = 60, align = 'center', 
                 border = 'black', borderWidth = 1)
        drawLabel("'h' to return to start page", 120, 660, size = 14, font = 'cursive', 
                  border = 'black', borderWidth = 0.5)


        # Intrument images
        for i in range(len(app.images)):
            image = app.images[i]
            instrument = app.instrumentIndex[i]
            left, top = app.instrumentLeftTop[i]
            
            color = 'goldenrod' if app.instrument == instrument else 'dimGray'
            borderWidth = 4 if color == 'gold' else 2
            drawImage(image, left, top, width = app.instrumentWidth, height = app.instrumentHeight, 
                    opacity = 90)
            drawRect(left, top, app.instrumentWidth, app.instrumentHeight, fill = None, 
                        border = color, borderWidth = borderWidth)


    # THE FOLLOWING BLOCK OF CODE IS 50% AI (USED AI TO WORK OUT LOGIC AND DEBUG)  
    # GEMINI PRO
    ####################################################################################################
        if app.showCam: 
            Webcam
            drawRect(520, 30, 252, 202, fill = None, 
                        border = gradient('black', 'darkGoldenrod', start = 'left-top'), 
                        borderWidth = 2)
            if app.currentFrame is not None:
                # Draw the webcam feed 
                drawImage(app.currentFrame, 520, 30, width=250, height=200)
            else:
                drawLabel("Loading Camera...", 520, 30)

            # DRAW HAND LANDMARKS
            camX, camY = 520, 30
            camW, camH = 250, 200

            for handX, handY in app.pointsToDraw:
                # Scale normalized coordinates to pixel size
                px = camX + (handX * camW)
                py = camY + (handY * camH)
                drawCircle(px, py, 3, fill='maroon', border='black', borderWidth=0.5, opacity = 70)

####################################################################################################
            drawCircle(645, 130, 50, fill = None, border = 'aqua', 
                   opacity = 70, dashes = True)
        
            drawLabel('Make gesture in the circle', 645, 250, size = 18, font = 'cursive')




def isInSquare(app, mX, mY, left, top, width, height): 
    right, bottom = left + width, top + height
    return left <= mX <= right and top <= mY <= bottom

def onMouseMove(app, mouseX, mouseY):
    if app.status == 'start': 
        if isInSquare(app, mouseX, mouseY, 225, 415, 350, 70):
            app.readyToStart = True
        else:
            app.readyToStart = False

def clickInSquare(app, mouseX, mouseY):     
    for i in range(len(app.instrumentLeftTop)):
        left, top = app.instrumentLeftTop[i]
        if (left <= mouseX <= left + app.instrumentWidth and
            top <= mouseY <= top + app.instrumentHeight): 
                return i
    return None



def onMousePress(app, mouseX, mouseY):
    i = clickInSquare(app, mouseX, mouseY)
    if app.status == 'start' and app.readyToStart:
        app.status = 'game'

    elif app.status == 'game' and i is not None:
       app.instrument = app.instrumentIndex[i]
       app.instrumentSound = app.instrumentSoundIndex[i]
       if app.note is not None:
           app.sound = app.instrumentSound[app.note]
    


def onKeyPress(app, key): 
    if key == 'escape':
        app.status = 'game'
    
    if (app.status != 'start') and key == 'h':
        app.status = 'start'
    
    if key == 'p':
        app.music = not app.music
        if app.music is False: 
            app.backgroundMusic.pause()
        elif app.music is True:
            app.backgroundMusic.play(loop = True)
    
    if app.status == 'game' and key == 'c': 
        app.showCam = not app.showCam



def onStep(app):

    # THE FOLLOWING CODE IS FROM GEMINI PRO
    ######################################################################################################
    # 1. Capture frame from webcam
    ret, frame = app.camera.read()
    
    if ret:
        # 2. Mirror the image for a natural "Photo Booth" feel
        frame = cv2.flip(frame, 1)
        
        # 3. Convert OpenCV BGR format to RGB for PIL
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 4. Convert to a PIL image so cmu_graphics can display it
        pilImage = Image.fromarray(frame)
        
        # 5. Resize to fit the app window if necessary
        app.currentFrame = CMUImage(pilImage)
    
    # Draw hand landmarks
    # Detect Hand Landmarks (The "Brain")
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    
    # Use clock for timestamp required by VIDEO mode
    timestamp_ms = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)
    result = app.detector.detect_for_video(mp_image, timestamp_ms)
    
    app.pointsToDraw = []
    if result.hand_landmarks:
        hand = result.hand_landmarks[0]
        # Store just the (x, y) for drawing
        for lm in hand:
            app.pointsToDraw.append((lm.x, lm.y))
    ######################################################################################################

    if len(app.pointsToDraw) == 21:    
        if Do(app.pointsToDraw):    app.note = 'Do'
        elif Re(app.pointsToDraw):  app.note = 'Re'
        elif Mi(app.pointsToDraw):  app.note = 'Mi'
        elif Fa(app.pointsToDraw):  app.note = 'Fa'
        elif Sol(app.pointsToDraw): app.note = 'Sol'
        elif La(app.pointsToDraw):  app.note = 'La'
        elif Ti(app.pointsToDraw):  app.note = 'Ti'
        else:                       app.note = None
    
    # THE FOLLOWING CODE IS MOSTLY AI
    ######################################################################################################
    if app.status == 'game' or app.status == 'startSimon':
        # 1. Stability Buffer: Check if the note is being held
        if app.note is not None and app.note == app.currentlyHeldNote:
            app.heldCounter += 1
        else:
            app.currentlyHeldNote = app.note
            app.heldCounter = 0

        # 2. Trigger the sound once the "Hold Time" (6 frames) is reached
        if app.heldCounter == app.requiredHoldTime:
            # Only play if it's a new note (prevents infinite looping)
            if app.currentlyHeldNote != app.lastPlayedNote:
                soundPath = app.instrumentSound.get(app.currentlyHeldNote)
                if soundPath:
                    Sound(soundPath).play()
                app.lastPlayedNote = app.currentlyHeldNote
        
        # Reset lastPlayedNote if hand is removed so you can play the same note twice
        if app.note is None:
            app.lastPlayedNote = None
    ######################################################################################################


        
runApp()