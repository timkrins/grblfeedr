'''
This is a grbl pre-processor.

Most code by Tim Krins

The anti-alias PIL code was modified from someone else whom I forgot. Oops.

'''


import re
import string
import math
import time
import random
import os
from PIL import Image, ImageDraw, ImageFont
import PIL

loadfile = "demo"

modtime = time.localtime(os.path.getmtime(__file__))
createtime = time.localtime(os.path.getctime(__file__))
filetime = time.gmtime((time.mktime(modtime) - time.mktime(createtime)))
filz = time.strftime("%d.%H.%M.%S", modtime)
print filz
filename = "pic." + loadfile + "." + filz + ".png"
savefile = 'convert.' + loadfile + "." + filz + '.html'
black = (0, 0, 0, 255)
blue = (0,0,255,100)
green = (0,255,0,200)
white = (255, 255, 255, 255)

loadfile = loadfile + ".nc"

isoAngle = 30
isoHeight = 0.5

def plot(draw, img, x, y, c, col,steep):
    ''' this is part of the anti-aliased line drawing module '''
    if steep:
        x,y = y,x
    if x < img.size[0] and y < img.size[1] and x >= 0 and y >= 0:
        c = c * (float(col[3])/255.0)
        p = img.getpixel((x,y))
        draw.point((int(x),int(y)),fill=(int((p[0]*(1-c)) + col[0]*c), int((p[1]*(1-c)) + col[1]*c), int((p[2]*(1-c)) + col[2]*c),255))
        #draw around the point
        draw.point((int(x)-1,int(y)-1),fill=(int((p[0]*(1-c)) + col[0]*c), int((p[1]*(1-c)) + col[1]*c), int((p[2]*(1-c)) + col[2]*c),255))
        draw.point((int(x)+1,int(y)+1),fill=(int((p[0]*(1-c)) + col[0]*c), int((p[1]*(1-c)) + col[1]*c), int((p[2]*(1-c)) + col[2]*c),255))
        draw.point((int(x)-1,int(y)+1),fill=(int((p[0]*(1-c)) + col[0]*c), int((p[1]*(1-c)) + col[1]*c), int((p[2]*(1-c)) + col[2]*c),255))
        draw.point((int(x)+1,int(y)-1),fill=(int((p[0]*(1-c)) + col[0]*c), int((p[1]*(1-c)) + col[1]*c), int((p[2]*(1-c)) + col[2]*c),255))


def iround(x):
    ''' this is part of the anti-aliased line drawing module '''
    return ipart(x + 0.5)

def ipart(x):
    ''' this is part of the anti-aliased line drawing module '''
    return math.floor(x)

def fpart(x):
    ''' this is part of the anti-aliased line drawing module '''
    return x-math.floor(x)

def rfpart(x):
    ''' this is part of the anti-aliased line drawing module '''
    return 1 - fpart(x)

def drawliner(draw, img, (x1, y1, x2, y2), col):
    ''' this is part of the anti-aliased line drawing module '''

    dx = x2 - x1
    dy = y2 - y1

    steep = abs(dx) < abs(dy)
    if steep:
        x1,y1=y1,x1
        x2,y2=y2,x2
        dx,dy=dy,dx
    if x2 < x1:
        x1,x2=x2,x1
        y1,y2=y2,y1
    try:
        gradient = float(dy) / float(dx)
    except:
        return None

    #handle first endpoint
    xend = round(x1)
    yend = y1 + gradient * (xend - x1)
    xgap = rfpart(x1 + 0.5)
    xpxl1 = xend    #this will be used in the main loop
    ypxl1 = ipart(yend)
    plot(draw, img, xpxl1, ypxl1, rfpart(yend) * xgap,col, steep)
    plot(draw, img, xpxl1, ypxl1 + 1, fpart(yend) * xgap,col, steep)
    intery = yend + gradient # first y-intersection for the main loop

    #handle second endpoint
    xend = round(x2)
    yend = y2 + gradient * (xend - x2)
    xgap = fpart(x2 + 0.5)
    xpxl2 = xend    # this will be used in the main loop
    ypxl2 = ipart (yend)
    plot (draw, img, xpxl2, ypxl2, rfpart (yend) * xgap,col, steep)
    plot (draw, img, xpxl2, ypxl2 + 1, fpart (yend) * xgap,col, steep)

    #main loop
    for x in range(int(xpxl1 + 1), int(xpxl2 )):
        plot (draw, img, x, ipart (intery), rfpart (intery),col, steep)
        plot (draw, img, x, ipart (intery) + 1, fpart (intery),col, steep)
        intery = intery + gradient

