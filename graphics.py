from cmu_graphics import *
import cv2
from PIL import Image
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math

#Do – fist
def Do(points): 
    #fingertip landmarks
    tips = [8, 12, 16, 20]
    joints = [6, 10, 14, 18]
    
    for i in range(len(tips)):
        tipX = points[tips[i]][0]
        jointX = points[joints[i]][0]
        tipY = points[tips[i]][1]
        jointY = points[joints[i]][1]

        if tipX < jointX or tipY < jointY:
            return False
    
    thumbTip = points[4]
    pinkyBase = points[17]
    # If the thumb tip is close to the pinky base, it's likely tucked in
    dist = math.sqrt((thumbTip[0] - pinkyBase[0])**2 + (thumbTip[1] - pinkyBase[1])**2)
    
    if dist > 0.25: # Thumb is too far out (hitchhiking or open palm)
        return False

    return True


#Re – upward palm
# all fingers and thumb in straight upward line
def Re(points): 
    tips = [4, 8, 12, 16, 20]
    middle = [3, 6, 10, 14, 18]
    joints = [2, 5, 9, 13, 17]

    for i in range(len(tips)):
        if (points[tips[i]][1] > points[middle[i]][1] or 
            points[tips[i]][1] > points[joints[i]][1] or 
            points[middle[i]][1] > points[joints[i]][1]):
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
        
        elif abs(nextTipY - tipY) > 0.1:
            return False
    
    return True

#Fa – thumb down
def Fa(points):
    
    # 4 fingers are curled (Fist-like)
    tips = [8, 12, 16, 20]
    joints = [5, 9, 13, 17]
    for i in range(len(tips)):
        # small horizontal distance 
        if abs(points[tips[i]][0] - points[joints[i]][0]) > 0.15:
            return False

    # Check the Thumb
    thumbTipY = points[4][1]
    thumbJointY = points[2][1]
    thumbMiddleY = points[3][1] 
    
    # In screen coordinates, Down = Larger Y.
    # So tip must be > joint.
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

        if nextTipY > tipY:
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
# 3 fingers into fist
# index finger pointing up
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
    app.width = 800
    app.height = 700

    app.gestureGuide = 'https://aabb2694.rocketcdn.me/wp-content/uploads/2021/08/unnamed2.jpg'
    app.images = ['piano.png', 'flute.png', 'violin.png', 
                  'trumpet.png', 'marimba.png', 'sax.png']

    app.instrumentIndex = ['piano', 'flute', 'violin', 
                          'trumpet', 'marimba', 'sax']
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

    app.instrument = app.pianoSounds
    app.note = 'Do'

    app.sound = None


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



def redrawAll(app):
    imageWidth, imageHeight = getImageSize(app.gestureGuide)
    drawImage(app.gestureGuide, 650, 450, align = 'center', 
              width=imageWidth/1.5, height=imageHeight/1.3)

    drawLabel('Wave For Music', app.width / 2 - 100, 45, 
              size = 60, font = 'cursive', 
              border = 'black', borderWidth = 4)
    drawLabel('Make hand gesture in front of your', app.width / 2 - 100, 110, 
              size = 22, font = 'cursive', border = 'black', borderWidth = 1)
    drawLabel('webcam to play note', app.width / 2 - 100, 145, 
              size = 22, font = 'cursive', 
              border = 'black', borderWidth = 1)

    drawLabel('Pick your instrument', 270, 250, size = 30, font = 'cursive')

    drawLabel(str(app.note), 700, 600, 
              size = 20, fill = 'brown', bold = True)

    # Intrument images
    for i in range(len(app.images)):
        image = app.images[i]
        instrument = app.instrumentIndex[i]
        left, top = app.instrumentLeftTop[i]
        
        color = 'gold' if app.instrument == instrument else 'black'
        borderWidth = 4 if color == 'gold' else 2
        drawImage(image, left, top, width = app.instrumentWidth, height = app.instrumentHeight)
        drawRect(left, top, app.instrumentWidth, app.instrumentHeight, fill = None, 
                    border = color, borderWidth = borderWidth)
    

    #WEBCAM
    if app.currentFrame is not None:
        # Draw the webcam feed in the center
        drawImage(app.currentFrame, 520, 30, width=250, height=200)
    else:
        drawLabel("Loading Camera...", app.width/2, app.height/2)

    # DRAW HAND LANDMARKS
    camX, camY = 520, 30
    camW, camH = 250, 200

    for x_norm, y_norm in app.pointsToDraw:
        # Scale normalized coordinates to pixel size
        px = camX + (x_norm * camW)
        py = camY + (y_norm * camH)
        drawCircle(px, py, 3, fill='crimson', border='black', borderWidth=0.5, opacity = 70)



def onMousePress(app, mouseX, mouseY):
    i = clickInSquare(app, mouseX, mouseY)
    if i is not None:
       app.instrument = app.instrumentIndex[i]
       app.sound.play()
    
def clickInSquare(app, mouseX, mouseY):     
    for i in range(len(app.instrumentLeftTop)):
        left, top = app.instrumentLeftTop[i]
        if (left <= mouseX <= left + app.instrumentWidth and
            top <= mouseY <= top + app.instrumentHeight): 
                return i
    return None


def onStep(app):
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

    
    if len(app.pointsToDraw) == 21:    
        if Do(app.pointsToDraw):
            app.note = 'Do'
        elif Re(app.pointsToDraw):
            app.note = 'Re'
        elif Mi(app.pointsToDraw):
            app.note = 'Mi'
        elif Fa(app.pointsToDraw):
            app.note = 'Fa'
        elif Sol(app.pointsToDraw):
            app.note = 'Sol'
        elif La(app.pointsToDraw):
            app.note = 'La'
        elif Ti(app.pointsToDraw):
            app.note = 'Ti'
        else:
            app.note = None

        
runApp()