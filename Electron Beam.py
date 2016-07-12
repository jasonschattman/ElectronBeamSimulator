############################################################################################################
#Title:  Electron Beam Simulator

#Purpose:  This program simulates an electron beam that is deflected by an electric charge as it flies towards an anode.
#                You can move the deflector charge using the mouse, and you can adjust the charge of the deflector
#                and the anode using slider bars.  The forces on the electrons are calculated using Coulomb's Law.
#                The forces then determine the acceleration and velocities of the electrons in each frame of the animation.

#Programmer:  J. Schattman 2016
############################################################################################################

from tkinter import *
from time import *
from math import *
root = Tk()
screen = Canvas( root, width = 1200, height = 900, background = "black" )

H = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]  #hexadecimal array used for colouring

def mouseClicked( event ):
    global mouseDown
    mouseDown = True
    

def mouseReleased( event ):
    global mouseDown
    mouseDown = False
 

def mouseMoved( event ):
    global xMouse, yMouse
    
    if mouseDown == True:
            xMouse = event.x
            yMouse = event.y


#Converts decimal number x to hexadecimal. Used for colouring
def convertDecimalToHex( x ):
    answer = ""
    
    while x != 0:
        q = int(x/16)
        r = x % 16
        answer = H[r] + answer
        x = q   

    if answer == "":
        return "0"

    else:
        return answer

    
#Converts an RGB colour value 0-255 to a 2-digit hex number.
def getHexColourValue( x ):
    hexValue = convertDecimalToHex( x )
    
    if len(hexValue) == 1:
        return "0" + hexValue
    
    else:
        return hexValue


#Converts an RGB triplet to a 6-digit hexadecimal colour code
def getPythonColour(r, g, b):
    rHD = getHexColourValue(r)
    gHD = getHexColourValue(g)
    bHD = getHexColourValue(b)
    color = "#" + rHD + gHD + bHD
    return color


#Calculates the colouring of a particle (either the anode or the deflector) based on its charge.  In general,
#Bright green = big positive charge
#Bright yellow = big negative charge
#White = neutral
def getParticleColour( currentCharge, maxMagnitude ):
      if currentCharge < 0:
            r1 = 255
            g1 = 255
            b1 = 0
            r2 = 255
            g2 = 255
            b2 = 255
            offset = maxMagnitude

      else:
            r1 = 255
            g1 = 255
            b1 = 255
            r2 = 0
            g2 = 255
            b2 = 0
            offset = 0

      deltaR = (r2-r1)/maxMagnitude
      deltaG = (g2-g1)/maxMagnitude
      deltaB = (b2-b1)/maxMagnitude

      r = int( r1 + (currentCharge+offset) * deltaR )       
      g = int( g1 + (currentCharge+offset) * deltaG )       
      b = int( b1 + (currentCharge+offset) * deltaB )
      
      return getPythonColour( r, g, b) 


#Sets constants at the start of the program
def setInitialValues():
    global deflectorChargeImageFile, electronImageFile, xDeflector, yDeflector, xMouse, yMouse, maxSpeedDeflector, speedElectrons
    global gameRunning, xCathode, yCathode, xAnode, yAnode
    global electronMass, anodeRadius, xDeflector, yDeflector, xMouse, yMouse
    global yElectronSpeed, electronImage, mouseDown, deflectorSign1, deflectorSign2, anodeSquaredRadius

    mouseDown = False
    xCathode = 600
    yCathode = 100
    xAnode = 600
    yAnode = 700
    anodeRadius = 100
    anodeSquaredRadius = anodeRadius**2
    electronMass = 1
    xDeflector = 500
    yDeflector = 300
    xMouse = xDeflector  
    yMouse = yDeflector
    deflectorSign1 = 0
    deflectorSign2 = 0
   
    resetElectrons()
    resetUserValues(1)
    

#Resets user values whenever a slider bar is adjusted
def resetUserValues(x):
    global anodeCharge, deflectorCharge, releaseInterval, deflectorColour, anodeColour
    
    anodeCharge = int(anodeChargeSlider.get())
    deflectorCharge = int(deflectorChargeSlider.get())
    beamDensity = int(beamDensitySlider.get() ) #1-10
    releaseInterval = min(11, max(2, 12 - beamDensity))

    anodeColour = getParticleColour( anodeCharge, 50000 )
    deflectorColour = getParticleColour( deflectorCharge, 1000 )
    

#Creates a new electron at the cathode.  Called in each frame of the animation.
def spawnNewElectron():
      xElectron.append(xCathode)
      yElectron.append(yCathode)
      xElectronSpeed.append(0)
      yElectronSpeed.append(0)
      electronImage.append(0)


#Deletes an electron when it comes close to the anode
def deleteElectron(i):
      xElectron.pop(i)
      yElectron.pop(i)
      xElectronSpeed.pop(i)
      yElectronSpeed.pop(i)
      electronImage.pop(i)


