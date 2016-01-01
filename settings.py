#Number of colors into which we'll reduce the images as an initial processing step
#   This makes a more manageable palatte at the expense of some small details not important
#   to the purpose of this task
num_colors=10

#These parameters describe the "ideal" background in terms of the HSV model.  
target_background_h=0
target_background_s=.76
target_background_v=.93

#In the field, the background will likely become discolored from dirt, etc.
#  so here, we provide a tolerance factor.  Any image that matches the ideal
#  color +/- the tolerance in each of the color model dimensions will be deemed
#  background and will be redacted
target_background_tolerance=.01

#The image background will be replaced with this value before it's stored.  The replacement
#  happens whether the image has an alpha channel or not.
new_background_hsv=(0, 1, 1)

need_new_tables=False #blows out existing tables and replaces with new.  Use w/ caution.