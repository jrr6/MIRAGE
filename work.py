from PIL import ImageTk, Image
from cmu_112_graphics import *
from image_analyzer import getImageData
from midiutil import MIDIFile
from midi2audio import FluidSynth
from threading import Thread
import time


def appStarted(app):
    app.timerDelay = 100
    app.beginTime = 0
    app.lineX = 0
    app.numBeats = 12
    app.moveLine = False
    app.tonicDict = {"C":24, "C#":25, "D":26, "D#":27, "E":28, "F":29, "F#":30, "G":31, "G#":32, "A":33, "A#":34, "B":35}
    app.majorChordDict = {"I":[4, 3, 5, 0], "i":[3, 4, 5, 0], "iio":[3, 3, 6, 2],"ii":[3, 4, 5, 2], "II":[4, 3, 5, 2], "III+":[4, 4, 4, 4],"iii":[3, 4, 5, 4], "III":[5, 4, 5, 4], "IV":[4, 3, 5, 5], "iv":[3, 4, 5, 5], "V":[4, 3, 5, 7], "v":[3, 4, 5, 7], "vi":[3, 4, 5, 9], "VI":[4, 3, 5, 9], "viio":[3, 3, 6, 11], "IM7":[4, 3, 4, 1, 0], "Im7":[3, 4, 3, 2, 0], "IMm7":[4, 3, 3, 2, 0], "IIM7":[4, 3, 4, 1, 2], "IIm7":[3, 4, 3, 2, 2], "IIMm7":[4, 3, 3, 2, 2], "IIIM7":[4, 3, 4, 1, 4], "IIIm7":[3, 4, 3, 2, 4], "IIIMm7":[4, 3, 3, 2, 4], "IVM7":[4, 3, 4, 1, 5], "IVm7":[3, 4, 3, 2, 5], "IVMm7":[4, 3, 3, 2, 5], "VM7":[4, 3, 4, 1, 7], "Vm7":[3, 4, 3, 2, 7], "VMm7":[4, 3, 3, 2, 7], "VIM7":[4, 3, 4, 1, 9], "VIm7":[3, 4, 3, 2, 9], "VIMm7":[4, 3, 3, 2, 9] ,  "VIIM7":[4, 3, 4, 1, 11], "VIIm7":[3, 4, 3, 2, 11], "VIIMm7":[4, 3, 3, 2, 11]}
    app.minorChordDict = {"i":[3, 4, 5, 0],"I":[4, 3, 5, 0], "iio":[3, 3, 6, 2], "II":[4, 3, 5, 2], "ii":[3, 4, 5, 2],"III+":[4, 4, 4, 3], "iii":[3, 4, 5, 3], "III":[4, 3, 5, 3],"iv":[3, 4, 5, 5],"IV":[4, 3, 5, 5], "V":[4, 3, 5, 7],"v":[3, 4, 5, 7], "VI":[4, 3, 5, 8], "vi":[3, 4, 5, 8], "viio":[3, 3, 6, 11],"IM7":[4, 3, 4, 1, 0], "Im7":[3, 4, 3, 2, 0], "IMm7":[4, 3, 3, 2, 0], "IIM7":[4, 3, 4, 1, 2], "IIm7":[3, 4, 3, 2, 2], "IIMm7":[4, 3, 3, 2, 2], "IIIM7":[4, 3, 4, 1, 3], "IIIm7":[3, 4, 3, 2, 3], "IIIMm7":[4, 3, 3, 2, 3], "IVM7":[4, 3, 4, 1, 5], "IVm7":[3, 4, 3, 2, 5], "IVMm7":[4, 3, 3, 2, 5], "VM7":[4, 3, 4, 1, 7], "Vm7":[3, 4, 3, 2, 7], "VMm7":[4, 3, 3, 2, 7], "VIM7":[4, 3, 4, 1, 8], "VIm7":[3, 4, 3, 2, 8], "VIMm7":[4, 3, 3, 2, 8] ,  "VIIM7":[4, 3, 4, 1, 10], "VIIm7":[3, 4, 3, 2, 10], "VIIMm7":[4, 3, 3, 2, 10]}
    app.topMargin = app.height/5
    app.mouseOverPlayButton = False
    app.isPlayingAudio = False
    app.uploaded = False
    app.loading = False
    app.loadingPercent = 0

def onUpload(app):
    filename = filedialog.askopenfile()
    loaderThread = Thread(target=doImageProc, args=(app, filename.name))
    loaderThread.start()
    app.loading = True

