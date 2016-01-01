import os
import sys
import matplotlib
import psycopg2

import numpy as np
from PIL import Image
from matplotlib.colors import hsv_to_rgb, rgb_to_hsv
from utilities import create_histogram, filter_background, mask
from utilities import reduce_image, get_color_list
from utilities import RGBToHTMLColor, collect_image_data
from utilities import collect_image_data, make_png_thumb
from settings import *  #background colors, etc.
from database_routines import get_connector, make_tables
import dominant_to_alpha



 

if __name__=='__main__':
    original_image_dir="/home/pat/workspace/snakes"
    hsv_image_dir="/home/pat/workspace/snakes"
    #original_image_file="test_image_red.png"  
    original_image_file="test_image.png" 
    
    conn=get_connector(db='snakes')
    curs = conn.cursor() 
    
    need_new_tables=False
    table='snake_id'
    if need_new_tables:
        make_tables()
    
    img_dict=collect_image_data(original_image_dir=original_image_dir,
                          hsv_image_dir=hsv_image_dir,
                          original_image_file=original_image_file,
                          target_background_h=target_background_h,
                          target_background_s=target_background_s,
                          target_background_v=target_background_v,
                          target_background_tolerance=target_background_tolerance,
                          new_background_hsv=new_background_hsv,
                          num_colors=num_colors
                          )  
    
    #convert Image object to thumbnail
    img=make_png_thumb(img_dict['image'], new_background_hsv)
    thumb='test_thumb.png'
    img.save('test_thumb.png')
    source='test_source'
    
    species='ball_python'
    img_file=os.path.join(original_image_dir, original_image_file)
    sql="""INSERT INTO {}  (thumb, species, img_file, r, g, b, h, s, v, html, source)
                VALUES('{}','{}','{}',{},{},{},{},{},{}, '{}','{}')""".format(
                table,
                thumb,
                species,
                img_file,
                img_dict['r'],
                img_dict['g'],
                img_dict['b'],
                img_dict['h'],
                img_dict['s'],
                img_dict['v'],
                img_dict['html'],
                source)

    curs.execute(sql)
    conn.commit()
    #note this transforms image to thumbnailt['image'].thumbnail((50,50))
    print(fb)
    a=1
    
    
    #number of colors preserved in palette reduction
   
    #fb=create_histogram(original_image_dir=original_image_dir,
                          #hsv_image_dir=hsv_image_dir,
                          #original_image_file=original_image_file,
                          #target_background_h=target_background_h,
                          #target_background_s=target_background_s,
                          #target_background_v=target_background_v,
                          #target_background_tolerance=target_background_tolerance,
                          #new_background_hsv=new_background_hsv,
                          #num_colors=num_colors
                          #) 
    
    #fb.show()
    
  

    ###Next step:  create 'flat' image of only the non-background pixels
    