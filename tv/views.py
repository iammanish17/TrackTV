from django.shortcuts import render
import requests
from bs4 import BeautifulSoup


def home(request):
    return render(request, 'tv/home.html')


def search(request, query: str = ""):
    if not query:
        return render(request, 'tv/search.html')
    url = "http://api.tvmaze.com/search/shows?q=%s" % query
    resp = requests.get(url).json()
    if not resp:
        return render(request, 'tv/search.html', {'query': query})
    else:
        for each in resp:
            if each["show"]["summary"]:
                each["show"]["summary"] = BeautifulSoup(each["show"]["summary"], "lxml").text
            if not each["show"]["image"]:
                each["show"]["image"] = {"original":"/static/tv/default.png"}
        context = {
            'results': resp,
            'query': query
        }
        return render(request, 'tv/search.html', context)
