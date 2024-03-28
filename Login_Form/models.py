from django.db import models


class User(models.Model):
    Roles = (
    (1, "Employee"),
    (2, "Manager"),
  )
     
    username = models.CharField(max_length=50, unique=True)
    password = models.TextField()
    roles = models.IntegerField(choices=Roles, default=1)
    email=models.EmailField()
    image=models.ImageField(null=True,upload_to='Login_Form/media')

    def __str__(self):
        return self.name
class Task(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        primary_key=True,
    )
    username = models.CharField(max_length=50,unique=True)
    task = models.CharField(max_length=100)
    task_status=models.CharField(max_length=100,default="Pending")

class Comments(models.Model):
    user=models.OneToOneField(
        Task,
        on_delete=models.PROTECT,
        primary_key=True,
    )
    username = models.CharField(max_length=50,unique=True)
    comments = models.CharField(max_length=100)