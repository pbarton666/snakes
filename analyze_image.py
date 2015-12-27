import os
import sys

import numpy as np
from PIL import Image
from utilities import hsv_to_rgb, rgb_to_hsv, mask
from utilities import create_histogram, filter_background
  
def reduce_image(original_image_dir=None,
                      hsv_image_dir=None,
                      original_image_file=None,
                      target_background_h=None,
                      target_background_s=None,
                      target_background_v=None,
                      target_background_tolerance=None,
                      new_background_hsv=None,
                      num_colors=None,
                      show_histo=True                      
                      ):
    """This routine assumes accepts an image in RGB, RGBA, or PNG format, 
       removes the (potentially noisy) background, replaces it with homogenous
       background, and reduces the color palatte.  It returns the reduced version"""
    
    #this returns an RGB image with background flattened to a known color
    im=filter_background(original_image_dir=original_image_dir,
                              hsv_image_dir=hsv_image_dir,
                              original_image_file=original_image_file,
                              target_background_h=target_background_h,
                              target_background_s=target_background_s,
                              target_background_v=target_background_v,
                              target_background_tolerance=target_background_tolerance,
                              new_background_hsv=new_background_hsv,
                              return_rgb=True
                              )
    
    #this is the new, uniform background color (as RGB)
    background_rgb=hsv_to_rgb(np.array((new_background_hsv)))*255
    back_r, back_g, back_b = background_rgb   
    im=im.convert("RGBA")
    
    #this reduces the image to a specified number of colors, then converts it
    # back to the RGBA color model
    im=im.convert('P', palette=Image.ADAPTIVE, colors=num_colors)
    im=im.convert("RGBA")
    return im

if __name__=='__main__':
    original_image_dir="/home/pat/workspace/snakes"
    hsv_image_dir="/home/pat/workspace/snakes"
    #original_image_file="test_image_red.png"  
    original_image_file="test_image.png" 
    
    #number of colors preserved in palette reduction
    num_colors=10  
    
    #These settings address logic that attempts to filter out the background
    #  color of the target image.  Anything in the target color +/0 the tolerance
    #  in all the settings is deemed background and replaced with the new background 
    #  color.  The effect is to have a homoginized, known background color redacted
    #  from the image for future analysis.
    
    #Note:  ideally, it would be optimal to filter this to alpha, but the image procesing
    #  libraries I've found to date do not work and play well with png files.
    
    #color (hsv) of the background, along with tolerence for determining it
    target_background_h=0
    target_background_s=.76
    target_background_v=.93
    target_background_tolerance=.01
    #color (hsv) of the new background color a
    new_background_hsv=(0, 1, 1)
   
    fb=create_histogram(original_image_dir=original_image_dir,
                          hsv_image_dir=hsv_image_dir,
                          original_image_file=original_image_file,
                          target_background_h=target_background_h,
                          target_background_s=target_background_s,
                          target_background_v=target_background_v,
                          target_background_tolerance=target_background_tolerance,
                          new_background_hsv=new_background_hsv,
                          num_colors=num_colors
                          )    
    fb.show()
    a=1
    ###Next step:  create 'flat' image of only the non-background pixels
    