def getDistance(x1, y1, x2, y2):
    return sqrt( (x2 - x1)**2 + (y2-y1)**2 )


def getSquaredDistance( x1, y1, x2, y2 ):
    return (x2 - x1)**2 + (y2-y1)**2


#Updates the positions of each electron currently on screen using Coloumb's Law and Newtons laws.
def updateElectronPositions():
    global xElectron, yElectron, xElectronDir, yElectronDir, xElectronSpeed, yElectronSpeed

    i = 0

    while i < len(xElectron):  #For each electron i, calculate the sum of the forces on it in the X and Y directions using Coulomb's Law

            #Calculate distances between electron i and the anode and the deflector
            squaredDistFromAnode = getSquaredDistance( xAnode, yAnode, xElectron[i], yElectron[i] )
            squaredDistFromDeflector = getSquaredDistance( xDeflector, yDeflector, xElectron[i], yElectron[i] )
            distFromAnode = sqrt( squaredDistFromAnode )
            distFromDeflector = sqrt( squaredDistFromDeflector )

            #Magnitude of the attractive and repulsive forces via Coulomb's Law, assuming the electron charge is -1 and the electrical constant K is 1.
            forceOfAttraction = anodeCharge / squaredDistFromAnode
            forceOfRepulsion = deflectorCharge / squaredDistFromDeflector

            #X and Y components of the attractive and repulsive forces, calculated using the unit vectors of the displacements between the electron and the anode/deflector
            forceOfAttractionX = forceOfAttraction * (xAnode - xElectron[i])/distFromAnode
            forceOfAttractionY = forceOfAttraction * (yAnode - yElectron[i])/distFromAnode

            forceOfRepulsionX = forceOfRepulsion * (xDeflector - xElectron[i])/distFromDeflector
            forceOfRepulsionY = forceOfRepulsion * (yDeflector - yElectron[i])/distFromDeflector

            #Net force on the electron in X and Y directions
            netForceX = forceOfAttractionX + forceOfRepulsionX
            netForceY = forceOfAttractionY + forceOfRepulsionY

            #Net acceleration of the electron in X and Y directions (per frame of animation)
            accelerationX = netForceX/electronMass
            accelerationY = netForceY/electronMass

            #Updating the current velocity of the electron using its  acceleration (the unit of speed is pixels per frame) 
            xElectronSpeed[i] = xElectronSpeed[i] + accelerationX
            yElectronSpeed[i] = yElectronSpeed[i] + accelerationY

            #Updating the current position of the electron using its velocity
            xElectron[i] = xElectron[i] + xElectronSpeed[i] 
            yElectron[i] = yElectron[i] + yElectronSpeed[i]

            #Delete the electron if it has gotten sufficiently close to the anode 
            if squaredDistFromAnode < anodeSquaredRadius:
                  deleteElectron(i)  #results in electrons i+1 up through n-1 being shifted one index down, so that i does not need to be incremented in order
                                               #to get to the next electron in the list
            else:
                  i = i + 1    #if the electron did not get absorbed by the anode, increment i to access the next electron in the list.


#Moves the deflector whenever it's dragged using the mouse
def updateDeflectorPosition():
    global xDeflector, yDeflector

    xDeflector = xMouse
    yDeflector = yMouse


#Calculates the grey scale at which the plus- or minus-sign will be drawn, based on the charge level. In general,
#Black = highly charged
#White = neutral
def getSignGreyScale( charge, maxCharge ):
    preciseGreyLevel = -100/maxCharge * abs(charge) + 100
    boundedGreyLevel = max(1, min(99, int(preciseGreyLevel)))
    colour = "grey" + str(boundedGreyLevel)
    return colour
     

#Draws the deflector charge, including its plus- or minus sign.  Its colour depends on its charge.
def drawDeflector():
    global deflectorChargeImage, deflectorSign1, deflectorSign2

    deflectorChargeImage = screen.create_oval( xDeflector-12, yDeflector-12, xDeflector + 12, yDeflector + 12, fill = deflectorColour )
    greyScale = getSignGreyScale( deflectorCharge, 1000 )
    
    if deflectorCharge < 0:
          deflectorSign1 = screen.create_line( xDeflector-6, yDeflector, xDeflector + 6, yDeflector, fill = greyScale, width = 1)

    elif deflectorCharge > 0:
          deflectorSign1 = screen.create_line( xDeflector-6, yDeflector, xDeflector + 6, yDeflector, fill = greyScale, width = 1)
          deflectorSign2 = screen.create_line( xDeflector, yDeflector-6, xDeflector, yDeflector + 6, fill = greyScale, width = 1)


