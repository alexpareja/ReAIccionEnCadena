from django.shortcuts import render, redirect
from .forms import RegistroFormulario


def index(request):
    return render(request, 'index.html')
# Create your views here.
def registro(request):
    if request.method == 'POST':
        form = RegistroFormulario(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirige a la página de inicio o a donde prefieras
    else:
        form = RegistroFormulario()

    return render(request, 'registro.html', {'form': form})


