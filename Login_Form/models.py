from django.db import models

class User(models.Model):
    username = models.CharField(max_length=50,unique=True)
    password = models.TextField()
    email=models.EmailField(null=True)

    def __str__(self):
        return self.name