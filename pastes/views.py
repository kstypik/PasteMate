from django.shortcuts import render
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

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


class PasteUpdateView(UpdateView):
    form_class = PasteForm
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    context_object_name = "paste"
    template_name = "pastes/form.html"
    extra_context = {
        "action_type": "Edit",
    }

    def get_queryset(self):
        return Paste.objects.filter(author=self.request.user)


class PasteDeleteView(DeleteView):
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    success_url = "/"
    context_object_name = "paste"
    template_name = "pastes/delete.html"

    def get_queryset(self):
        return Paste.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.title if self.object.title else "Untitled"
        return context
