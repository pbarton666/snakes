import os

import numpy as np
from PIL import Image
from utilities import hsv_to_rgb, rgb_to_hsv, mask
from filter_background import filter_background



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

def analyze_image(original_image_dir=None,
                      hsv_image_dir=None,
                      original_image_file=None,
                      target_background_h=None,
                      target_background_s=None,
                      target_background_v=None,
                      target_background_tolerance=None,
                      new_background_hsv=None
                      ):
    """This routine assumes an RGBA image, with background already represented
       as alpha (transparent).  It converts all non-background pixels to HSV and
       stores them in another 'image' for color frequency analysis."""
    colors=5
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
    h, w = im.size
    #im.show()
    #img_as_data=np.array(im)
    #this reduces the image to a specified number of colors, then converts it
    # back to the RGBA color model
    im=im.convert('P', palette=Image.ADAPTIVE, colors=colors)
    im=im.convert("RGBA")
    
    #a sorted list of the most popular colors and the number of pixels of each
    colors=sorted(im.getcolors())
    #create a new list of sorted colors, counting up total pixel count
    draft_color_list=[]
    total_pixels=0
    #first pass count pixels, not including the background color
    
    for count, color in colors:
        #this checks whether this color is close to the background
        r, g, b, a = color
        is_back = mask(r, back_r, g, back_g, b, back_b, slop = 1)
        #if it's a "real" color, catelogue # of pixels and the RGB value
        
        if not is_back :  
            total_pixels += count
            draft_color_list.append((count, (r, g, b)))
    
    #revise the count to reflect a decimal version of the % each color represents
    #   skip anything under 1%
    color_list=[]
    default=np.array((255,255,255))
    axis=np.array((255,0,0))
    for count, color in draft_color_list:
        pct = int(100* count/total_pixels)
        print(count, total_pixels, pct)
        if pct >=1:
            color_list.append((pct, color))
    
    #to visulize, we'll create a new np array.  We'll load each row
    # with color values - one column per percentage in image
    height=20
    width=10
    
    histo=np.zeros((len(color_list)*height +1, 100*width, 3   ))
    histo[:,:]=default
    rix=-1
    cix=-1
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
    im3.show()
    r, g, b, a = img_as_data.T
    
    h, w = img_as_data.size
    
    new_histo=new_image.histogram()
    new_colors=new_image.getcolors(w*h)  #a list of tuples [count (rgba), ...]
    new_image.save(saveas) 


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
    
    
    
    #gather up all the non-background pixels and create image for chromatic analysis
    
    #add and alpha channel
    
    return data_hsv        
        #can we save the hsv data as an image (even if we can't view it easily)?
if __name__=='__main__':
    original_image_dir="/home/pat/workspace/snakes"
    hsv_image_dir="/home/pat/workspace/snakes"
    original_image_file="test_image_red.png"     
    
    #test(original_image_dir,original_image_file)
    target_background_h=0
    target_background_s=.76
    target_background_v=.93
    target_background_tolerance=.01
    new_background_hsv=(0, 1, 1)
   
    fb=analyze_image(original_image_dir=original_image_dir,
                          hsv_image_dir=hsv_image_dir,
                          original_image_file=original_image_file,
                          target_background_h=target_background_h,
                          target_background_s=target_background_s,
                          target_background_v=target_background_v,
                          target_background_tolerance=target_background_tolerance,
                          new_background_hsv=new_background_hsv
                          )    
    im2 = Image.fromarray(fb, "RGB")
    im2.show()
    a=1
    ###Next step:  create 'flat' image of only the non-background pixels
    