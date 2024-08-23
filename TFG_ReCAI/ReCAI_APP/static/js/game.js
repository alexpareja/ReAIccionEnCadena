document.addEventListener('DOMContentLoaded', function() {
    var idPalabra = document.getElementById('idPalabra').value;
    var palabraElement = document.getElementById(idPalabra);
    document.getElementById('campo_respuesta').focus();    
    if (palabraElement) {
        palabraElement.style.backgroundColor = ''; // Quita el color de fondo
        palabraElement.classList.add('palabraactual'); // Agrega la clase palabraactual
    }
});


document.addEventListener('DOMContentLoaded', () => {
    const grupos = document.querySelectorAll('#panel');

    grupos.forEach(grupo => {
        const invisibles = grupo.querySelectorAll('.invisible');
        const elementosPermitidos = [];
        // Añade el primer elemento invisible al array si existe
        if (invisibles.length > 0) {
            elementosPermitidos.push(invisibles[0]);
        }
        // Añade el último elemento invisible al array si este es diferente al primero y existe
        if (invisibles.length > 1) {
            elementosPermitidos.push(invisibles[invisibles.length - 1]);
        }

        invisibles.forEach(item => {
            item.addEventListener('click', function() {
                // Verifica si el elemento está permitido y no está bloqueado.
                if (!elementosPermitidos.includes(this) || this.classList.contains('blocked')) {
                    // Si no está permitido o está bloqueado, no hacer nada.
                    return;
                }

                // Verifica si el texto aún no ha sido revelado parcialmente.
                if (!this.classList.contains('partially-revealed')) {
                    const originalText = this.textContent;
                    this.innerHTML = `<span class="revealed-text">${originalText[0]}</span>` + '<span style="visibility:hidden;">' + originalText.slice(1) + '</span>';
                    this.classList.add('partially-revealed'); // Marca el elemento como modificado.

                    // Guarda el texto original del elemento seleccionado en localStorage.
                    localStorage.setItem('palabraSeleccionada', originalText);
                }

                // Añade la clase 'blocked' a todos los otros elementos para prevenir más interacciones.
                invisibles.forEach(otherItem => {
                    otherItem.classList.add('blocked');
                });
            });
        });
    });
});

/*
    document.addEventListener('DOMContentLoaded', () => {
        const invisibles = document.querySelectorAll('#panel .invisible');
        let revealingElement = null; // Almacena el elemento que está siendo revelado

        invisibles.forEach(item => {
            item.dataset.revealedCount = 0;

            item.addEventListener('click', function() {
                if (revealingElement && revealingElement !== this) return; // Ignora el clic si no es el elemento en revelación

                const maxReveal = this.textContent.length;
                let revealedCount = parseInt(this.dataset.revealedCount);

                if (revealedCount < maxReveal) {
                    revealingElement = this; // Establece el elemento actual como el elemento en revelación
                    const originalText = this.textContent;
                    revealedCount++;
                    this.dataset.revealedCount = revealedCount;

                    const visibleText = originalText.substr(0, revealedCount);
                    const hiddenText = originalText.substr(revealedCount);

                    this.innerHTML = `<span class="revealed-text">${visibleText}</span>` + '<span style="visibility:hidden;">' + hiddenText + '</span>';

                    if (!this.classList.contains('partially-revealed')) {
                        this.classList.add('partially-revealed');
                    }

                    // Cuando se haya revelado completamente, cambia la clase del elemento
                    if (revealedCount === maxReveal) {
                        revealingElement = null; // Resetea el elemento en revelación
                        this.classList.remove('invisible', 'partially-revealed'); // Remueve clases que indiquen estado previo
                        this.classList.add('visible'); // Añade la clase 'visible' para indicar que está completamente revelado
                    }
                }
            });
        });
});
*/

function seleccionarPalabra(elemento) {
    var esSeleccionable = document.getElementById('esSeleccionable');
    var idP =  document.getElementById('palabra_elegida');
    let form = document.getElementById('formSeleccionarPalabra');
    if (esSeleccionable.value == 1 && elemento.classList.contains("activo")){
        idP.value = elemento.id;
        form.submit()
    }
}

