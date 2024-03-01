document.addEventListener('DOMContentLoaded', function() {
    var idPalabra = document.getElementById('idPalabra').value;
    var palabraElement = document.getElementById(idPalabra);
    
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
