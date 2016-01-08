import numpy as np
import math
import os
from matplotlib.colors import hsv_to_rgb, rgb_to_hsv

from PIL import Image

"""some (mostly numpy-based) utilities for wrangling images"""



def collect_image_data(original_image_dir=None,
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
    """This routine gathers 'color swatches' from an image.  For every color found in > 1%
       of the pixels in a reduced form of the image, it returns the %pixels, and the color as
       RGB, HSV, and html.  The reduced form is a mapping to a color palatte consisting of 
       num_colors colors (provided by setup.py)"""
    
    #replaces noisy background, reduces image to num_colors palatte
    im=reduce_image(original_image_dir=original_image_dir,
                          hsv_image_dir=hsv_image_dir,
                          original_image_file=original_image_file,
                          target_background_h=target_background_h,
                          target_background_s=target_background_s,
                          target_background_v=target_background_v,
                          target_background_tolerance=target_background_tolerance,
                          new_background_hsv=new_background_hsv,
                          num_colors=num_colors
                          ) 
    
    #this is the new, uniform background color (as RGB)
    background_rgb=hsv_to_rgb(np.array((new_background_hsv)))*255
    back_r, back_g, back_b = background_rgb 
    
    #returns a list of the colors (RGB) and % of each
    color_list=get_color_list(im=im, 
                                target_background_tolerance=target_background_tolerance,
                                back_r=back_r, 
                                back_g=back_g, 
                                back_b=back_b
                                )
    
    #The color list is a list of tuples.  Each tuple contains:
    # (%pixels represented, (r, g, b))
    #
    #We'll reconstruct this to be a list of dicts with these keys:
    # pct, r, g, b, h, s, v, html
    
    pik_data=[]
    
    for pct, rgb in color_list:
        #separates tuple of values [0,255]
        r, g, b= rgb
        #calculate HSV [0,1] (these raw HSV values could be fed to hsv_to_rgb to reverse the op)
        h_raw, s_raw, v_raw=rgb_to_hsv([ r/255, g/255, b/255])
        #calculate hsv values in natural units
        h = h_raw*360  #h is in terms of degrees
        s = s_raw*100  #s is in terms of percent
        v = v_raw*100  #v is in terms of percent

        html=RGBToHTMLColor(rgb)
        
        pik_data.append({'pct':pct,
                         'r':r, 'g':g, 'b':b, 
                         'h':h, 's':s,'v':v,
                         'html':html})
        

    #return the color analysis and the image used
    return {'pik_data':pik_data, 'image': im}

        

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
    
  
    im=im.convert("RGBA")
    
    #this reduces the image to a specified number of colors, then converts it
    # back to the RGBA color model
    im=im.convert('P', palette=Image.ADAPTIVE, colors=num_colors)
    im=im.convert("RGBA")
    return im

def make_png_thumb(img=None, background=None, hsv=True):
    "creates a transparent-background thumbnail for web page display"
    
    data=np.array(img)
    r, g, b, a = data.T    
    
    #if background is hsv, convert it to rgb
    if hsv:
        background = hsv_to_rgb(np.array((background)))
        back_red, back_blue, back_green = background
        back_red=back_red*255
        back_blue=back_blue*255
        back_green=back_green*255
    else:
        back_red, back_blue, back_green = background
    #this sets the masking condition and replaces the background color 
    replace = (r == back_red) & (b == back_blue) & (g == back_green)
     
    data[replace.T] = (0,0,0,0)
    
    #create a thumbnail (note - need to do masking ops first because thumbnail
    #routine does some color averaging).
    new_image=Image.fromarray(data, 'RGBA')
    new_image.thumbnail((100,100))
    return new_image

def filter_background(original_image_dir=None,
                      hsv_image_dir=None,
                      original_image_file=None,
                      target_background_h=None,
                      target_background_s=None,
                      target_background_v=None,
                      target_background_tolerance=None,
                      new_background_hsv=None,
                      return_rgb=None
                      ):
    """Routine for filtering the background of an image captured in the wild.
       Converts an image using the RGB color model to HSV.  Then, using the HSV
       model, identifies and converts all 'close enough' pixels to a uniform color.
       The resulting image can then easily be manipulated to reduce the new background
       to alpha, screen out the non-background pixels, etc.
       
       This should allow reasonable filtering, even when the background becomes soiled, 
       worn, etc.
       
       Returns numpy array of the HSV image"""


    with Image.open(os.path.join(original_image_dir,original_image_file)) as im:
        #this converts to the HSV color model in stages
        #first lose the alpha (if required for RGBA images)
        
        #If the image came in as a .png file it'll convert to black
        #  because the transparency value is set to 0. We can screen out the
        #  background with a rigorous filter, but risk messing converting "real"
        #  black to the new background color. Will not be issue with other file formats.
        
        if os.path.splitext(original_image_file.lower())[1]=='.png':
            target_background_h=0
            target_background_s=0
            target_background_v=0
            target_background_tolerance=0
        im=im.convert("RGB")
        #im.show()
        #convert the image to a numpy array and transform to HSV
        #  thinking here that this will be better correct for uneven (dirty) background
        
        data_hsv=rgb_to_hsv(np.array(im)/255) #conversion for matplotlib routine
        
        #split image into h, s, v channels and find pixels that are 'close enough' to background
        h, s, v=data_hsv.T
        background_areas=mask(h, target_background_h,
                              s, target_background_s,
                              v, target_background_v,
                              slop=target_background_tolerance
                              )
        
        #substitute a single color for what may be a variagated background
        data_hsv[background_areas.T] = new_background_hsv     
        
        #the hsv image, conveted back to RGB for display
        data_rgb=hsv_to_rgb(data_hsv) 
        data_rgb_255=(data_rgb* 255).astype(np.int8)
        
        im2 = Image.fromarray(data_rgb_255, "RGB")
        #im2.show()
        if not return_rgb:
            return data_hsv
        else:
            return im2


def get_color_list(im=None, 
                   target_background_tolerance=None,
                   back_r=None, 
                   back_g=None, 
                   back_b=None):
    
    """Ransacks an image and returns a list containing the palatte elements and what 
         pecent of the image contains each color.  Hard-coded logic screens out any
         color that's less than 1% of the total image"""
        
    #a sorted list of the most popular colors and the number of pixels of each
    colors=sorted(im.getcolors())
    
    #create a new list of sorted colors, counting up total pixel count
    draft_color_list=[]
    total_pixels=0
    #first pass count pixels, not including the background color
    
    for count, color in colors:
        #this checks whether this color is close to the background
        r, g, b, a = color
        is_back = mask(r, back_r, g, back_g, b, back_b, slop = target_background_tolerance)
        
        #if it's a "real" color, catelogue # of pixels and the RGB value
        if not is_back :  
            total_pixels += count
            draft_color_list.append((count, (r, g, b)))
    
    #revise the count to reflect a decimal version of the % each color represents
    #   skip anything under 1%
    color_list=[]

    for count, color in draft_color_list:
        pct = int(100* count/total_pixels)
        #print(count, total_pixels, pct)
        if pct >=1:
            color_list.append((pct, color))
    return color_list


def create_histogram(original_image_dir=None,
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
    """This routine creates a histogram of a reduced-palatte version of an original
        RBG, RGBA, or PNG image."""
    
    #replaces noisy background, reduces image to num_colors palatte
    im=reduce_image(original_image_dir=original_image_dir,
                          hsv_image_dir=hsv_image_dir,
                          original_image_file=original_image_file,
                          target_background_h=target_background_h,
                          target_background_s=target_background_s,
                          target_background_v=target_background_v,
                          target_background_tolerance=target_background_tolerance,
                          new_background_hsv=new_background_hsv,
                          num_colors=num_colors
                          ) 
    
    #this is the new, uniform background color (as RGB)
    background_rgb=hsv_to_rgb(np.array((new_background_hsv)))*255
    back_r, back_g, back_b = background_rgb 
    
    #returns a list of the colors and % of each
    color_list=get_color_list(im=im, 
                                target_background_tolerance=target_background_tolerance,
                                back_r=back_r, 
                                back_g=back_g, 
                                back_b=back_b
                                )

        
    
    #to visulize, we'll create a new np array.  We'll load each row
    # with color values - one column per percentage in image.  This results
    # in a crude histogram, mostly for debugging.
    
    default=np.array((255,255,255))  #the background color of the histo
    axis=np.array((255,0,0))         #the color of a bar at the bottom (to visualize scale)
    
    height=20  #height of each bar (pixels)
    width=10   #width of each bar (pixels)
    
    #create np array, pad it out w/ default color
    histo=np.zeros((len(color_list)*height +1, 100*width, 3   ))
    histo[:,:]=default
    
    #fill in color-coded bars (each the color of the pixels represented)
    rix=-1  #row index
    cix=-1  #column index
    for count, color in color_list:
        x=1
        for _ in range(height): #height of each bar
            rix+=1
            for _ in range(count):
                for _ in range(width):
                    cix+=1
                    histo[rix, cix,:]= color
            cix=-1
            a=1
            
    #add a bar to stake out 100%
    rix+=1
    for _ in range(100*width):
        histo[rix, cix,:]= axis
        cix+=1
                   
    im3=Image.fromarray(histo.astype(np.int8), "RGB")
    if show_histo:
        im3.show()
    return im3

def mask(c1, c1_target, c2, c2_target, c3, c3_target, slop=0):
    "given three channels return a mask for nearly-matching values"
    #
    mask= ((c1 >= c1_target - slop) & (c1 <= c1_target + slop)) &\
          ((c2 >= c2_target - slop) & (c2 <= c2_target + slop)) &\
          ((c3 >= c3_target - slop) & (c3 <= c3_target + slop)) 
    return mask

def RGBToHTMLColor(rgb_tuple):
    """ convert an (R, G, B) tuple to #RRGGBB """
    #http://code.activestate.com/recipes/266466-html-colors-tofrom-rgb-tuples/
    hexcolor = '#%02x%02x%02x' % rgb_tuple
    # that's it! '%02x' means zero-padded, 2-digit hex values
    return hexcolor

def stg2tup(stg):
    "convert a sting like '123,456,789' to a tuple like (123, 456, 789)"
    return tuple([int(i) for i in stg.split(',')] )

def tup2stg(tup):
    "convert a tuple like (123, 456, 789) to a string like '123, 456, 789'"
    return  ', '.join([str(i) for i in tup])




if __name__=='__main__':
    assert stg2tup('123, 456, 789')==(123, 456, 789)
    assert stg2tup('123,456,789')==(123, 456, 789)
    assert tup2stg((123, 456, 789))=='123, 456, 789'
    print('Yea! Tests passed')