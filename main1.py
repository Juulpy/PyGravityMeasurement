import cv2 #Module voor camera-analyse
import imutils #om de middelpunten te berekenen
import math
import time

cap = cv2.VideoCapture(0) #stream de camerabeelden naar python

with open("out.txt","w") as f: #maak of open de outputfile als out.txt
    f.write("gravitatieconstante\tperiode\n") #Maak out.txt leeg en voeg de headers voor de TSV toe.
length = 0.79 #lengte van draad
coords = (0,0) #startwaarde voor coordinaten van bal
oldcoords = (0,0) #tempwaarde
elapsed = 0 #tempwaarde
DirectionChanged = False #Bool die true is als de richting veranderd is
olddirection = "left" #startwaarden voor de richting van de bal
direction = "left"

def ballCenter(cnts): #functie om het middelpunt van de 'blob' te berekenen

    for c in cnts: #cnts is de 'contour' van de bal
        M = cv2.moments(c) #bereken de momenten van alle blobs
        try:
            cX = int(M["m10"] / M["m00"]) #bereken het centrum alle x-coordinaten
            cY = int(M["m01"] / M["m00"]) #bereken het centrum alle y-coordinaten
            coords = (cX,cY) #tuple van de coordinaten van het centrum van de bal
            return coords #return de coordinaten
        except ZeroDivisionError: #Als M["00"] 0 dan wordt er door 0 gedeeld, skip als dit zo is
            pass

while(True): #loop voor de frame-analyse
    start = time.time() #start de timer (periodeberekening)
    # Capture frame-by-frame
    ret, frame = cap.read() #het camerabeeld leesbaar maken voor cv2

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #beeld grayscale maken zodat de threshold(drempel) toegepast kan worden
    ret, frame = cv2.threshold(frame, 200, 255, cv2.THRESH_BINARY) #drempelwaarde toepassen, elke grijswaarde die donkerder is dan RGB(200,200,200) (afhankelijk van lichtsituatie) wordt gefiltert.
    frame = cv2.GaussianBlur(frame, (13, 13), 0) #blur toepassen, dit maakt de centrumberekening makkelijker en minder ruisgevoelig
    cnts = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #vind de contouren van de bal
    cnts = imutils.grab_contours(cnts) #maak een leesbare list van alle contouren
    try: #als er geen bal gedetecteerd is zou het een error geven, in dat geval, skippen!
        coords = ballCenter(cnts) #bereken door de eerder gevonden cnts de coordinaten van de bal dmv de functie
        dX =  abs(oldcoords[0]-coords[0]) #bereken het verschil in x-waarden per frame
        if(oldcoords[0]<coords[0]): # als de bal naar rechts beweegt, verander de direction-waarde naar 'right'
            direction = "right"

        if(oldcoords[0]>coords[0] and dX < 5):#vice versa, maar met extra voorwaarde dat dX kleiner moet zijn dan 5, om gekke meetwaarden te voorkomen
            direction = "left"

        if(olddirection == "left" and direction == "right"): #als de de bal eerst naar links bewoog en nu naar rechts beweegt, start de timer
            starttime = time.time()
            DirectionChanged = True #en verander de boolean naar True (ruis voorkomen)

        if(olddirection == "right" and direction == "left" and DirectionChanged == True): #voer dit uit als de bal de andere kant op begint te bewegen
            elapsed = time.time() - starttime #bereken de verstreken tijd
            period = 2*elapsed #het programma meet een halve periode, dus de elapsed-waarde moet verdubbeld worden
            DirectionChanged = True
            gravitation = (length*4*math.pi**2)/(period**2) #bereken de gravitatieconstante met de gegeven formule
            print(gravitation)
            if(gravitation > 3 and gravitation < 100): #om gekke waarden te voorkomen
                with open("out.txt","a") as f: #schrijf de output naar de file
                    f.write(str(gravitation).replace(".",",") + "\t" + str(period).replace(".",",")+"\n")


        output = frame
        cv2.imshow('frame',output) #laat het gefilterde beeld zien (debug)
        olddirection = direction
        oldcoords = coords
        print(coords) #debug




    except Exception as e: #als er geen bal gedetecteerd wordt (eerste paar frames) geeft het programma een error. skip deze en print de error (debug)
        print (e)
        pass




    if cv2.waitKey(1) & 0xFF == ord("q"): #druk op q om het programma te sluiten
        break
