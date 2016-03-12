"""Routines to capture surface geometry of pythons specifically.
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
           - there's a good fit (R2 > .7; and
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
import csv
import re
#analytical libraries
import numpy as np
from scipy import ndimage #handles rotations
from scipy import stats   #for linear regression
import numpy as np
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
       
       return {'left': results_left, 'right': results_right, 'data_labels':data_labels}
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
                    data_labels=('label', 'rotation', 'split', 'slope', 'intercept', 'r2', 'angle')
                    ### be sure to keep these labels in synch with the results tuple ####
                   
                    if debug_print:
                        cum_angle+=angle
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
                    
    return {'left': results_left, 'right': results_right, 'data_labels':data_labels}           


def scrub_data(raw_data):
    """scrubs non-alphanu kruft out of a stringified tuple, 
       converts to float where possible, returns a list
    ["('left', ' -20', ' 6.563)"] -> ['left', -20.0,  6.563"]
    """
    content=raw_data[0].split(',')
    for ix, item in enumerate(content):  
        for bad_thing in ["(", r")", r'"', r"'"]:
            item=item.replace(bad_thing,"")
        content[ix]=item
        try:
            content[ix]=float(item)
        except:
            pass
                
    return content
    
def print_array(npa):
    for n in npa:
        for c in n:
            print(c, end=", ")
        print()    

def analyze_results(data_file=None, debug_print=False):
    """This routine figures out whether wez gots us a 'thon. 

       The image processing routine has created data based on different permutations
       of the original capture and statistical analysis applied against them. Now we
       need to make some sense out of it and decide if we have a python.  Here's the 
       algorithm:
       
       - find all the rotation/split combinations for which we have data for both halves 
         of the beast (not always the case - especially with extreme splits).
        - find the pairs with the smallest difference between the measured angles; this way
          we know the image is aligned properly.
             - from among these, find the ones with a reasonable fit (R^2) so we know we're not
               looking at garbage.
                   -from among these, find those closest to the total angle we expect from python
                     markings (somewhere around 55-60 degrees)
       - as an additional check, we'll look over all the observations looking for whether 
         the measured angle stable over observations (it should be if the marking is real).
         
       Note: this could be done more easily with an object already in memory, but this is 
       a bit more robust.
    """
    
    ##TODO: write tests!
    if not data_file:
        return -1
    
    #Grab the screening criteria
    threhhold_max_angle_dlta =float(config['geometry_python']["threhhold_max_angle_dlta"])
    threhhold_min_avg_r2 =float(config['geometry_python']["threhhold_min_avg_r2"])
    threhhold_min_angle_sum =float(config['geometry_python']["threhhold_min_angle_sum"])
    threhhold_max_angle_sum =float(config['geometry_python']["threhhold_max_angle_sum"])
    threhhold_max_coef_of_var =float(config['geometry_python']["threhhold_max_coef_of_var"])
        
    #read data, scrub out the kruft and convert numbers to floats
    raw=[]
    with open(data_file, 'r') as df:
        reader=csv.reader(df, delimiter='\t')
        for line in reader:
            line=scrub_data(line)
            raw.append(line)
    data_rows=len(raw)
    
    #Build data structure of matched left/right pairs. Raw data has these fields:
    #data_labels=('label', 'rotation', 'split', 'slope', 'intercept', 'r2', 'angle')
    #.... where 'label' is 'left' or 'right'.  All the 'left' ones comes first.
    #
    #All we really need to keep are the r2 and angle metrics for analysis
    
    #for sanity, some names for data column indices for incoming data
    LABEL_IX=0; ROT_IX=1; SPLIT_IX=2; SLOPE_IX=3; INT_IX=4; R2_IX=5; ANGLE_IX=6
    
    dtype=[('left_r2', float), ('right_r2', float), ('avg_r2', float),
           ('left_angle',float), ('right_angle', float), ('sum_angle', float), 
           ('dlta_angle', float)
           ]
    npa=np.ones((len(raw)/2), dtype=dtype)
    
    #a couple o' indices    
    trow=0  #target row - our current np array target
    srow=0  #source row - present position in raw data 
    
    #From the top of the raw data, find the next 'left' and keep looking
    #  until we find Mr. 'right'
    
    while True:
        label = raw[srow][LABEL_IX] #left or right
        if label=='right':  
            break   #we've exahausted the 'left'
        
        #data from the left half
        left_rotation=raw[srow][ROT_IX]
        left_split=raw[srow][SPLIT_IX]
        left_r2=raw[srow][R2_IX]
        left_angle=raw[srow][ANGLE_IX]
        
        #scan the rest of the data for the matching 'right'       

        for i in range(srow+1, data_rows+1):
            if raw[i][LABEL_IX] == 'right' and \
               raw[i][ROT_IX] == left_rotation and \
               raw[i][SPLIT_IX] == left_split:
                #yes!  we have the other half so load up the np array
                right_r2=raw[i][R2_IX]
                avg_r2=(left_r2 + right_r2)/2
                right_angle=raw[i][ANGLE_IX]
                sum_angle=left_angle + right_angle
                dlta_angle=abs(left_angle - right_angle)
               
                npa[trow]=(left_r2, right_r2, avg_r2,
                           left_angle, right_angle, sum_angle, dlta_angle)

                trow+=1
                break
        srow+=1
    #We're done, so prune extra rows from the np array
    npa=npa[:trow]


    
    #Analysis begins here
    '''
    - find all the rotation/split combinations for which we have data for both halves 
      of the beast (not always the case - especially with extreme splits).
     - find the pairs with the smallest difference between the measured angles; this way
       we know the image is aligned properly.
          - from among these, find the ones with a reasonable fit (R^2) so we know we're not
            looking at garbage.
                -from among these, find those closest to the total angle we expect from python
                  markings (somewhere around 55-60 degrees)
    - as an additional check, we'll look over all the observations looking for whether 
      the measured angle stable over observations (it should be if the marking is real).  '''  
    
    ##TODO: move these bits in atomic subroutines
    results=[]
    results.append('starting with {} observations'.format(len(npa)))

    #cull out observations with too much difference between the halves
    metric='dlta_angle'
    culled_npa=np.sort(npa, order=metric)
    last_good=-1

    for obs in culled_npa:
        if obs[metric] > threhhold_max_angle_dlta:
            break
        else:
            last_good+=1
    culled_npa=culled_npa[:last_good+1]
    results.append('{} remaining after symmetry check'.format(len(culled_npa)))
    results.append('... max delta between left/right angles is {}'.format(threhhold_max_angle_dlta))
    
    #cull out observations with a lousy fit
    metric='avg_r2'
    culled_npa=np.sort(culled_npa, order=metric)[::-1]  #descending order
    last_good=-1
    
    for obs in culled_npa:
        if obs[metric] < threhhold_min_avg_r2:
            break
        else:
            last_good+=1
    culled_npa=culled_npa[:last_good+1]  
    results.append('{} remaining after goodness-of-fit check'.format(len(culled_npa)))
    results.append('... R^2 needs to be better than {}'.format(threhhold_min_avg_r2))
    
    
    #check if the angles measured is stable (it should be)
    metric='sum_angle'
    coeff_of_variation=np.std(culled_npa['sum_angle'])/np.mean(culled_npa['sum_angle'])
    results.append('coefficient of variation on angles is: {}'.format(coeff_of_variation))
    results.append('...max is {}'.format(threhhold_max_coef_of_var))
    if coeff_of_variation > threhhold_max_coef_of_var:
        results.append('... not looking good.')
        variability_OK=False
    else:
        variability_OK=True
    
    
    #cull out those whose angles don't look like pythonic "V"s
    #huck out those that are too small
    metric='sum_angle'
    culled_npa=np.sort(culled_npa, order=metric)[::-1]  #descending order
    last_good=-1

    for obs in culled_npa:
        if obs[metric] < threhhold_min_angle_sum:
            break
        else:
            last_good+=1
    culled_npa=culled_npa[:last_good+1]   
    
    #huck out those that are too big
    metric='sum_angle'
    culled_npa=np.sort(culled_npa, order=metric)
    last_good=-1

    for obs in culled_npa:
        if obs[metric] >  threhhold_max_angle_sum:
            break
        else:
            last_good+=1
    culled_npa=culled_npa[:last_good+1]  
    results.append('{} remaining after angle check'.format(len(culled_npa)))
    results.append('... angle needs to be between {} and {}'.format(
                   threhhold_min_angle_sum, threhhold_max_angle_sum))
    
    
    if len(culled_npa):
        if variability_OK:
            results.append("\n *** Looks like we've got a python! ***")
        else:
            results.append("Not so sure.  Everything matches except consistency.")
    else:
        results.append("No python here.")
    
    debug_print=True    
    if debug_print:
        for r in results:
            print(r)





if __name__=='__main__':
    image_file='/home/pat/workspace/snakes/snakes/images/research_images/color_head.png'
    image_file='/home/pat/workspace/snakes/snakes/images/research_images/corn.png'
    image_file='/home/pat/workspace/snakes/snakes/images/research_images/king.png'
    #image_file= '/home/pat/workspace/snakes/snakes/images/test_pattern_images/test_45_degrees.PNG'
    #image_file= '/home/pat/workspace/snakes/snakes/images/test_pattern_images/test_55_degrees.PNG'
    #image_file= '/home/pat/vmshared/test_pattern_images/test_55_degrees.PNG'
    #image_file= '/home/pat/vmshared/test_pattern_images/markers.PNG'
    #image_file= '/home/pat/vmshared/test_pattern_images/grid.PNG'
    #image_file= '/home/pat/vmshared/test_pattern_images/test_45_degrees.PNG'
    #image_file= '/home/pat/vmshared/test_pattern_images/test_45_degrees_marked.PNG'
    
    do_process_image=True
    results_file=config['locations']['debug_dir']+config['locations']['debug_file']
    
    if do_process_image:
        results=process_image(file_name=image_file, debug_print=True, 
                              debug_show_images=False, debug_plot=False,
                              rotation_range=20, split_range=10)
                              #rotation_range=0, split_range=0)
                            
        #bad images yield no results                      
        if results:       
            with open(results_file, 'w') as dfile:
                for lst in [results['left'], results['right']]:
                    for line in lst:
                        dfile.write(str(line)+'\n')

    analyze_results(results_file, debug_print=False)
    
    x=1