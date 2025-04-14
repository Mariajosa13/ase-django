document.addEventListener('DOMContentLoaded', function () {
    // Validar cantidad en la página de detalles
    const cantidadInput = document.getElementById('cantidad');
    if (cantidadInput) {
        cantidadInput.addEventListener('change', function () {
            const max = parseInt(this.getAttribute('max'));
            const value = parseInt(this.value);

            if (value < 1) {
                this.value = 1;
            } else if (value > max) {
                this.value = max;
                alert(`Solo hay ${max} unidades disponibles.`);
            }
        });
    }

    // Previsualización de imagen en la página de detalles
    const miniaturas = document.querySelectorAll('.miniatura');
    if (miniaturas.length > 0) {
        const imagenPrincipal = document.getElementById('imagen-principal');

        miniaturas.forEach(img => {
            img.addEventListener('click', function () {
                imagenPrincipal.src = this.getAttribute('data-img-large');

                // Quitar clase activa de todas las miniaturas
                miniaturas.forEach(m => m.classList.remove('active'));

                // Agregar clase activa a la miniatura seleccionada
                this.classList.add('active');
            });
        });
    }

    // Ordenar productos
    const ordenSelect = document.getElementById('id_orden');
    if (ordenSelect) {
        ordenSelect.addEventListener('change', function () {
            document.querySelector('form').submit();
        });
    }

    // Filtro de rango de precios
    const rangeInputs = document.querySelectorAll('.range-input');
    if (rangeInputs.length === 2) {
        const precioMin = document.getElementById('id_precio_min');
        const precioMax = document.getElementById('id_precio_max');

        rangeInputs.forEach(input => {
            input.addEventListener('input', function () {
                if (this.id === 'range-min') {
                    precioMin.value = this.value;
                } else {
                    precioMax.value = this.value;
                }
            });
        });
    }

    // Animaciones para productos destacados
    const productosDestacados = document.querySelectorAll('.producto-destacado');
    if (productosDestacados.length > 0) {
        productosDestacados.forEach(producto => {
            producto.addEventListener('mouseenter', function () {
                this.classList.add('destacado-hover');
            });

            producto.addEventListener('mouseleave', function () {
                this.classList.remove('destacado-hover');
            });
        });
    }

    // Vista previa rápida de productos
    const botonesVistaPrevia = document.querySelectorAll('.btn-vista-previa');
    if (botonesVistaPrevia.length > 0) {
        const modalVistaPrevia = document.getElementById('modal-vista-previa');
        const modalTitulo = document.getElementById('modal-titulo');
        const modalImagen = document.getElementById('modal-imagen');
        const modalPrecio = document.getElementById('modal-precio');
        const modalDescripcion = document.getElementById('modal-descripcion');
        const modalEnlace = document.getElementById('modal-enlace');

        botonesVistaPrevia.forEach(boton => {
            boton.addEventListener('click', function (e) {
                e.preventDefault();

                const productoId = this.getAttribute('data-producto-id');

                // Simular petición Ajax (reemplazar con petición real)
                fetch(`/api/productos/${productoId}/`)
                    .then(response => response.json())
                    .then(data => {
                        modalTitulo.textContent = data.nombre;
                        modalImagen.src = data.imagen;
                        modalPrecio.textContent = `$${data.precio}`;
                        modalDescripcion.textContent = data.descripcion;
                        modalEnlace.href = data.url;

                        // Mostrar modal
                        modalVistaPrevia.classList.add('show');
                        modalVistaPrevia.style.display = 'block';
                    });
            });
        });
    }
});
