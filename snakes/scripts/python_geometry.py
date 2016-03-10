"""Routine to capture surface geometry of pythons specifically.
   Take some head shot (oriented snout down) with a dark background and figure out
           whether it's a python.  Pythons have a distinct "V" on top of their heads, the 
           apex over the snout and the legs of the "V" extending just inside the eyes.  
           The angle of the vertex is acute - somewhere around 55-60 degrees.  We'l identify
           the marking by exploiting the fact that the coloration of
           the "V" is lighter than the surrounding skin.  The strategy is:
           - reduce the image to grayscale (pixel values 0-255)
           - do a binary reduction - light pixels to white (255), dark to black (0)
           - split the image roughly in half vertically
           - fit a regression line to the white pixels separately for each half (after appropriate rotations)
           - compare the regression lines and goodness-of-fit metrics.

           It's a python if:
           - the beta coefficient (slope) show that the lines are about 45-50 degrees apart; and
           - the slopes/angles of the two halves are pretty close to one another; and
           - there's a good fit (R2 > .75-.80) for both halves; and
           - both the beta coefficient delta and R2 are stable as the image is rotated

           Snakes without linear markings will have beta coefficient deltas all over the map
           and less-than-stable R2s"""

##TODO: - logic to analyze the metrics (means and best fit)
##TODO: - store stats in the database
##TODO: - new database fields to include is_head_shot, and whatever stats we develop
##TODO: - user input screen to upload head shot and evaluate species in real time
##TODO: - can we substitute head shots for full-body images for chromatic analysis?
 

#core libraries
import os
import sys
import configparser
from math import asin, sqrt
#analytical libraries
import numpy as np
from scipy import ndimage #handles rotations
from scipy import stats   #for linear regression
import matplotlib.pyplot as plt
from PIL import Image

RAD2DEG=57.3

config=configparser.ConfigParser()
config.read('snake_settings_cfg.ini')

def process_image(file_name=None, debug_print=False, 
                  debug_show_images=False, debug_plot=False,
                  rotation_range=30, split_range= 20):
    """rotation range is +/- degrees from center e.g.,  30 means +30 .. -30
       split range is difference from even e.g., 20 means  60/40 .. 40/60
       specify both to be 0 for "no rotation, 50/50 split".
    """
    results_left = [] 
    results_right = []
    if not file_name:
        file_name=config['locations']['capture_image_dir'] + \
                  config['locations']['capture_image_file'] 
    
    with Image.open(file_name) as image:
        #Here, we try lots of rotations and left/right splits to find
        #  the best fit
        
        #rotation range specifies rotation rotations in degrees
        for rotation in range(-rotation_range, rotation_range + 1, 10):
            #im=ndimage.interpolation.rotate(image, rotation, reshape=False)
            im=ndimage.interpolation.rotate(image, rotation, reshape=True)
            
            rotated=Image.fromarray(im)
            if debug_show_images:
                rotated.show(title="original image") 
                
            #split range specifies vertical split.  
            for split in range(50 - split_range, 50 + split_range + 1, 5):
                cum_angle = 0
                #create a np array for the left "half" (depends on split)
                data=np.array(im).astype(np.uint8())
                half_width=int(len(data[0])*split/100)
                left_data = data[:, :half_width]
                left=Image.fromarray(left_data)
                
                #convert to binary array (two-step process because convert() has a bug).
                left=left.convert("1", dither=0)
                left=left.convert("L", dither=0) #produces pixel array with values 0 and 255
                left_data=np.array(left)

                #create the right "half" in the same way                                
                right_data = data[:, half_width:]     
                right=Image.fromarray(right_data)
                right=right.convert("1", dither=0)
                right=right.convert("L", dither=0)
                right_data=np.array(right)                            

                #Calculate regression coefficients for each half of the image; note that we
                #  need to rotate the image to get regression to work properly
                for imgdata, label, pic in zip(
                    [
                     np.fliplr(np.flipud(left_data)),  #flips left half horizontally and vertically
                     np.fliplr(right_data)
                     #np.fliplr(np.flipud(left_data)),  #flips left half horizontally and vertically
                     #right_data                     
                     ],           #flips right half horizontally
                    ['left', 'right'],
                    [left, right]):
                
                    if label=='left':
                        results=results_left
                    else:
                        results=results_right

                    if debug_show_images:
                        pic.show(title=label)  
                    
                    #Set up the regression analysis ...
                    
                    #create vectors of x and y values of pixels representing the marking
                    #  we're looking for - a pixel value of 255 (white) against a 0 (black) background.
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

                    #This uses scipy.stats for the linear regression
                    try:
                        #Slope is the b-coefficient
                        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
                        
                    except ValueError:
                        #if the regression becomes singular and fails, we'll just skip the
                        #  observation.  This can happen with mononchromatic - or nearly so - images.
                        continue
                    
                    r2=r_value**2
                    
                    #a bit of trig - right triangle w/ sides opp=slope, adj=1, hyp=sqrt(1+slope**2)
                    angle=asin(slope/ sqrt(1+slope**2))*RAD2DEG 
                    
                    #stash the results - we'll pass these on to another routine for evaluation.
                    results.append( (label, rotation, split, slope, intercept, r2, angle))
                    cum_angle+=angle
                    if debug_print:
                        print("Results for {}: rotation: {}, split: {}".format(label, rotation, split))
                        print("  beta = {}  R2 = {} angle = {} cum_angle = {} intercept = {}".format(
                               round(slope,2), round(r2, 2), round(angle, 2), round(cum_angle, 2), round(intercept, 2)))
                        #print()
                        
                    #optinally, display the regression line over the scatter plot
                    if debug_plot:
                        fig, ax = plt.subplots() 
                        ax.plot(x, slope * x + intercept, color='red', scalex = 300, scaley=300)
                        ax.set_ylim([0, 350])
                        ax.set_xlim([0, 350])                      

                        ax.scatter(x, y)            
                        fig.show() 
                        x=1
                x=1
                if debug_print:
                    print()  
                    
    return {'left': results_left, 'right': results_right}           

def analyze_results(results=None):
    pass


if __name__=='__main__':
    image_file='/home/pat/workspace/snakes/snakes/images/research_images/color_head.png'
    #image_file= '/home/pat/workspace/snakes/snakes/images/test_pattern_images/test_45_degrees.PNG'
    #image_file= '/home/pat/workspace/snakes/snakes/images/test_pattern_images/test_55_degrees.PNG'
    #image_file= '/home/pat/vmshared/test_pattern_images/test_55_degrees.PNG'
    #image_file= '/home/pat/vmshared/test_pattern_images/markers.PNG'
    #image_file= '/home/pat/vmshared/test_pattern_images/grid.PNG'
    #image_file= '/home/pat/vmshared/test_pattern_images/test_45_degrees.PNG'
    #image_file= '/home/pat/vmshared/test_pattern_images/test_45_degrees_marked.PNG'
    results=process_image(file_name=image_file, debug_print=True, 
                          debug_show_images=False, debug_plot=False,
                          rotation_range=20, split_range=10)
                          #rotation_range=0, split_range=0)
                          
    #bad images yield no results                      
    if results:       
        with open(config['locations']['debug_dir']+config['locations']['debug_file'], 'w') as dfile:
            for lst in [results['left'], results['right']]:
                for line in lst:
                    dfile.write(str(line)+'\n')

    pass