startHTML ='\
<html>\
<head>\
<style type="text/css">\
body\
{\
margin: 30px;\
font-family: Arial;\
background-image:url(' + filename + ');\
background-repeat:no-repeat;\
background-attachment:fixed;\
background-position:90% 30%;\
margin-right:200px;\
}\
</style>\
<title>grblfeedr 1.0: ' + loadfile + '</title>\
</head>\
'

validcommands = dict({
                           'G':'GCode',
                           'M':'MachineOp',
                           'T':'Toolchange'
                     })
validvalues = dict({
                          'X':'XPos',
                          'Y':'YPos',
                          'Z':'ZPos',
                          'F':'Feedrate',
                          'I':'IPos',
                          'J':'JPos',
                          'R':'Radius',
                          'P':'Pausetime'
})
validg = dict({
                           0:'FastMove',
                           1:'LinearMove',
                           2:'ClockwiseArc',
                           3:'CounterClockwiseArc',
                           4:'Dwell',
                           17:'SelectPlane1',
                           18:'SelectPlane2',
                           19:'SelectPlane3',
                           20:'InchesMode',
                           21:'mmMode',
                           28:'Home',
                           30:'Home',
                           53:'Absolute',
                           80:'Cancel',
                           90:'Absolute',
                           91:'Relative',
                           93:'InverseFeed',
                           94:'NormalFeed'
})
validm = dict({
                            0:'Stop', 
                            1:'OptionalStop', 
                            2:'EndOfProgram', 
                            3:'SpindleOnClockwise', 
                            4:'SpindleOnCounterClockwise', 
                            5:'SpindleOff',
                            30:'EndOfProgram',
                            60:'EndOfProgram',
                            99:'ResetAxes'
})

timeVal = time.strftime("%d/%m/%Y %H:%M:%S")
headerText = loadfile + ", processed " + timeVal + " by grblfeedr 0." + filz

def makeHTML(parsedFileArray, adjust):
    ''' This module creates a HTML file using the parsed file and an adjustment. '''
    ''' Usage: makeHTML( Parsed file [array] , adjust values [tuple]) '''

    madeHTMLArray = []
    madeHTMLArray.append(startHTML)
    
    madeHTMLArray.append("<b>( " + headerText + " )</b><br><br>")
    for lineitem in parsedFileArray:
        builtLineHTML = buildLineHTML(lineitem, adjust)
        madeHTMLArray.append(''.join(builtLineHTML)+'<br>')
    madeHTMLArray.append('</html>')
    madeHTML = '\n'.join(madeHTMLArray)
    return madeHTML

def makeArray(parsedFileArray, adjust = [0,0,0]):
    ''' Create an array of values from the input file '''
    ''' Usage: makeArray( Parsed file [array] , adjust value [tuple] ) '''
    
    processedFile = []
    linenumber = 0
    for item in parsedFileArray:
        processedLine = processLine(item, adjust, linenumber)
        linenumber+= 1
        for part in processedLine:
            processedFile.append(part)
    return processedFile

def sendFile(parsedFileArray, adjust = [0,0,0]):
    ''' Creates an array ready to be sent to the grbl device (unformatted) '''
    ''' Usage: sendFile( Parsed file [array] , adjust value [tuple] ) '''
    
    sendFileArray = []
    for lineitem in parsedFileArray:
        builtLine = buildLine(lineitem, adjust)
        sendFileArray.append(' '.join(builtLine))
    return sendFileArray
    
def parseFileArray(file):
    ''' Takes the file and makes it into an array '''
    ''' Usage: parseFileArray( Input file [file] ) '''
    
    parsedFileArray = []
    for line in file:
        parsedFileArray.append(line.upper())
    return parsedFileArray
    
