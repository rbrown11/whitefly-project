#### WHITE FLY GUI ####


## PRELIM IDEAS
# load folder of images and show image name 
# be able to crop image to remove the background ## MAYBE NOT NECESSARY
# also have a button that puts filter on text 
# count whiteflies and output a csv with count and image name

## check against manual counts!!


import glob
import PySimpleGUI as sg
from PIL import Image, ImageTk
import os
import cv2
import numpy as np
import tkinter as tk
import pandas as pd

from threading import Thread



def parse_folder(path):
    images = glob.glob(f'{path}/*.jpg') + glob.glob(f'{path}/*.png')
    return images

def load_image(path, window):
    try:
        image = Image.open(path)
        image.thumbnail((1440, 810))
        photo_img = ImageTk.PhotoImage(image)
        window["image"].update(data=photo_img)
    except:
        print(f"Unable to open {path}!")


def nothing(x):
    pass


def main():
    elements = [
        [sg.Image(key="image"),
         sg.Image(key='hsv_im')
        
        ],
        [
            sg.Text("Image File"),
            sg.Input(size=(25, 1), enable_events=True, key="file"),
            sg.FolderBrowse(),
        ],
        [
            sg.Button("Prev"),
            sg.Button("Next"),
            sg.Button('Crop image'),
            sg.Button('Filter image'),
            sg.Button('Count flies'),
            sg.Button('Export results')

        ],
        [
        sg.Text('Fly count:', key='fly', visible=False) ],
    ]
    window = sg.Window("Image Viewer", elements, size=(1600, 1000))
    images = []
    location = 0
    crop = 'FALSE'
    image_name = []
    fly_count = []
    
    resultsTable = pd.DataFrame(
        columns=['image_name', 'fly_count'])
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "file":
            images = parse_folder(values["file"])
            if images:
                load_image(images[0], window)
        if event == "Next" and images:
            window['hsv_im'].update(visible=False) 
            if location == len(images) - 1:
                location = 0
            else:
                location += 1
            load_image(images[location], window)
        if event == "Prev" and images:
            window['hsv_im'].update(visible=False)         
        
            if location == 0:
                location = len(images) - 1
            else:
                location -= 1
            load_image(images[location], window)
        file_name = os.path.basename(images[location])
        if event == 'Crop image':
            fromCenter = False
            im = cv2.imread(images[location])
            down_width = 300
            down_height = 600	
            down_points = (down_width, down_height)
            im_resized = cv2.resize(im , down_points, interpolation= cv2.INTER_LINEAR)
            file_name = os.path.basename(images[location])
            r = cv2.selectROI(im_resized, fromCenter)
            top_left_x = r[0]
            top_left_y = r[1]
            width = r[2]
            height = r[3]
            
           # crop_im = im[top_left_x:top_left_y, (top_left_x + width):(top_left_y + height) ]     
            
            
            
            crop_im = im_resized[int(r[1]):int(r[1]+r[3]),  
                      int(r[0]):int(r[0]+r[2])]        
                                    
            print('coords', top_left_x, top_left_y, width, height)
            
            
            cv2.imwrite(os.path.join(values['file'], 'crop_img.png'), crop_im) 
                       
            crop_image = Image.open(os.path.join(values['file'], 'crop_img.png'))
            crop_image.thumbnail((1440, 810))
            crop_img = ImageTk.PhotoImage(crop_image)

            
            
            
            window["image"].update(data=crop_img)
            
            ## set a variable to make sure to load the correct image in filter image
            
            crop = 'TRUE'
              
            ###########################################
            ## crop image and then update the window ##
            ###########################################
            
            
            # how to display the cropped version ?
            
            
            cv2.waitKey(2500)
            
            if event == sg.WIN_CLOSED:
                break

        if event == 'Filter image':
        
            if crop == 'TRUE':
            
                image = cv2.imread(os.path.join(values['file'], 'crop_img.png'))
                                
                
            elif crop == 'FALSE':

                image = cv2.imread(images[location])

            cv2.namedWindow('image', cv2.WINDOW_NORMAL)

            cv2.createTrackbar('HMin', 'image', 0, 179, nothing)
            cv2.createTrackbar('SMin', 'image', 0, 255, nothing)
            cv2.createTrackbar('VMin', 'image', 0, 255, nothing)
            cv2.createTrackbar('HMax', 'image', 0, 179, nothing)
            cv2.createTrackbar('SMax', 'image', 0, 255, nothing)
            cv2.createTrackbar('VMax', 'image', 0, 255, nothing)


            cv2.setTrackbarPos('HMax', 'image', 179)
            cv2.setTrackbarPos('SMax', 'image', 255)
            cv2.setTrackbarPos('VMax', 'image', 255)


            hMin = sMin = vMin = hMax = sMax = vMax = 0
            phMin = psMin = pvMin = phMax = psMax = pvMax = 0
            

            
            while(1):

                hMin = cv2.getTrackbarPos('HMin', 'image')
                sMin = cv2.getTrackbarPos('SMin', 'image')
                vMin = cv2.getTrackbarPos('VMin', 'image')
                hMax = cv2.getTrackbarPos('HMax', 'image')
                sMax = cv2.getTrackbarPos('SMax', 'image')
                vMax = cv2.getTrackbarPos('VMax', 'image')


                lower = np.array([hMin, sMin, vMin])
                upper = np.array([hMax, sMax, vMax])


                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, lower, upper)
                result = cv2.bitwise_and(image, image, mask=mask)


                if((phMin != hMin) | (psMin != sMin) | (pvMin != vMin) | (phMax != hMax) | (psMax != sMax) | (pvMax != vMax) ):
                    print("(hMin = %d , sMin = %d, vMin = %d), (hMax = %d , sMax = %d, vMax = %d)" % (hMin , sMin , vMin, hMax, sMax , vMax))
                    phMin = hMin
                    psMin = sMin
                    pvMin = vMin
                    phMax = hMax
                    psMax = sMax
                    pvMax = vMax


                cv2.imshow('image', result)
                
                
                if cv2.waitKey(1) == ord('q'):
                    break
                    
                if cv2.getWindowProperty('image', cv2.WND_PROP_VISIBLE) < 1:
                    break
            
            cv2.destroyWindow('image') 
            
            cv2.imwrite(os.path.join(values['file'], 'hsv_img.png'), result)
            
            hsv_image = Image.open(os.path.join(values['file'], 'hsv_img.png'))
            hsv_image.thumbnail((1440, 810))
            hsv_img = ImageTk.PhotoImage(hsv_image)
            
            window["hsv_im"].update(data=hsv_img)
            
            print('image shown')
                
            



        if event == 'Count flies':
        
            path_to_img = os.path.join(values['file'], 'hsv_img.png')
            print(path_to_img)
            image = cv2.imread(path_to_img)
        
            #image = cv2.imread(hsv_img)
            #image = cv2.imread(window['hsv_im'])
        
            #image = cv2.imread(os.path.join(values['file'], 'hsv_img.png'))
        
            #image = cv2.imread(images[location])
            
            #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            #crop_img = image[top_left_x:top_left_y, (top_left_x + width):(top_left_y + height) ]
                       
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
        
            canny = cv2.Canny(gray, 30,150,3) 
            
            (cnt, hierarchy) = cv2.findContours( canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 
            cv2.drawContours(image, cnt, -1, (0, 255, 0), 2) 
            
            fly_nb = len(cnt)
            
            window["fly"].update(visible=True)
            window["fly"].update('Fly count:' + str(len(cnt)))            
       
            
            print(len(cnt))
        
#            print(r)
            image_name.append(file_name)
            fly_count.append(fly_nb)
            
            
#            currentResults = pd.DataFrame({'image_name': [file_name], 'fly_count': [fly_nb]
#                                          })
                                          
#            print(currentResults)
#            print(currentResults)
#            print(resultsTable)
#            resultsTable = pd.concat(
#                [currentResults, resultsTable.loc[:]]).reset_index(drop=True)
#            print(resultsTable)

            cv2.waitKey(2500)

        if event == "Export results":
        
            resultsTable = pd.DataFrame({'image_name' : image_name, 'fly_count': fly_count }) 

            resultsTable.to_csv(os.path.join(os.path.dirname(images[location]), 'fly_count.csv'), sep=",", index=False)


    window.close()



if __name__ == "__main__":
    main()
