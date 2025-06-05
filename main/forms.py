from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from .models import Libro, Foro, PublicacionForo
from django.contrib.auth.models import User




class ForoForm(forms.ModelForm):
    class Meta:
        model = Foro
        fields = ['libro', 'titulo_del_foro', 'participantes']
        widgets = {
            'libro': ModelSelect2Widget(
                model=Libro,
                search_fields=['titulo_del_libro__icontains'],
                attrs={'data-placeholder': 'Selecciona un libro'}
            ),
            'participantes': ModelSelect2MultipleWidget(
                model=User,
                search_fields=['username__icontains'],
                attrs={'data-placeholder': 'Selecciona participantes'}
            )
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)
        if user:
            self.fields['participantes'].queryset = User.objects.exclude(id=user.id)

class PublicacionForoForm(forms.ModelForm):
    class Meta:
        model = PublicacionForo
        fields = ['mensaje']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mensaje'].widget.attrs.update({
            'class': 'foro-textarea-inline',
            'placeholder': 'Escribe tu mensaje...'
        })



class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo_del_libro', 'autor', 'genero', 'resumen', 'foto_perfil']



