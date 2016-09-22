import cv2
import numpy as np
import img_manip_analyze

BLUR_RANGE = [1, 31]
BLUR = 9

THRESHOLD_RANGE = [20,120]
THRESHOLD = 60

ITER_RANGE = [1, 15]
ITER = 6

AREA_RANGE = [10,10000]
AREA = 800


#MAX_EDGE_RATIO = 0.1
ERODE_ITER_ADDITION = 3

def detect_ab(ih, blur, threshold, iter, min_area):
    filtered = cv2.GaussianBlur(ih.bwimg,(blur, blur), 0)
    ret, thresh_black = cv2.threshold(filtered, threshold, 255, cv2.THRESH_BINARY)

    kernel = np.ones((3,3), dtype=np.uint8)
    pi = thresh_black

    pi = cv2.dilate(pi,kernel,iterations = iter)
    pi = cv2.erode(pi,kernel,iterations = iter + ERODE_ITER_ADDITION)
    
    contimg, contours, hierarchy = cv2.findContours(pi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #print hierarchy
    
    for c, h in zip(contours, hierarchy[0]):
        area = cv2.contourArea(c)
        if area > min_area and h[2] < 0:# and area < 100000:
            ih.temp_cells.append(c)
    
    return contimg


    #dist = cv2.distanceTransform(255-pi, cv2.DIST_L2, 5)
    #cv2.imwrite("step2.png", dist)
    #dist = np.uint8(dist)

    #sure_fg = cv2.adaptiveThreshold(dist, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, ADAPTIVE_THRESHOLD, -4)
    #sure_fg = cv2.morphologyEx(sure_fg, cv2.MORPH_OPEN, kernel, iterations = KERNEL_ITER)
    #sure_fg = np.uint8(sure_fg)
    #cv2.imwrite("step3.png", sure_fg)

    #ret, markers = cv2.connectedComponents(sure_fg)
    #markers = markers + 10
    #markers[np.logical_and(pi != 255, sure_fg != 255)] = 0
    #cv2.imwrite("step4.png", markers)

    #temp_cimg = np.zeros_like(cimg)
    #temp_cimg[pi==255] = [0,0,255]
    #temp_cimg[pi!=255] = [255,0,0]
    #cv2.imwrite("temp.png", temp_cimg)
    #markers = cv2.watershed(temp_cimg, markers)
    #cv2.imwrite("step5.png", markers)
    #print markers

    #cimg[markers == -1] = [0,0,255]
    #cv2.imwrite("step6.png", cimg)
    
if __name__ == "__main__":
    ih = img_manip_analyze.ImageHolder("P1_12000a.tif", 1.0)
    img = detect_ab(ih, BLUR, THRESHOLD, ITER, AREA)
    
    img = np.array(ih.image)
    for c in ih.temp_cells:
        cv2.drawContours(img, [c], 0, (0, 255, 128), thickness=cv2.FILLED)
    cv2.imwrite("test.png", img)
