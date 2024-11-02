
import cv2
import numpy as np
import sys
from config.config import *
import mss



def find_center(ul,br):
    x1,y1 =ul
    x2,y2 = br
    cx = (x1+x2)/2
    cy = (y1+y2)/2
    return cx,cy

def detectImage(img_png):
    # Ubica ícono/imagen dentro de imagen base (screenshot del escritorio) y retorna coordenadas x,y del centro
    image = cv2.imread(img_png)
    try:
        # Uso del algoritmo SIFT para encontrar keypoints y descriptores
        sift = cv2.SIFT_create()
        keypts_image, descript_image = sift.detectAndCompute(image,None)
    except Exception as e:
        raise e

    # Toma un Screenshot del escritorio completo para procesamiento.
    # moniotrs: [{'left': 0, 'top': 0, 'width': 2966, 'height': 900}, {'left': 0, 'top': 0, 'width': 1366, 'height': 768}, {'left': 1366, 'top': 0, 'width': 1600, 'height': 900}]
    with mss.mss() as sct:
        #print("Monitores sct.monitors :", sct.monitors)  # Muestra en pantalla los monitores detectados y permite conocer sobre cual se realizará el procesamiento
        screenshot = np.array(sct.grab(sct.monitors[1]))
    screenshot_gray = cv2.cvtColor(screenshot,cv2.COLOR_BGR2GRAY)
    keypts_imgtempl, descript_imgtempl = sift.detectAndCompute(screenshot,None)
    # Uso de función  Brute force Matcher para match los keypoints
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(descript_image,descript_imgtempl, k=2)

    good_matches = []
    for m,n in matches:
        if m.distance < 0.95*n.distance:
            good_matches.append(m)

    # Encuenta la ubicación de la imagen en el screenshot
    if len(good_matches)>=4:
        src_pts = np.float32([keypts_image[m.queryIdx].pt for m in good_matches]).reshape(-1,1,2)
        dst_pts = np.float32([keypts_imgtempl[m.trainIdx].pt for m in good_matches]).reshape(-1,1,2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
        h,w,c = image.shape
        pts = np.float32([[0,0],[0,h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts,M)
        x,y = dst[0][0]
        # De no usar la función find_center las coordenadas entregadas serán de la esquina superior izq de la imagen detectada
        x,y = find_center(dst[0][0],dst[2][0])
        print(f"coords: {x} - {y}")
        
    else:
        print("sin coords")
    return  int(x), int(y)