def doImageProc(app, name):
    data = getImageData(name, updateLoader(app))
    app.L = data['edges']
    app.sideMargin = (app.width - len(app.L[0])) / 2
    app.tonic = data['tonic']
    app.tonality = "Major" if data['major'] else "Minor"
    app.tempo = data['tempo']
    app.chordProgression = data['chords']
    app.tonicRow = findTonicRow(app)
    app.rectangleHeight = int(len(app.L) / 96)
    app.standardRectangleWidth = int(app.width / 100)
    app.currentMidi = pixelToMidi(app)
    createMidiFile(app)
    calculateLineSpeed(app)
    app.concatenatedMidi = concatenatedMidi(app)
    app.uploaded = True
    app.loading = False

# CURRYING! YAY!
def updateLoader(app):
    def func(value):
        app.loadingPercent = value
    return func

def calculateLineSpeed(app):
    pixelsPerBeat = len(app.L[0])/(app.numBeats)
    pixelsPerMilisecond = ((app.tempo/60)/1000) * pixelsPerBeat
    app.lineSpeed = 3*app.timerDelay * pixelsPerMilisecond
 
#from course website
def rgbColorString(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

def mouseMoved(app, event):
    if app.uploaded:
        app.mouseOverPlayButton = isPositionInsidePlayButton(app, event.x, event.y)
    else:
        app.mouseOverUploadButton = isPositionInsideUploadButton(app, event.x, event.y)

def mousePressed(app, event):
    if not app.isPlayingAudio and app.uploaded and isPositionInsidePlayButton(app, event.x, event.y):
        app.isPlayingAudio = True
        app.beginTime = time.time()
        playThread = Thread(target=playMidi, args=(app, 0))
        playThread.start()
    if not app.uploaded and not app.loading and isPositionInsideUploadButton(app, event.x, event.y):
        onUpload(app)

def timerFired(app):
    if app.isPlayingAudio:
        app.lineX += app.lineSpeed
        if app.lineX > app.sideMargin + len(app.L):
            app.lineX = 0
            app.isPlayingAudio = False

def pixelToMidi(app):
    midiRectangles = []
    #setup midiRectangles ------------------
    y = 0
    while y < len(app.L):
        x = 0
        midiRectangles.append([])
        while x < len(app.L[0]):   
            midiRectangles[-1].append([x, y, False])
            x += app.standardRectangleWidth
        y += app.rectangleHeight
    #---------------------------------------
    tonicRow = findTonicRow(app)
    chordProgressionStepSize = len(midiRectangles[0])/(len(app.chordProgression))
    for row in range(len(midiRectangles)):        
        for col in range(len(midiRectangles[0])):
            chordProgressionIndex = int((col/len(midiRectangles[0])) * (len(app.chordProgression)))
            if chordProgressionIndex == len(app.chordProgression):
                chordProgressionIndex -= 1
            note = rowNumToMidiNoteNum(app, row)
            box = midiRectangles[row][col]
            box[2] = (midiRectangleIntersect(app, box[0], box[1])) and ((note) in getNotesInChord(app, app.chordProgression[chordProgressionIndex]))
        chordProgressionIndex = 0
    return midiRectangles

def isPositionInsidePlayButton(app, x, y):
    halfWidth = app.width/22
    halfHeight = app.height/30
    topLeftX = app.width/2 - halfWidth
    topLeftY = app.height - (app.height - app.topMargin - len(app.L))/2 - halfHeight
    bottomRightX = app.width/2 + halfWidth
    bottomRightY = app.height - (app.height - app.topMargin - len(app.L))/2 + halfHeight
    if x >= topLeftX and x <= bottomRightX and y >= topLeftY and y <= bottomRightY:
        return True
    return False

def isPositionInsideUploadButton(app, x, y):
    return (app.width // 2 - 100 <= x <= app.width // 2 + 100
            and app.height // 2 - 50 <= y <= app.height // 2 + 50)

def drawPlayButton(app, canvas):
    halfWidth = app.width/22
    halfHeight = app.height/30
    topLeftX = app.width/2 - halfWidth
    topLeftY = app.height - (app.height - app.topMargin - len(app.L))/2 - halfHeight
    bottomRightX = app.width/2 + halfWidth
    bottomRightY = app.height - (app.height - app.topMargin - len(app.L))/2 + halfHeight
    color = "limegreen"
    if app.mouseOverPlayButton:
        color = "green"
    if app.isPlayingAudio:
        color = "gray"
    canvas.create_rectangle(topLeftX, topLeftY, bottomRightX, bottomRightY, fill = color)
    # canvas.create_rectangle(topLeftX + halfWidth*3, topLeftY, bottomRightX + halfWidth*3, bottomRightY, fill='red')
    # canvas.create_text(topLeftX + halfWidth*4, (topLeftY + bottomRightY) // 2, text='Reset', font='Helvetica 12 bold', fill='white')


def drawTriangleAbovePlayButton(app, canvas):
    halfWidth = app.width/33
    halfHeight = app.height/40
    topLeftX = app.width/2 - halfWidth
    topLeftY = app.height - (app.height - app.topMargin - len(app.L))/2 - halfHeight
    bottomRightX = app.width/2 + halfWidth
    bottomRightY = app.height - (app.height - app.topMargin - len(app.L))/2 + halfHeight
    
    margin = halfWidth/2
    topMargin = halfHeight/5

    canvas.create_polygon(topLeftX + margin,topLeftY + topMargin, topLeftX + margin, topLeftY + 2*halfHeight - topMargin, topLeftX + 2*halfWidth - margin/2, bottomRightY - halfHeight, fill = "gray" )

def drawMarkerAndPiano(app, canvas):
    row = app.tonicRow
    tonic = app.tonic
    

def concatenatedMidi(app):
    concatenatedMidi = []
    for row in range(len(app.currentMidi)):
        rowList = app.currentMidi[row]
        currentPosition = 0
        while currentPosition < len(rowList):
            length = app.standardRectangleWidth
            x, y = None, None
            while app.currentMidi[row][currentPosition][2]:
                if length == app.standardRectangleWidth:
                    x, y = app.currentMidi[row][currentPosition][0], app.currentMidi[row][currentPosition][1]
                    length += app.standardRectangleWidth
                else:
                    length += app.standardRectangleWidth
                currentPosition += 1
                if currentPosition >= len(app.currentMidi[row]):
                    break
            if x != None and y != None:
                concatenatedMidi.append([x, y, length - app.standardRectangleWidth])
            currentPosition += 1  

    return concatenatedMidi

def getPitchForY(app, yCoord):
    row = int(yCoord/app.rectangleHeight)
    result = rowNumToMidiNoteNum(app, row)
    return result

def rowNumToMidiNoteNum(app, rowNum):
    octave = (rowNum // 12)
    pitch = ((rowNum - app.tonicRow) + app.tonicDict[app.tonic]) % 12
    note = 12*octave + pitch
    return note - 12

def playMidi(app, bogus):
    FluidSynth().play_midi('ourMidi.mid')

def rowNumToMidiNoteNum(app, rowNum):
    rowNum = 96 - rowNum
    shiftFactor = (app.tonicRow - app.tonicDict[app.tonic]) % 12
    result = 24  + rowNum + shiftFactor
    return result

def createMidiToTest(app):
    degrees  = getNotesInChord(app, "V") # MIDI note number
    track    = 0
    channel  = 0
    time     = 0    # In beats
    duration = 1    # In beats
    tempo    = 20   # In BPM
    volume   = 25  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                      # automatically)
    MyMIDI.addTempo(track, time, tempo)

    for i, pitch in enumerate(degrees):
      MyMIDI.addNote(track, channel, pitch , time + i, duration, volume)

    with open("test.mid", "wb") as output_file:
        MyMIDI.writeFile(output_file)



def createMidiFile(app):
    degrees  = [60, 62, 64, 65, 67, 69, 71, 72]  # MIDI note number
    track    = 0
    channel  = 0
    time = 0
    tempo    = app.tempo  # In BPM
    volume   = 50  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                      # automatically)
    MyMIDI.addTempo(track, time, tempo)
    for midiNote in concatenatedMidi(app):
        time = ((midiNote[0])/len(app.L[0])) * ((app.numBeats))
        duration = ((midiNote[2])/len(app.L[0])) * ((app.numBeats))
        note = getPitchForY(app, midiNote[1])
        MyMIDI.addNote(track, channel, note , time , duration, volume)

    with open("ourMidi.mid", "wb") as output_file:
        MyMIDI.writeFile(output_file)
    

def drawMidi(canvas, app):
    extent = 7

    canvas.create_rectangle(0, 0, app.width, app.height, fill = rgbColorString(50, 50, 50))
    canvas.create_rectangle(0, app.topMargin - extent, app.width, app.topMargin + len(app.L) + extent, fill = "black")

    img = ImageTk.PhotoImage(Image.open('logo_dark.jpg'))
    canvas.create_image((app.width // 2, app.height // 2 + 300), image=img)

    for row in range(len(app.currentMidi)):
        for box in app.currentMidi[row]:
            if not box[2]:
                canvas.create_rectangle(box[0] + app.sideMargin, box[1] + app.topMargin, box[0] + app.standardRectangleWidth + app.sideMargin, box[1] + app.rectangleHeight + app.topMargin, fill = "gray")
    midiToDraw = app.concatenatedMidi
    for midiPair in midiToDraw:
        canvas.create_rectangle(midiPair[0] + app.sideMargin, midiPair[1] + app.topMargin, midiPair[0] + midiPair[2] + app.sideMargin, midiPair[1] + app.rectangleHeight + app.topMargin, fill = "lightgreen", outline = "black")

def drawUploader(app, canvas):
    buttonWidth = 100
    img = ImageTk.PhotoImage(Image.open('logo.jpg'))
    canvas.create_image((app.width // 2, app.height // 2 - 200), image=img)
    if not app.loading:
        canvas.create_rectangle(app.width // 2 - buttonWidth,
                                app.height // 2 - buttonWidth / 2,
                                app.width // 2 + buttonWidth,
                                app.height // 2 + buttonWidth / 2, fill='lightgreen')
        canvas.create_text(app.width // 2, app.height // 2, text='Select Image', font='Helvetica 16 bold', fill='white')
        canvas.create_text(app.width // 2, app.height // 2 + 200, text='Created by Cameron Chiu, Joseph Rotella, Matthew Suh, and Zack Sussman',
                           font='Helvetica 12 bold', fill='black')
    else:
        img = ImageTk.PhotoImage(Image.open('logo.jpg'))
        canvas.create_image((app.width // 2, app.height // 2 - 200), image=img)
        # loading bar outline
        canvas.create_rectangle(app.width // 2 - 201, app.height // 2 - 52, app.width // 2 + 201, app.height // 2 + 52, outline='black', width=3)
        quantity = -200 + app.loadingPercent * 400
        canvas.create_rectangle(app.width // 2 - 200, app.height // 2 - 50,
                                app.width // 2 + quantity, app.height // 2 + 50,
                                fill='lightgreen', outline='white', width=0)
        # canvas.create_text(app.width // 2, app.height // 2 + 300, text='Processing...', font='Helvetica 16 bold')


def redrawAll(app, canvas):
    if not app.uploaded:
        drawUploader(app, canvas)
    else:
        drawMidi(canvas, app)
        drawMarkerAndPiano(app, canvas)
        drawLine(app, canvas)
        drawPlayButton(app, canvas)
        drawTriangleAbovePlayButton(app, canvas)

def drawLine(app, canvas):
    canvas.create_line(app.lineX + app.sideMargin, app.topMargin, app.lineX + app.sideMargin, len(app.L) + app.topMargin, fill = "red", width = 2)

def keyPressed(app, event):
    if event.key == "Space" and not app.isPlayingAudio:
        app.isPlayingAudio = True
        app.beginTime = time.time()
        playThread = Thread(playMidi, (app, 0))
        playThread.start()
    elif event.key == 'r' and app.uploaded:
        appStarted(app)



def getNotesInChord(app, chord):
    chordDict = {}
    if app.tonality == "Major":
        chordDict = app.majorChordDict
    elif app.tonality == "Minor":
        chordDict = app.minorChordDict
    notes = chordDict[chord] + []
    startingNote = notes.pop()
    result = [(startingNote + app.tonicDict[app.tonic]) % 12]
    for octave in range(16):
        for num in notes:
            result.append(result[-1] + num)
    return result

def isNoteInScale(app, midiNoteNumber):
    scaleNumbers = []
    if app.tonality == "Major":
        scaleNumbers = [2, 2, 1, 2, 2, 2, 1]
    elif app.tonality == "Minor":
        scaleNumbers = [2, 1, 2, 2, 1, 3, 1]
    result = []
    result.append(app.tonicDict[app.tonic] % 12)
    for octave in range(16):
        for num in scaleNumbers:
            result.append(result[-1] + num)
    return midiNoteNumber in result

#return True if the list is active in the box
def midiRectangleIntersect(app, x, y):
    for row in range(y, y + app.rectangleHeight):
        for col in range(x, x + app.standardRectangleWidth):
            if col < len(app.L[0]) and row < len(app.L) and app.L[row][col]:
                return True
    return False


def findTonicRow(app):
    bestRow = 0
    bestCount = 0
    for row in range(len(app.L)):
        count = 0
        for num in app.L[row]:
            if num:
                count += 1
        if count > bestCount:
            bestCount = count
            bestRow = row
    return bestRow


runApp(width = 800, height = 800)
