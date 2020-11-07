from cmu_112_graphics import *
from image import fetchTestImage
from midiutil import MIDIFile
from midi2audio import FluidSynth


def appStarted(app):
    app.L = fetchTestImage()[1]
    app.tonic = "B"
    app.tonality = "Minor"
    app.tempo = 20
    app.numBeats = 4
    app.chordProgression = ["V", "i", "III+", "iv", "V", "i"]
    app.tonicRow = findTonicRow(app)
    app.rectangleHeight =  int(len(app.L)/96)
    app.standardRectangleWidth = int(app.width/100)
    app.tonicDict = {"C":24, "C#":25, "D":26, "D#":27, "E":28, "F":29, "F#":30, "G":31, "G#":32, "A":33, "A#":34, "B":35}
    app.majorChordDict = {"I":[4, 3, 5, 0], "ii":[3, 4, 5, 2], "iii":[3, 4, 5, 4], "IV":[4, 3, 5, 5], "V":[4, 3, 5, 7], "vi":[3, 4, 5, 9], "viio":[3, 3, 6, 11]}
    app.minorChordDict = {"i":[3, 4, 5, 0], "ii0":[3, 3, 6, 2], "III+":[4, 4, 4, 3], "iv":[3, 4, 5, 5], "V":[4, 3, 5, 7], "VI":[4, 3, 5, 8], "viio":[3, 3, 6, 11]}
    app.currentMidi = pixelToMidi(app)
    createMidiFile(app)
    createMidiToTestHowWeThinkThisShitWorks(app)
    playMidi(app)
 


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
    chordProgressionStepSize = len(midiRectangles[0])/(len(app.chordProgression))
    for row in range(len(midiRectangles)):        
        for col in range(len(midiRectangles[0])):
            chordProgressionIndex = int((col/len(midiRectangles[0])) * (len(app.chordProgression)))
            if chordProgressionIndex == len(app.chordProgression):
                chordProgressionIndex -= 1
            note = rowNumToMidiNoteNum(app, row)
            box = midiRectangles[row][col]
            box[2] = (midiRectangleIntersect(app, box[0], box[1])) and ((96  + 24 - note) in getNotesInChord(app, app.chordProgression[chordProgressionIndex]))
        chordProgressionIndex = 0
    return midiRectangles



def drawMarkerAndPiano(app, canvas):
    row = app.tonicRow
    tonic = app.tonic
    canvas.create_text(app.width/10, row, text = tonic, fill = "pink", font = "Arial 11 bold")

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
    return note - 12

def playMidi(app):
    FluidSynth().play_midi('ourMidi.mid')
    print("played midi")

def rowNumToMidiNoteNum(app, rowNum):
    shiftFactor = (app.tonicRow - app.tonicDict[app.tonic]) % 12
    result = 24  + rowNum + shiftFactor
    return result

def createMidiToTestHowWeThinkThisShitWorks(app):
    degrees  = getNotesInChord(app, "V") # MIDI note number
    track    = 0
    channel  = 0
    time     = 0    # In beats
    duration = 1    # In beats
    tempo    = 60   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                      # automatically)
    MyMIDI.addTempo(track, time, tempo)

    for i, pitch in enumerate(degrees):
      MyMIDI.addNote(track, channel, pitch, time + i, duration, volume)

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
    for row in range(len(app.currentMidi)):
        for box in app.currentMidi[row]:
            if not box[2]:
                canvas.create_rectangle(box[0], box[1], box[0] + app.standardRectangleWidth, box[1] + app.rectangleHeight, fill = "gray")
    midiToDraw = concatenatedMidi(app)
    for midiPair in midiToDraw:
        canvas.create_rectangle(midiPair[0], midiPair[1], midiPair[0] + midiPair[2], midiPair[1] + app.rectangleHeight, fill = "lightgreen", outline = "black")
def redrawAll(app, canvas):
    drawMidi(canvas, app)
    drawMarkerAndPiano(app, canvas)

def keyPressed(app, event):
    pass

def mousePressed(app, event):
    pass


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