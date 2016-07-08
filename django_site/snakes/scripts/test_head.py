import os
import sys
#import matplotlib
#import psycopg2

import numpy as np
from scipy import ndimage
from scipy import stats   #for linear regression
import matplotlib.pyplot as plt

from PIL import Image
from matplotlib.colors import hsv_to_rgb, rgb_to_hsv

#from utilities import create_histogram, filter_background, mask
#from utilities import reduce_image, get_color_list
#from utilities import RGBToHTMLColor, collect_image_data
#from utilities import collect_image_data, make_png_thumb
#from utilities import add_image_to_database, add_directory_to_database
#from snake_settings import *  #background colors, etc.
#from database_routines import get_connector, make_tables
#import dominant_to_alpha


if __name__=='__main__':
        """Take some head shot (oriented snout down) with a dark background and figure out
           whether it's a python.  Pythons have a distinct "V" on top of their heads, the 
           apex over the snout and the legs extending over their 'ears'.  The angle is acute,
           generally 45-50 degrees.  We'll take advantage of the fact that the coloration of
           the "V" is lighter than the surrounding skin.  The strategy is:
           - reduce the image to grayscale (pixel values 0-255)
           - do a binary reduction - light pixels to white (255), dark to black (0)
           - split the image roughly in half vertically
           - fit a regression line to the white pixels separately for each half (after appropriate rotations)
           - compare the regression lines and goodness-of-fit metrics.
           
           It's a python if:
           - the beta coefficient (slope) of the lines are about 45-50 degrees apart; and
           - there's a good fit (R2 > .75-.80) for both halves; and
           - both the beta coefficient delta and R2 are stable as the image is rotated
           
           Snakes without linear markings will have beta coefficient deltas all over the map
           and less-than-stable R2s
           
           TODO:  
           - logic to analyze the metrics (means and best fit)
           - store stats in the database
           - new database fields to include is_head_shot, and whatever stats we develop
           - user input screen to upload head shot and evaluate species in real time
           - can we substitute head shots for full-body images for chromatic analysis?
           - add this to the writeup
           """
        original_image_dir="/home/pat/workspace/snakes/research_images"
        
        #for testing ... 'color_head.png' is a python
        #original_image_file='color_head.png'
        original_image_file='head_shot_eastern_diamondback.png'
        
        print_array=False
        
        with Image.open(os.path.join(original_image_dir,original_image_file)) as original_image:
                #range specifies rotation angles
                for i in range(0, 11, 5):
                        im=ndimage.interpolation.rotate(original_image, i, reshape=False)
                        rotated=Image.fromarray(im)
                        #rotated.show()   
                        #range specifies vertical split.  60 means left is 60% and right is 40% of image.
                        for split in range(60, 39, -5):
                                #split=40
                                #convert to a numpy array
                                data=np.array(im).astype(np.uint8())
                                #'half' of the width (depends on split) in pixels
                                half_width=int(len(data[0])*split/100)
                                
                                #create the left half of the image
                                left_data = data[:, :half_width]
                                left=Image.fromarray(left_data)#,"RGB")
                                #two-step conversion, first to grayscale then to binary (necessary because
                                #  a bug in convert() fails to produce correct binary array).
                                left=left.convert("1", dither=0)
                                left=left.convert("L", dither=0) #produces pixel array with values 0 and 255
                                left_data=np.array(left)

                                
                                #create the right half in the same way                                
                                right_data = data[:, half_width:]     
                                right=Image.fromarray(right_data)#, "RGB")
                                right=right.convert("1", dither=0)
                                right=right.convert("L", dither=0)
                                right_data=np.array(right)
                                
                                #for debugging, we can print the array
                                if print_array:                   
                                        imgdata=data
                                        #imgdata.show()
                                        for r in range(len(imgdata)):
                                                this_row=''
                                                for c in range(len(imgdata[0])):
                                                        this_elem=imgdata[r,c]
                                                        
                                                        if (this_elem==[255,255,255]).all():
                                                                char='1'
                                                        else:
                                                                char='0'
                                                            
                                                        this_row+=str(char)
                                                print(this_row)
                                                a=1                             
                                
                                ##TODO:  results to database and silence printing
                                
                                #Calculate regression coefficients for each half of the image; note that we
                                #  need to rotate the image to get regression to work properly
                                print("Results for rotation: {}, split: {}".format(i, split))
                                for imgdata, label, pic in zip(
                                        [np.fliplr(np.flipud(left_data)),  #flips left half horizontally and vertically
                                         np.fliplr(right_data)],           #flips right half horizontally
                                        ['left', 'right'],
                                        [left, right]):
                                        if label=='left':
                                                pass
                                        
                                        #regression:  (x, y) pairs are (row, col) for values where
                                        #   image matrix = 255 (white).  Need to start with a 'dark background'                                         
                                       
                                        pic.show()                        
                                        length=np.sum(imgdata)+1
                                        x=np.zeros((length))
                                        y=np.zeros((length))
                                        rix=0
                                        for row in range(len(imgdata)):
                                                for col in range(len(imgdata[0])):
                                                        if  imgdata[row][col]==255:
                                                                x[rix]=row
                                                                y[rix]=col
                                                                rix+=1
                                        
                                        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
                                        
                                        r2=r_value**2
                                        print("{} beta = {}  R2 = {} std err = {}".format(label, round(slope,2), round(r2, 2), round(std_err, 2)))
                                        
                                        #optinally, display the regression line over the scatter plot
                                        plot=True
                                        if plot:
                                                fig, ax = plt.subplots()
                                                #alternative regression routine (can calculate betas w/o y-intercept)
                                                #fit = np.polyfit(x, y, deg=1)  
                                                ax.plot(x, slope * x + intercept, color='red')
                                                ax.scatter(x, y)            
                                                fig.show()   
                                        
                                        
                                print()
                        print()


        
        

    

    