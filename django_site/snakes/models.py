from django.db import models

class SnakeColors(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    pct = models.IntegerField(blank=True, null=True)
    r = models.IntegerField(blank=True, null=True)
    b = models.IntegerField(blank=True, null=True)
    g = models.IntegerField(blank=True, null=True)
    h = models.FloatField(blank=True, null=True)
    s = models.FloatField(blank=True, null=True)
    v = models.FloatField(blank=True, null=True)
    html = models.CharField(max_length=8, blank=True, null=True)
    snake = models.ForeignKey('SnakeInfo', models.DO_NOTHING, blank=True, null=True)
    
    def __str__(self):
            return "snake {} color {}".format(self.snake, self.id)    

    class Meta:
        managed = False
        db_table = 'snake_colors'


class SnakeInfo(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    thumb_file = models.CharField(max_length=120, blank=True, null=True)
    orig_image_file = models.CharField(max_length=120, blank=True, null=True)
    web_image_file = models.CharField(max_length=120, blank=True, null=True)
    species = models.CharField(max_length=50, blank=True, null=True)
    identifying_authority = models.CharField(max_length=100, blank=True, null=True)
    img_file = models.CharField(max_length=80, blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return "snake_{}".format(self.id)    

    class Meta:
        managed = False
        db_table = 'snake_info'


class SnakeId(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    thumb = models.CharField(max_length=80, blank=True, null=True)
    species = models.CharField(max_length=50, blank=True, null=True)
    img_file = models.CharField(max_length=80, blank=True, null=True)
    r = models.IntegerField(blank=True, null=True)
    b = models.IntegerField(blank=True, null=True)
    g = models.IntegerField(blank=True, null=True)
    h = models.FloatField(blank=True, null=True)
    s = models.FloatField(blank=True, null=True)
    v = models.FloatField(blank=True, null=True)
    html = models.CharField(max_length=8, blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return "snake_{}".format(self.id)
    
    

    class Meta:
        managed = True
        db_table = 'snake_id'
