from unimarket.models import Item, Member, ReviewScore
from django.forms import ModelForm

# 지환
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms


class FileUploadForm(ModelForm):
    class Meta:
        model = Item
        fields = ["title", "catNo", "price", "info", "itemImg"]


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = Member
        fields = [
            "password",
            "nickname",
            "gender",
            "marrStat",
            "proImg",
            "loc",
            "zonecode",
        ]
