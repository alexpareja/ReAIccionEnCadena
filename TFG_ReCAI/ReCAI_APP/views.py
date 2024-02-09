from django.shortcuts import render, redirect
from .forms import RegistroFormulario
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import openai
#from ReCAI_APP import settings


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

def game(request):
    return render(request, 'game.html')


#@csrf_exempt
#def chatgpt_api(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        response = chatgpt_request(message)
        return JsonResponse({'response': response})
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'})
    
#def chatgpt_request(message):
    openai.api_key = settings.OPENAI_API_KEY
    model = "text-davinci-003"  # Puedes cambiar el modelo según tus preferencias

    response = openai.Completion.create(
        engine=model,
        prompt=message,
        max_tokens=150
    )

    return response.choices[0].text.strip()