from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.urls import path
import markdown2
from . import util
from django import forms
from django.shortcuts import redirect
import random



def index(request):
    """  
        Renders the index page with a list of all encyclopedia entries.
    """
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })
def entry(request, title):
    """    Renders a specific encyclopedia entry page.
    If the entry does not exist, it renders an error page.
    """
    # Retrieve the content of the entry
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "requested page was not found."
        })
    html_content = markdown2.markdown(content)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content
    })

def search(request):
    """    Handles search requests for encyclopedia entries.
    If an exact match is found, redirects to that entry.
    Otherwise, returns a list of entries that contain the search query as a substring.
    """
    query = request.GET.get("q", "")
    entries = util.list_entries()

    # Check for exact match (case-insensitive)
    for entry in entries:
        if entry.lower() == query.lower():
            return HttpResponseRedirect(reverse("entry", args=[entry]))

    # Otherwise, find substring matches
    results = [entry for entry in entries if query.lower() in entry.lower()]

    return render(request, "encyclopedia/search.html", {
        "query": query,
        "results": results
    })

class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label="Content", widget=forms.Textarea)

def new_page(request):
    """    Handles the creation of a new encyclopedia entry.
    If the form is submitted with valid data, it saves the entry and redirects to the new entry page.
    If an entry with the same title already exists, it returns an error message.
    """
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            if util.get_entry(title):
                return render(request, "encyclopedia/error.html", {
                    "message": f"An entry with the title '{title}' already exists."
                })
            full_content = f"# {title}\n\n{content}"
            util.save_entry(title, full_content)
            return HttpResponseRedirect(reverse("entry", args=[title]))
    else:
        form = NewEntryForm()

    return render(request, "encyclopedia/new.html", {
        "form": form
    })

def edit_page(request, title):
    """    Handles the editing of an existing encyclopedia entry.
    If the form is submitted with valid data, it saves the updated entry and redirects to the entry page.
    """
    if request.method == "POST":
        content = request.POST.get("content")
        util.save_entry(title, content)
        return redirect("entry", title=title)

    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "Page not found."
        })

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": content
    })


def random_page(request):
    """    Redirects to a random encyclopedia entry.
    """
    entries = util.list_entries()
    random_title = random.choice(entries)
    return redirect("entry", title=random_title)



    





    
    ...
