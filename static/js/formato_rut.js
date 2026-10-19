/**
 * Formateador Oficial de RUT Chileno (XX.XXX.XXX-Y)
 * Ilustre Municipalidad de La Serena - Sistema SGR
 *
 * Aplica automáticamente el formato con puntos y guión al ingresar números
 * en cualquier campo de RUT de los formularios.
 */

(function() {
    'use strict';

    /**
     * Limpia y formatea un string como RUT chileno
     * @param {string} valor 
     * @returns {string} RUT con formato XX.XXX.XXX-Y o X.XXX.XXX-Y
     */
    function formatearRut(valor) {
        if (!valor) return '';

        // Eliminar caracteres que no sean dígitos o K
        let limpio = valor.toString().replace(/[^0-9kK]/g, '').toUpperCase();
        if (limpio.length === 0) return '';

        // Limitar a 9 caracteres (8 dígitos cuerpo + 1 dígito verificador)
        if (limpio.length > 9) {
            limpio = limpio.slice(0, 9);
        }

        // Si solo hay 1 caracter, retornarlo tal cual
        if (limpio.length === 1) {
            return limpio;
        }

        // El cuerpo solo puede contener números, la K solo en el dígito verificador
        const cuerpo = limpio.slice(0, -1).replace(/[^0-9]/g, '');
        const dv = limpio.slice(-1);

        if (!cuerpo) {
            return dv;
        }

        // Formatear cuerpo con puntos de miles de derecha a izquierda
        const cuerpoConPuntos = cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

        return cuerpoConPuntos + '-' + dv;
    }

    /**
     * Valida si un RUT chileno es válido según Módulo 11
     * @param {string} rutCompleto 
     * @returns {boolean}
     */
    function validarRut(rutCompleto) {
        if (!rutCompleto) return false;
        const limpio = rutCompleto.toString().replace(/[^0-9kK]/g, '').toUpperCase();
        if (limpio.length < 8 || limpio.length > 9) return false;

        const cuerpo = limpio.slice(0, -1);
        const dv = limpio.slice(-1);

        let suma = 0;
        let multiplo = 2;
        for (let i = cuerpo.length - 1; i >= 0; i--) {
            suma += parseInt(cuerpo[i], 10) * multiplo;
            multiplo = multiplo < 7 ? multiplo + 1 : 2;
        }
        const dvEsperado = 11 - (suma % 11);
        const dvCalc = dvEsperado === 11 ? '0' : (dvEsperado === 10 ? 'K' : dvEsperado.toString());

        return dv === dvCalc;
    }

    /**
     * Asocia los eventos de formateo en tiempo real a un elemento input
     * @param {HTMLInputElement} input 
     */
    function activarFormatoRut(input) {
        if (!input || input.dataset.rutActivo === 'true') return;
        input.dataset.rutActivo = 'true';

        // Atributos recomendados para experiencia móvil y desktop
        input.setAttribute('maxlength', '12');
        input.setAttribute('autocomplete', 'off');
        input.setAttribute('spellcheck', 'false');

        // Formatear en tiempo real mientras el usuario escribe
        input.addEventListener('input', function(e) {
            const valorAnterior = this.value;
            const posCursor = this.selectionStart || 0;

            // Contar cuántos caracteres válidos (números o K) había antes del cursor
            const textoAntes = valorAnterior.slice(0, posCursor);
            const validosAntes = textoAntes.replace(/[^0-9kK]/g, '').length;

            const valorFormateado = formatearRut(valorAnterior);
            this.value = valorFormateado;

            // Recalcular posición del cursor para que no salte al final
            let validosContados = 0;
            let nuevaPos = valorFormateado.length;

            for (let i = 0; i < valorFormateado.length; i++) {
                if (/[0-9kK]/i.test(valorFormateado[i])) {
                    validosContados++;
                }
                if (validosContados >= validosAntes) {
                    nuevaPos = i + 1;
                    break;
                }
            }

            // Si se borró todo
            if (validosAntes === 0) {
                nuevaPos = 0;
            }

            try {
                this.setSelectionRange(nuevaPos, nuevaPos);
            } catch (err) {
                // En navegadores que no admitan setSelectionRange en ciertos tipos
            }
        });

        // Manejar Backspace para saltar puntos o guión sin trabarse
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace') {
                const pos = this.selectionStart;
                if (pos === this.selectionEnd && pos > 0) {
                    const charAnterior = this.value[pos - 1];
                    if (charAnterior === '.' || charAnterior === '-') {
                        e.preventDefault();
                        const antes = this.value.slice(0, pos - 2);
                        const despues = this.value.slice(pos);
                        this.value = formatearRut(antes + despues);
                        const nuevaPos = Math.max(0, pos - 2);
                        try {
                            this.setSelectionRange(nuevaPos, nuevaPos);
                        } catch (err) {}
                    }
                }
            }
        });

        // Asegurar formato limpio al perder el foco
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = formatearRut(this.value);
            }
        });

        // Formatear si ya viene con valor inicial
        if (input.value) {
            input.value = formatearRut(input.value);
        }
    }

    /**
     * Inicializa todos los inputs identificados como RUT en la página
     */
    function inicializarTodos() {
        // Buscar inputs de RUT por clase, id o name (excluyendo cajas de búsqueda global tipo name="q")
        const selectores = [
            'input.formato-rut',
            'input[data-tipo="rut"]',
            'input[name*="rut" i]:not([name="q"])',
            'input[id*="rut" i]:not([id*="search"]):not([id*="buscar"])'
        ];

        document.querySelectorAll(selectores.join(',')).forEach(activarFormatoRut);
    }

    // Exponer helpers en window
    window.formatearRut = formatearRut;
    window.validarRut = validarRut;
    window.activarFormatoRut = activarFormatoRut;

    // Ejecutar al cargar el DOM y ante mutaciones (por si se abren modales o AJAX)
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializarTodos);
    } else {
        inicializarTodos();
    }

    // Observador para elementos dinámicos que se inserten después
    if (window.MutationObserver) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(m) {
                m.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) {
                        if (node.matches && (
                            node.matches('input.formato-rut') ||
                            node.matches('input[data-tipo="rut"]') ||
                            node.matches('input[name*="rut" i]:not([name="q"])') ||
                            node.matches('input[id*="rut" i]')
                        )) {
                            activarFormatoRut(node);
                        }
                        if (node.querySelectorAll) {
                            inicializarTodos();
                        }
                    }
                });
            });
        });
        observer.observe(document.body || document.documentElement, { childList: true, subtree: true });
    }
})();
