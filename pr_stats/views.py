from django.shortcuts import render
from django.http import HttpResponse

def index(results):
    return HttpResponse("PRs are so cool")
