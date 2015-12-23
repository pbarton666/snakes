import numpy as np
from PIL import Image
from skimage import color as color

def mask(c1, c1_target, c2, c2_target, c3, c3_target, slop=0):
    "given three channels return a mask for nearly-matching values"
    mask= ((c1 >= c1_target - slop) & (c1 <= c1_target + slop)) &\
          ((c2 >= c2_target - slop) & (c2 <= c2_target + slop)) &\
          ((c3 >= c3_target - slop) & (c3 <= c3_target + slop)) 
    return mask

with Image.open("/home/pat/workspace/snakes/test_image_red.png") as im:
    im=im.convert("RGBA")
    data=np.array(im)
    red, green, blue, alpha = data.T
    #im=im.convert("HSV")
    #data=np.array(im)
    #h, s, v = data.T  
    #boolen mask of areas meeting criteria
    #background_areas=mask(h, 0, s, 76, v, 93, slop=3)
    #background_areas=(red == 238) & (blue == 57) & (green == 57)
    background_areas=mask(red, 238, blue, 57, green, 57, slop=1)
    #when transposed back to original, has same shape as original
    #data[..., :-1][white_areas.T] = (255, 0, 0) # Transpose back needed
    data[background_areas.T] = (0, 0, 0, 0) # Transpose back needed

    im2 = Image.fromarray(data)
    im2.save('test_image_red1.png')
    im2.show()    
    
    im=im.convert("RGB")
    data=np.array(im)
    #data=data/255
    hsv=color.rgb2hsv(data)
    #hsv=color.rgb2hsv(im.convert("RGB"))  
    im3 = Image.fromarray(hsv, "HSV")
    im3.save('test_image_hsv.png')
    im3.show()
    a=1