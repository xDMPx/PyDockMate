from django.contrib import admin 
  
# Register your models here. 
from .models import Agent, Host
  
admin.site.register(Agent)
admin.site.register(Host)