#Draws all the electrons on screen.
def drawElectrons():
    global electronImage
    
    for i in range(len(xElectron)):
        electronImage[i] = screen.create_oval(xElectron[i]-4, yElectron[i]-4, xElectron[i]+4, yElectron[i]+4, fill = "yellow")


#Draws the cathode and anode, again with colour based on their charge strength
def drawCathodeAndAnode():
    global cathodeImage, anodeImage, anodeSignImage1,  anodeSignImage2
    
    cathodeImage = screen.create_oval(xCathode-10, yCathode-10, xCathode+10, yCathode+10, fill="green")
    anodeImage = screen.create_oval(xAnode-anodeRadius, yAnode-anodeRadius, xAnode+anodeRadius, yAnode+anodeRadius, fill=anodeColour)

    greyScale = getSignGreyScale( anodeCharge, 50000 )    
    anodeSignImage1 = screen.create_line(xAnode, yAnode-anodeRadius/2, xAnode, yAnode+anodeRadius/2, fill = greyScale, width = 3)
    anodeSignImage2 = screen.create_line(xAnode-anodeRadius/2, yAnode, xAnode+anodeRadius/2, yAnode, fill = greyScale, width = 3)


#Deletes all images after each frame of the animation
def deleteImages():
    screen.delete( deflectorChargeImage, deflectorSign1, deflectorSign2, cathodeImage, anodeImage, anodeSignImage1,  anodeSignImage2 )
    deleteElectronImages()


#Deletes just the electrons
def deleteElectronImages():
    for i in range( len(xElectron) ):
            screen.delete( electronImage[i] )


#Clears all arrays containing the electrons' data. Called when the user clicks "Clear Electrons"
def resetElectrons():
      global xElectron, yElectron, xElectronSpeed, yElectronSpeed, electronImage
      
      xElectron = []
      yElectron = []
      xElectronSpeed = []
      yElectronSpeed = []
      electronImage = []


#Main procedure.  Runs the animation as an infinite loop
def runGame():

    f = 0  #frame counter

    while True:
          
        if f % releaseInterval == 0 and len( xElectron ) < 500:  #releases a new electron every releaseInterval frames
            spawnNewElectron()
              
        updateDeflectorPosition()
        updateElectronPositions()
        
        drawCathodeAndAnode()
        drawDeflector()
        drawElectrons()
        
        screen.update()
        sleep(0.01)
        deleteImages()

        f = f + 1


#Creates the slider bars and buttons when the program loads
def buildGUI():
      global anodeChargeSlider, deflectorChargeSlider, beamDensitySlider
      
      anodeChargeLabel = Label(root, text = "Anode charge", font = "fixedsys 15", foreground="yellow", background="slate grey")
      anodeChargeLabel.place( x = 10, y = 30)
      anodeChargeSlider = Scale( root, from_ = 0, to=50000, orient=HORIZONTAL, command = resetUserValues, length=150, width = 10, resolution = 1000  )
      anodeChargeSlider.pack()
      anodeChargeSlider.place( x = 120, y = 30 )
      anodeChargeSlider.set( 20000 )

      deflectorChargeLabel = Label(root, text = "Deflector charge", font = "fixedsys 15", foreground="yellow", background="slate grey")
      deflectorChargeLabel.place( x = 10, y = 80)
      deflectorChargeSlider = Scale( root, from_ = -1000, to=1000, orient=HORIZONTAL, command = resetUserValues, length=150, width = 10, resolution = 20 )
      deflectorChargeSlider.pack()
      deflectorChargeSlider.place( x = 140, y = 80)
      deflectorChargeSlider.set( -400) 

      beamDensityLabel = Label(root, text = "Beam density", font = "fixedsys 15", foreground="yellow", background="slate grey")
      beamDensityLabel.place( x = 10, y = 130)
      beamDensitySlider = Scale( root, from_ = 1, to=10, orient=HORIZONTAL, command = resetUserValues, length=100, width=10  )
      beamDensitySlider.pack()
      beamDensitySlider.place( x = 120, y = 130 )
      beamDensitySlider.set( 5 )

      clearElectronsButton = Button(root, text="Clear Electrons", command = clearElectronsButtonPressed)
      clearElectronsButton.pack()
      clearElectronsButton.place( x = 10, y = 180, width = 110 )


#Called when the user clicks "Clear Electrons"
def clearElectronsButtonPressed():
      deleteElectronImages()
      resetElectrons()

      
#Starts the program.  It's the first procedure called when the program loads.
def start():
    global xDeflector, yDeflector, xMouse, yMouse
    
    buildGUI()
    setInitialValues()
    runGame()


#Makes the screen listen for user actions
root.after( 0, start )
screen.bind("<Button-1>", mouseClicked )
screen.bind("<Motion>", mouseMoved )
screen.bind("<ButtonRelease-1>", mouseReleased )
screen.pack()
screen.focus_set()
root.mainloop()