def buildLine(line, adjust):
    ''' Builds a line that can be read by grbl '''
    ''' Usage: buildLine ( line [string] , adjust values [tuple] ) '''

    builtLine = []
    processedLine = processLine(line, adjust)
    for i in range(0,len(processedLine)):
        try:
            builtLine.append(processedLine[i][0]+processedLine[i][1])
        except:
            None
    return builtLine
    
def buildLineHTML(line, adjust):
    ''' Builds a line into a HTML line to be displayed on the computer '''
    ''' Usage: buildLineHTML ( line [string] , adjust values [tuple] ) '''
    
    builtLine = []
    commentsLine = []
    builtLineHTML = None
    processedLine = processLine(line, adjust)
    for i in range(0,len(processedLine)):
        if processedLine[i][0]:
            try:
                builtLine.append("<i>" + processedLine[i][1] + str(max(x for x in processedLine[i][3:11] if x is not None)) + "</i>")
            except:
                None
            try:
                commentsLine.append(processedLine[i][11])
            except:
                None
        else:
            try:
                builtLine.append("<b>" + processedLine[i][1]+processedLine[i][2] + "</b>")
            except:
                None
            try:
                commentsLine.append(processedLine[i][11])
            except:
                None
    if not(commentsLine):
        commentsLine.append("BlankLine")
    builtLineHTML = ['<font color=black>'] + builtLine + ['</font><font color=blue size=-2>('] + commentsLine + [')</font>']
    return builtLineHTML
    
def processLine(line, adjust, linenumber = None):
    ''' Process the line and find the parts that grbl can read '''
    ''' Usage: processLine( line [string] , adjust values [tuple] , line number [int] ) '''
    
    processedLine = []
    lastcommand = None
    possibles = 'G[\s\d][\s\d]|M[\s\d][\s\d]|T[\s\d][\s\d]|[X|Y|Z|F|I|J|R|P][-|\d|\.]+'
    #findcomments = re.findall("\((.*?)\)", line)
    nocomments = re.sub("\((.*?)\)", "", line)
    findcode = re.findall(possibles, nocomments)
    findnotcode = re.sub(possibles, "", nocomments)
    if findcode:
        for code in findcode:
            processedIndividual = processIndividual(code, adjust, lastcommand)
            processedIndividual = processedIndividual + (linenumber,)
            processedLine.append(processedIndividual)
            lastcommand = processedIndividual[13]
    else:
        processedLine.append((False,None,None,None,None,None,None,None,None,None,None,'Blank',None, None, linenumber))
    return processedLine

def processIndividual(code, adjust, lastcommand):
    ''' Processes an individual match of the regex search '''
    ''' Usage: processIndividual( matched code [string] , adjust value [tuple] , lastcommand [string] ) '''\
    
    gchar = gint = None
    color = None
    xadjust = adjust[0]
    yadjust = adjust[1]
    zadjust = adjust[2]
    xfloat = yfloat = zfloat = None
    ffloat = ifloat = jfloat = None
    rfloat = pfloat = descriptor = None
    gchar = code[0:1]
    gint = code[1:]
    if gchar in validvalues:
        valueCode = True
        try:
            if lastcommand == 'G0':
                color = green
            elif lastcommand == 'G1':
                color = blue
        except:
            color = None
        if gchar == "X":xfloat = float(float(gint) + float(xadjust))
        if gchar == "Y":yfloat = float(float(gint) + float(yadjust))
        if gchar == "Z":zfloat = float(float(gint) + float(zadjust))
        if gchar == "F":ffloat = float(gint)
        if gchar == "I":ifloat = float(gint)
        if gchar == "J":jfloat = float(gint)
        if gchar == "R":rfloat = float(gint)
        if gchar == "P":pfloat = float(gint)
        descriptor = gchar + 'Val'
    elif gchar in validcommands:
        valueCode = False
        if (gchar == 'G' and int(gint) in validg):
            descriptor = 'GCode' + validg[int(gint)]
            lastcommand = 'G'+ str(int(gint))
        elif (gchar == 'M' and int(gint) in validm):
            descriptor = 'MCode'+ validm[int(gint)]
            lascommand = None
        elif gchar == 'T':
            descriptor = 'ToolCode'
            lastcommand = None
        else:
            descriptor = 'UnrecognisedCode' + gchar + str(int(gint))
            gchar = None
    else:
        gchar = None
        descriptor = 'Nothing was recognised'
    return (valueCode,gchar,gint,xfloat,yfloat,zfloat,ffloat,ifloat,jfloat,rfloat,pfloat,descriptor,color,lastcommand) # make this a dict

