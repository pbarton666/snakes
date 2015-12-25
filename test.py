import os

import numpy as np
from PIL import Image
from utilities import hsv_to_rgb, rgb_to_hsv, mask



def test(original_image_dir=None,original_image_file=None ):
    'ss'
    with Image.open(os.path.join(original_image_dir,original_image_file)) as im:
        #im.show()
        img_as_data=np.array(im)
        r, g, b, a = img_as_data.T
        background_areas=mask(r, 238,
                              g, 57,
                              b, 57,
                              slop=10
                              )
        
        #substitute a single color for what may be a variagated background
        img_as_data[background_areas.T] = (255,0,0,255)   
        clean = Image.fromarray(img_as_data, "RGBA")
        #clean.show()
        colors=20
        reduced=clean.convert('P', palette=Image.ADAPTIVE, colors=colors)
        reduced.show()
        quantized=clean.quantize(colors=colors)
        quantized.show()

        reduc2 = reduced.convert('RGB') #turns it to rgb
        #reduc2_hist0 = reduc2.histogram()
        reduc_fn = 'scratch.BMP'
        reduc2.save(reduc_fn)
        xxx = Image.open(reduc_fn)
        xxx=xxx.convert('RGB')
        #xconverted_image = raw_image.convert('RGBA')
        xxx_histo=xxx.histogram()
        h, w = xxx.size
        xreduced_colors=xxx.getcolors(w*h)
        xxx.close()    

def filter_background(original_image_dir=None,
                      hsv_image_dir=None,
                      original_image_file=None,
                      target_background_h=None,
                      target_background_s=None,
                      target_background_v=None,
                      target_background_tolerance=None,
                      new_background_hsv=None
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
        im2.show()
        
        return data_hsv

        
        #can we save the hsv data as an image (even if we can't view it easily)?
if __name__=='__main__':
    original_image_dir="/home/pat/workspace/snakes"
    hsv_image_dir="/home/pat/workspace/snakes"
    original_image_file="test_image_red.png"     
    
    test(original_image_dir,original_image_file)
    target_background_h=0
    target_background_s=.76
    target_background_v=.93
    target_background_tolerance=.01
    new_background_hsv=(0, 1, 1)
   
    filter_background(original_image_dir=original_image_dir,
                          hsv_image_dir=hsv_image_dir,
                          original_image_file=original_image_file,
                          target_background_h=target_background_h,
                          target_background_s=target_background_s,
                          target_background_v=target_background_v,
                          target_background_tolerance=target_background_tolerance,
                          new_background_hsv=new_background_hsv
                          )    
    
    ###Next step:  create 'flat' image of only the non-background pixels
    