from django.contrib import admin 
  
# Register your models here. 
from .models import Agent, Container, Host
  
admin.site.register(Agent)
admin.site.register(Host)
admin.site.register(Container)
