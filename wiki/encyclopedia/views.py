from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from . import util
from markdown2 import markdown
from random import choice
from django import forms

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    content = util.get_entry(title)
    if content == None:
        return HttpResponse("error no page exist")
    
    return render(request, "encyclopedia/entry.html", {
        "title" : title,
        "content" : markdown(content)
    })

def search(request):
    query = request.GET["q"].lower()
    entry_list = [n.lower() for n in util.list_entries()]
    if query in entry_list:
        return redirect(entry, query)
    else:
        results = [entry for entry in entry_list if query in entry]
        return render(request, "encyclopedia/index.html", {
            "entries": results
            })

def random(request):
    entries = util.list_entries()
    entry = choice(entries)
    content = util.get_entry(entry)
    return render(request, "encyclopedia/entry.html", {
        "title" :  entry,
        "content" : markdown(content)
    })

class NewForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control', 'id' : 'titleBox'}))
    content = forms.CharField( required=False, widget=forms.Textarea(attrs={'class': 'form-control'}))

def create(request):
    if (request.method == "POST"):
        currForm = NewForm(request.POST)
        if (currForm.is_valid()):
            title = currForm.cleaned_data["title"]
            if title in util.list_entries():
                return render(request, "encyclopedia/create.html", {
                    "form": currForm,
                    "message" : "your title already in the list"
                })
            content = currForm.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect(entry, title)
    return render(request, "encyclopedia/create.html", {
        "form" : NewForm(),
        "message" : ""
    })

def edit(request, title):

    if request.method == "GET":
        content = util.get_entry(title)

        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content" : content
        })
    elif request.method == "POST":
        form = request.POST
        title = form.get("title")
        content = form['content']
        util.save_entry(title, content)
        return redirect(entry, title)