def mm(madeArray):
    ''' Calculates minimum and maximum values of the array '''
    ''' Usage: mm( values [array] ) '''
    
    #start them all at zero.
    XVals = [(0)]
    YVals = [(0)]
    ZVals = [(0)]
    FVals = []
    for item in madeArray:
        try:
            XVals.append(float(item[3])) ## Might want to return a dict instead, later, for simplicitys sake
        except:
            None
        try:
            YVals.append(float(item[4]))
        except:
            None
        try:
            ZVals.append(float(item[5]))
        except:
            None
        try:
            FVals.append(float(item[6]))
        except:
            None
    minMax = ({
              'XMin':float(min(x for x in XVals if x is not None)),
              'XMax':float(max(x for x in XVals if x is not None)),
              'YMin':float(min(x for x in YVals if x is not None)),
              'YMax':float(max(x for x in YVals if x is not None)),
              'ZMin':float(min(x for x in ZVals if x is not None)),
              'ZMax':float(max(x for x in ZVals if x is not None)),
              'FMin':float(min(f for f in FVals if f is not None)),
              'FMax':float(max(f for f in FVals if f is not None))
              })
    return minMax

def drawPicture(draw, image, madeCoord, multiply, isoMin, isoMax, adjust = None):
    ''' Draws an isometric representation of the toolpath '''
    ''' Usage: drawPicture( draw [PIL image] , image [PIL image] , coordinates [tuple], multiplier [int], min isometric vals [array], max iso vals [array], adjust values [tuple] ) '''
    
    isoAdjust = ((0-isoMin[0])*multiply, (0-isoMin[1])*multiply)
    adjust = isoAdjust
    try:
        lastval
    except:
        lastval = ((madeCoord[0][0]*multiply)+adjust[0]),((madeCoord[0][1]*multiply)+adjust[1])
        madeCoord.pop(0)
    for item in madeCoord:
        if (item[0] or item[1]):
            if item[2] is not None:
                colour = item[2]
                colour = (colour[0],colour[1],colour[2],colour[3])
            else:
                colour = black
            nextval = ((item[0]*multiply)+adjust[0]),((item[1]*multiply)+adjust[1])
            lastval = drawLine(
                               draw,
                               image,
                               (lastval[0], lastval[1]),
                               (nextval[0], nextval[1]),
                               colour
                               )
    
def createCanvas(imageSize):
    ''' Creates a PIL canvas to be drawn on '''
    ''' Usage: createCanvas ( image size [array] ) '''
    
    width = imageSize[0]
    height = imageSize[1]
    image = Image.new("RGB", (width, height), white)
    draw = PIL.ImageDraw.Draw(image)
    return (image, draw)

def drawLine(draw, image, first, second, colour):
    ''' Draws a line '''
    ''' Usage: drawLine ( draw [PIL image], image [PIL image] , first coord [array], second coord [array], color [tuple] ) '''
    
    x1 = float(first[0])
    y1 = float(first[1])
    x2 = float(second[0])
    y2 = float(second[1])
    drawliner(draw, image, (x1, y1, x2, y2), colour)
    return second
    
def makeCoords(madeArray, adjust):
    ''' Makes a 2D array of isometric coordinates for drawing '''
    ''' Usage: makeCoords ( 3D corrdinates [array], adjust values [tuple] ) '''
    
    makeLists = []
    XVal = 0
    YVal = 0
    ZVal = 0
    linenumber = -1
    color = None
    for item in madeArray:
        if (item[3] is not None) and (item[3] != XVal):
            XVal = float(item[3])
            color = item[12]
        if (item[4] is not None) and (item[4] != YVal):
            YVal = float(item[4])
            color = item[12]
        if (item[5] is not None) and (item[5] != ZVal):
            ZVal = float(item[5])
            color = item[12]
        if (item[12] is not None) and (item[12] != color):
            color = item[12]
        if linenumber is not item[14]:
                makeLists.append([float(XVal) + float(adjust[0]),float(YVal) + float(adjust[1]), float(ZVal) + float(adjust[2]), color, linenumber])
                linenumber = item[14]
                
    return makeLists
    
