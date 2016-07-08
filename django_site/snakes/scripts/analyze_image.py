import os
import sys
#import matplotlib
#import psycopg2

#import numpy as np
#from PIL import Image
#from matplotlib.colors import hsv_to_rgb, rgb_to_hsv
#from utilities import create_histogram, filter_background, mask
#from utilities import reduce_image, get_color_list
#from utilities import RGBToHTMLColor, collect_image_data
#from utilities import collect_image_data, make_png_thumb
from utilities import add_image_to_database, add_directory_to_database
#from snake_settings import *  #background colors, etc.
#from database_routines import get_connector, make_tables
#import dominant_to_alpha

##TODO: use the hsv_image_dir to point to the html img reference.
##Save appropriate full-scale version there

'''next steps:
      - store thumbnails and full images in web-accessible location
      - get additional images on Dropbox
      - add content to contextualize
      - add thumbs and links to background info'''


        

if __name__=='__main__':
        #add all the images in a directory in the form:
        #  ball_python_1.png
        #to the database, using file name as species
        
        original_image_dir="/home/pat/workspace/snakes/snakes/static"
        
        hsv_image_dir="/home/pat/workspace/snakes/snakes/static/thumbs"
        add_directory_to_database(original_image_dir=original_image_dir, 
                                  hsv_image_dir=hsv_image_dir, 
                                  db='snakes') 

    

    