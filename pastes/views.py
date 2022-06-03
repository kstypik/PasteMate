from django.shortcuts import render
from django.views.generic import CreateView

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
