from django.db import models
from werkzeug.security import check_password_hash

class User(models.Model):
    username = models.CharField(max_length=50,unique=True)
    password = models.TextField()
    confirm_password=models.TextField(null=True)
    email=models.EmailField(null=True)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __str__(self):
        return self.name