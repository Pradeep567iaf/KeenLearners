from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from .models import User,Room  # import user and room models

class MyUserCreationForm(UserCreationForm):
  class Meta:
    model = User
    fields = ['name','username','email','password1','password2']


class RoomForm(ModelForm):
  class Meta:
    model = Room
    fields = '__all__'
    exclude = ['host','participants']
    # fields = ['name','description']

class UserForm(ModelForm):
  class Meta:
    model = User
    # fields = '__all__'
    fields = ['avatar','name','username','email','bio']
