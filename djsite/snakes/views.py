from django.http import HttpResponse
from django.shortcuts import render
import operator
from .models import SnakeInfo, SnakeColors

def index(request):
    
    colors = SnakeColors.objects  #==SELECT * 
    snakes = SnakeInfo.objects.order_by('species', 'id')
    objs_to_render=[]
    ids_to_render=[]
    species_to_render=[]
    filenames_to_render=[]
    for s in snakes:
        colors=SnakeColors.objects.filter(snake=s.id).order_by('-pct')
        objs_to_render.append(colors.all())
        ids_to_render.append(s.id)
        species_to_render.append(s.species)
        filenames_to_render.append(s.img_file)
        a=1
    #context={'snakes': objs_to_render, 'ids':ids_to_render}
    context={'snakes': zip(objs_to_render, ids_to_render, species_to_render, filenames_to_render)}
    return render(request, 'snakes/index.html', context)    
    #return HttpResponse("Hello, world. You're at the  index.")


def snakes(request):



    return HttpResponse("Hello, world. You're at snakes.")

def colors(request):
    return HttpResponse("Hello, world. You're at colors.")
def admin(request):
    return HttpResponse("Hello, world. You're at admin index.")