document.addEventListener('DOMContentLoaded', function() {

    var actualizarActivos= document.getElementById('actualizarActivos')
    if(actualizarActivos == null){
        borrarEstilos();
    }

    var elementos = document.querySelectorAll('#panel li');
    elementos.forEach(function(elemento) {
        var estiloGuardado = localStorage.getItem(elemento.id);
        if (estiloGuardado) {
            elemento.classList = estiloGuardado;
        }
    });

    var actualizarActivos= document.getElementById('actualizarActivos')
    var idP =  document.getElementById('palabra_elegida');
    var liPalabraElegida =  document.getElementById(idP.value);
    var esSeleccionable = document.getElementById('esSeleccionable');
    if (esSeleccionable.value == 1){
        jug = document.getElementById('turno_actual').value;
        if ((jug == "IA") | (jug == 'IA 1') | (jug == 'IA 2')){
            seleccionarPalabraIA();
            console.log(jug);
        }
    }
    if (actualizarActivos) {
        //ver si es turno de la IA
        liPalabraElegida.classList.remove('activo');
        liPalabraElegida.classList.add('resuelto');
        localStorage.setItem(liPalabraElegida.id, liPalabraElegida.classList)
        var liAnterior = document.getElementById('p'+ String(parseInt(liPalabraElegida.id[1])-1));
        var liPosterior = document.getElementById('p'+ String(parseInt(liPalabraElegida.id[1])+1));
        console.log(liAnterior);
        console.log(liPosterior);

        if (liAnterior != null){
            if(!liAnterior.classList.contains('resuelto')){
                liAnterior.classList.add('activo');
                localStorage.setItem(liAnterior.id, liAnterior.classList)
            }
        }
        else{
            if(parseInt(liPalabraElegida.id[1]) == 5){
                liAnteriorAnterior = document.getElementById('p'+ String(parseInt(liPalabraElegida.id[1])-2));
                if(!liAnteriorAnterior.classList.contains('resuelto')){
                    liAnteriorAnterior.classList.add('activo');
                    localStorage.setItem(liAnteriorAnterior.id, liAnteriorAnterior.classList)
    
                }
            }
        }
        if (liPosterior != null){
            if(!liPosterior.classList.contains('resuelto')){
                liPosterior.classList.add('activo');
                localStorage.setItem(liPosterior.id, liPosterior.classList)

            }
        }
        else{
            if(parseInt(liPalabraElegida.id[1]) == 3){
                liPosteriorPosterior = document.getElementById('p'+ String(parseInt(liPalabraElegida.id[1])+2));
                if(!liPosteriorPosterior.classList.contains('resuelto')){
                    liPosteriorPosterior.classList.add('activo');
                    localStorage.setItem(liPosteriorPosterior.id, liPosteriorPosterior.classList)
    
                }
            }
        }
        actualizarActivos = false;
    }
});

function borrarEstilos(){
    localStorage.clear();
}

function seleccionarPalabraIA() {
    // Generar un número aleatorio entre 1 y el número total de recuadros
    var ids = [];
    var elementosActivos = document.querySelectorAll('li.activo');
    
    elementosActivos.forEach(function(elemento) {
        ids.push(elemento.id);
    });

    var indiceAleat = Math.floor(Math.random() * ids.length);
    var elementoAleat = ids[indiceAleat];

    // Simular un clic en el recuadro seleccionado por la IA
    document.getElementById(elementoAleat).click();
    
    console.log(document.getElementById(elementoAleat), elementoAleat, indiceAleat, elementosActivos);
  }

/*function obtenerIdsActivos() {
    var ids = [];
    var elementosActivos = document.querySelectorAll('li.activo');
    
    elementosActivos.forEach(function(elemento) {
        ids.push(elemento.id);
    });
    
    // Envía los IDs al backend (en este caso, a la URL '/ruta/de/tu/vista/')
    fetch('/centro_de_la_cadena/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}' // Asegúrate de incluir el token CSRF si estás utilizando Django forms
        },
        body: JSON.stringify({ ids: ids })
    })
    .then(response => {
        // Maneja la respuesta del servidor si es necesario
        console.log('IDs enviados al backend');
    })
    .catch(error => {
        console.error('Error al enviar los IDs al backend:', error);
    });
}*/