def findMin(array):
    xval = []
    yval = []
    for item in array:
        if(item[0]):
            xval.append(item[0])
        if(item[1]):
            yval.append(item[1])
    return (min(xval),min(yval))
    
def findMax(array):
    xval = []
    yval = []
    for item in array:
        if(item[0]):
            xval.append(item[0])
        if(item[1]):
            yval.append(item[1])
    return (max(xval),max(yval))
   
def makeIsometric(coords):
    xc1 = 0-(coords[0]*math.cos(math.radians(isoAngle)))
    yc1 = 0-(coords[0]*math.sin(math.radians(isoAngle)))
    
    xc2 = coords[1]*math.cos(math.radians(isoAngle))
    yc2 = 0-(coords[1]*math.sin(math.radians(isoAngle)))
    
    xc3 = 0
    yc3 = 0-(coords[2]*isoHeight)
    x = xc1 + xc2 + xc3
    y = yc1 + yc2 + yc3

    x = 0-x #flip
    color = coords[3]
    return (x,y,color)

def makeIsometricArray(threeDimension):
    twoDimension = []
    for threeD in threeDimension:
        twoD = makeIsometric(threeD)
        twoDimension.append(twoD)
    return twoDimension

def findAdjust(minMaxVals):
    return (0-minMaxVals['XMin'],0-minMaxVals['YMin'],0-minMaxVals['ZMin'])
    
fLoad = open(loadfile, 'r')
fSave = open(savefile, 'w')
parsedFileArray = parseFileArray(fLoad)
madeArray = makeArray(parsedFileArray)
minMaxVals = mm(madeArray)
adjust = findAdjust(minMaxVals)
sentFile = sendFile(parsedFileArray, adjust)
madeHTML = makeHTML(parsedFileArray, adjust)

madeArray.append((False, 'G', '00', None, None, None, None, None, None, None, None, 'GCodeFastMove', None, 'G0', 50)) #add an extra
threeDimension = makeCoords(madeArray, adjust)
madeArray.pop() #remove the extra


## Determine the size of image
imageWidthMax = 800
imageHeightMax = 600

## Make two dimension array w colour
twoDimension = makeIsometricArray(threeDimension)

## Find the minimum and maximum values for the isometric picture
isoMin = findMin(twoDimension)
isoMax = findMax(twoDimension)

isoWidth = isoMax[0] - isoMin[0]
isoHeight = isoMax[1] - isoMin[1]
isoRatio = isoHeight / isoWidth

imageWidthCalc = int(imageWidthMax / isoRatio)
imageHeightCalc = int(isoRatio * imageHeightMax)
print (imageWidthCalc, imageHeightCalc)

if (imageWidthCalc > imageWidthMax):
    imageWidth = imageWidthMax
else:
    imageWidth = imageWidthCalc
    
if (imageHeightCalc > imageHeightMax):
    imageHeight = imageHeightMax
else:
    imageHeight = imageHeightCalc

imageSize = (imageWidth,imageHeight)
print imageSize

isoMultiplyWide = (imageWidth / isoWidth)
isoMultiplyHeight = (imageHeight / isoHeight)

isoMultiply = min(isoMultiplyWide, isoMultiplyHeight)
print isoMultiply

isoAdjust = (0-isoMin[0], 0-isoMin[1])

## Make the canvas
canvas = createCanvas(imageSize)
image = canvas[0]
draw = canvas[1]

## Draw the picture on the screen
drawPicture(draw, image, twoDimension, isoMultiply, isoMin, isoMax, isoAdjust)

## Draw text on the image
text = headerText
font = PIL.ImageFont.truetype("arial.ttf", 12)
fontsize = font.getsize(text)
draw.text((imageWidth-fontsize[0], imageHeight-fontsize[1]), text, font=font,fill=(255,0,0))

##  Save the picture.
image.save(filename)

# Save the HTML
fSave.write(madeHTML)
fLoad.close()
fSave.close()