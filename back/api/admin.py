from django.contrib import admin
from .models import Category, Task, Comment, TaskHistory

admin.site.register(Category)
admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(TaskHistory)