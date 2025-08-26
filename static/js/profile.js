document.addEventListener('DOMContentLoaded', function() {
    const profileIcon = document.querySelector('.profile-icon');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    // Muestra/oculta el menú al hacer clic en el ícono
    profileIcon.addEventListener('click', function(event) {
        dropdownMenu.classList.toggle('active');
        // Previene que el evento de clic se propague al documento
        event.stopPropagation(); 
    });

    // Cierra el menú si se hace clic fuera de él
    document.addEventListener('click', function(event) {
        if (!dropdownMenu.contains(event.target) && dropdownMenu.classList.contains('active')) {
            dropdownMenu.classList.remove('active');
        }
    });
});