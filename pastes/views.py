from django.shortcuts import render
from django.views.generic import CreateView, DetailView

from .forms import PasteForm
from .models import Paste


class PasteCreateView(CreateView):
    model = Paste
    form_class = PasteForm
    template_name = "pastes/create.html"

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
        return super().form_valid(form)


class PasteDetailView(DetailView):
    model = Paste
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    context_object_name = "paste"
    template_name = "pastes/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.title if self.object.title else "Untitled"
        return context
