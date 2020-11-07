from cmu_112_graphics import *
from image import fetchTestImage
from midiutil import MIDIFile

def appStarted(app):
    app.L = fetchTestImage()[1]
    app.tonic = "C#"
    app.tonality = "Major"
    app.tempo = 60
    app.numBeats = 4
    app.tonicRow = findTonicRow(app)
    app.rectangleHeight =  int(len(app.L)/96)
    app.standardRectangleWidth = int(app.width/100)
    app.tonicDict = {"C":24, "C#":25, "D":26, "D#":27, "E":28, "F":29, "F#":30, "G":31, "G#":32, "A":33, "A#":34, "B":35}
    app.currentMidi = pixelToMidi(app)
    createMidiFile(app)



def timerFired(app):
    pass

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
    for row in range(len(midiRectangles)):
        for col in range(len(midiRectangles[0])):
            note = rowNumToMidiNoteNum(app, row)
            box = midiRectangles[row][col]
            box[2] = (midiRectangleIntersect(app, box[0], box[1])) and (note in createDiatonicNotes(app))
    return midiRectangles

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
    row = int((len(app.L) - yCoord)/app.rectangleHeight)
    result = rowNumToMidiNoteNum(app, row)
    return result

def rowNumToMidiNoteNum(app, rowNum):
    octave = (rowNum // 12)
    pitch = ((rowNum - app.tonicRow) + app.tonicDict[app.tonic]) % 12
    note = 12*octave + pitch
    return note

def rowNumToMidiNoteNum(app, rowNum):
    shiftFactor = (app.tonicRow - app.tonicDict[app.tonic]) % 12
    result = 24  + rowNum + shiftFactor
    return result


def createMidiFile(app):
    degrees  = [60, 62, 64, 65, 67, 69, 71, 72]  # MIDI note number
    track    = 0
    channel  = 0
    time = 0
    tempo    = app.tempo  # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

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
    for row in app.currentMidi:
        for box in row:
            if not box[2]:
                canvas.create_rectangle(box[0], box[1], box[0] + app.standardRectangleWidth, box[1] + app.rectangleHeight, fill = "gray")
    midiToDraw = concatenatedMidi(app)
    for midiPair in midiToDraw:
        canvas.create_rectangle(midiPair[0], midiPair[1], midiPair[0] + midiPair[2], midiPair[1] + app.rectangleHeight, fill = "lightgreen", outline = "black")
def redrawAll(app, canvas):
    drawMidi(canvas, app)

def keyPressed(app, event):
    pass

def mousePressed(app, event):
    pass


def createDiatonicNotes(app):
    tonalityDict = {"Major":[2, 2, 1, 2, 2, 2, 1], "Minor":[2, 1, 2, 2, 1, 3, 1]}
    start = app.tonicDict[app.tonic]
    result = [start]
    for octave in range(16):
        for num in tonalityDict[app.tonality]:
            result.append(result[-1] + num)
            result.insert(0, result[0] - num)
    return result

#return True if the list is active in the box
def midiRectangleIntersect(app, x, y):
    for row in range(y, y + app.rectangleHeight):
        for col in range(x, x + app.standardRectangleWidth):
            if app.L[row][col]:
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