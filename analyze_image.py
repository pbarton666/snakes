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

##TODO: use the hsv_image_dir to point to the html img reference.
##Save appropriate full-scale version there

'''next steps:
      - store thumbnails and full images in web-accessible location
      - get additional images on Dropbox
      - add content to contextualize
      - add thumbs and links to background info'''

def add_image_to_database(original_image_dir=None,
                          hsv_image_dir=None,
                          original_image_file=None,
                          target_background_h=None,
                          target_background_s=None,
                          target_background_v=None,
                          target_background_tolerance=None,
                          new_background_hsv=None,
                          num_colors=None,
                          db=None, 
                          source='dummy_source',
                          species='monty_python',
                          identifying_authority='None',
                          ):
        
        '''Adds an image to the database, after first having removed the background
              color'''
        conn=get_connector(db=db)
        curs = conn.cursor()         
        
        #get RGB, HSV, and html colors from a reduced-color form of 
        #  the image (background, number of colors, etc come from settings.py)
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
        if not os.path.exists(hsv_image_dir):
                os.path.create(hsv_image_dir)
        
        thumb_filename=os.path.join(hsv_image_dir, 
                                  os.path.splitext(original_image_file)[0] +
                                     "_thumb.png"
                                     )
        img.save(thumb_filename)
    
        
        sql="""INSERT INTO snake_info  (thumb_file, species, img_file, identifying_authority, source)
                    VALUES('{}','{}','{}','{}','{}')
                    RETURNING id"""\
                .format(thumb_filename, 
                        species,
                        os.path.join(original_image_dir, original_image_file),
                        identifying_authority,
                        source)
                                                               
        curs.execute(sql)
        snake_id = curs.fetchone()[0]
        
        ##TODO: local file name; make relative for web app
        for color in img_dict['pik_data']:
                sql="""INSERT INTO snake_colors  (pct, r, g, b, h, s, v, html, snake_id)
                            VALUES({}, {}, {},{},{},{},{}, '{}', {})""".format(
                            color['pct'],
                            color['r'],
                            color['g'],
                            color['b'],
                            color['h'],
                            color['s'],
                            color['v'],
                            color['html'],
                            snake_id)
        
                curs.execute(sql)
        conn.commit()

 

if __name__=='__main__':
        #add all the images in a directory in the form:
        #  ball_python_1.png
        #to the database, using file name as species
        original_image_dir="/home/pat/workspace/snakes/images"
        hsv_image_dir="/home/pat/workspace/snakes/images/thumbs"
        for f in os.listdir(original_image_dir):
                #f='indigo_1.png'
                if os.path.isfile(os.path.join(original_image_dir, f)):
                        #species is the filename less the trailing '_##.png' bit
                        species=' '.join(os.path.splitext(f)[0].split('_')[:-1])
                        original_image_file=f
                        add_image_to_database(original_image_dir=original_image_dir,
                                                  hsv_image_dir=hsv_image_dir,
                                                  original_image_file=original_image_file,
                                                  target_background_h=target_background_h,
                                                  target_background_s=target_background_s,
                                                  target_background_v=target_background_v,
                                                  target_background_tolerance=target_background_tolerance,
                                                  new_background_hsv=new_background_hsv,
                                                  num_colors=num_colors,
                                                  db='snakes', 
                                                  source='dummy_source',
                                                  species=species,
                                                  identifying_authority='None',
                                              )    
    
    
    
    
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
    

    