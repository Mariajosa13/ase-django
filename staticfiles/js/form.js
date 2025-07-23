const container = document.getElementById('container');
    const registerBtn = document.getElementById('register');
    const loginBtn = document.getElementById('login');

    registerBtn.addEventListener('click', () => {
        container.classList.add("active");
    });

    loginBtn.addEventListener('click', () => {
        container.classList.remove("active");
    });

    function mostrarCamposEspecificos() {
        // IMPORTANT: The ID will now be prefixed by Django's form rendering.
        // It will be 'id_signup-tipo_usuario'
        const tipoUsuarioSelect = document.getElementById('id_signup-tipo_usuario'); 
        
        const camposCliente = document.getElementById('campos_cliente');
        const camposDomiciliario = document.getElementById('campos_domiciliario');
        const camposTienda = document.getElementById('campos_tienda');

        // Hide all fields first
        if (camposCliente) camposCliente.style.display = 'none';
        if (camposDomiciliario) camposDomiciliario.style.display = 'none';
        if (camposTienda) camposTienda.style.display = 'none';

        // Show fields based on selected user type
        const selectedValue = tipoUsuarioSelect.value;
        if (selectedValue === 'cliente') {
            if (camposCliente) camposCliente.style.display = 'block';
        } else if (selectedValue === 'domiciliario') {
            if (camposDomiciliario) camposDomiciliario.style.display = 'block';
        } else if (selectedValue === 'tienda') {
            if (camposTienda) camposTienda.style.display = 'block';
        }
    }

    // Call the function on page load to set initial state
    document.addEventListener('DOMContentLoaded', mostrarCamposEspecificos);