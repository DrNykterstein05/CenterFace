# CenterFace
## Benutzung
Das Programm CenterFace kann dazu benutzt werden, in einer Videokonferenz ein Gesicht dauerhaft zu zentrieren. Außerdem
könnte man bei einer Überwachungskamera, ein Gesicht verfolgen, um es besser analysieren zu können.
## Umsetzung
Die Gesichterkennung erfolgt durch die Methode face_detection.py in der importierten Bibliothek mediapipe. Dabei wird ein
Gesicht anhand von sechs sogenannten "Keypoints" erkannt. Die Detektion wird mit Hilfe der Bibliothek cv2 auf dem
Originalbild projeziert und angezeigt.
1. Koordinaten um das Gesicht berechnen: Die Methode computeCropping() benötigt den Parameter detection, um mit den
Koordiaten der Keypoints den Rahmen um das Gesicht zu berechnen, in das gezoomt werden soll. Die Koordiaten der vier Seiten,
sowie des Winkels( Erklärung in 3.), um den das Gesicht zur Seite gedreht werden soll und die Koordinaten der Nase werden
in die Liste computed_coords gespeichert.
2. Angleichung der Koordinaten, wenn das Gesicht aus der Kamera verschwindet: Die Methode validateCropping() benötigt die
vorher berechneten computed_coords als Parameter. Wenn das Gesicht ganz oder zur Hälfte aus dem Kamerabild verschwindet
werden die Koordinaten an den Rand angeglichen. Ausgegeben werden die verbesserten Koordinaten. Falls das Gesicht normal im
Bild ist, werden die ursprünglichen Koordinaten ausgegeben.
3. Berechnung des Kopfneigewinkels nach links oder rechts: Die Methode computeAngel() benötigt die Koordinaten der zwei 
Ohren. Erst wird mit der Ankathete und Gegenkathete die Hypotenuse berechnet, dann wird mit dem Sinus der Winkel zwischen 
der Linie der Ohren und einer Horizontalen berechnet und ausgegeben.
4. Bewegungen auf dem Bild können weniger stark und langsamer verfolgt werden: In der Methode smoothMotion() werden von den
letzten x computed_coords der Durchschnitt berechnet, wobei x vom Benutzer verändert werden kann. Je höher x, desto 
verzögerter die Zentrierung. Das Gleiche wird mit dem
Winkel gemacht. Dadurch erfolgt ein sehr viel angenehmeres Bild, da nicht jede kleinste Bewegung sofort angeglichen wird. 
Ausgeben werden der Durchschnitt der jeweiligen Koordinaten und des Winkels.
5. Bild um den Winkel drehen: rotateImage() benötigt das Bild, den Winkel und die Koordinaten des Drehpunkts. Der Winkel
wurde wie in 3. beschrieben berechnet. Als Drehpunkt benuztzen wir die Nase. Ausgegeben wird das rotierte Bild.
## Lokale Ausführung
Für die lokale Ausführung ist eine Python inklusive pip Installation nötig. Um die nötigen Bibliotheken zu installieren
`pip install -r requirements.txt` aufrufen.
Zum Start des Programms `python CenterFace.py` ausführen.
Im Falle, dass das Programm nicht starten sollte, in Zeile 12 statt <cap = cv2.VideoCapture(0)> <cap = cv2.VideoCapture(1)> probieren.
