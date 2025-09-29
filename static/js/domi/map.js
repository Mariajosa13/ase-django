let map;
let domiciliarioMarker;
let pedidosMarkers = {};

function initMap() {
    console.log("map.js cargado");
    const medellinCordenadas = [6.2442, -75.5812];

    // mapa leaFlet
    map = L.map('map').setView(medellinCordenadas, 13) // centra en Medellín con zoom 13

    //diseño
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    // obtener ubicación del domiciliario
    if (navigator.geolocation){
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                const pos = [lat, lng];

                map.setView(pos, 16); // centra en la ubi real del domi

                const motoIcon = L.icon({
                    iconUrl: '/static/img/moto.png',
                    iconSize: [40, 40],
                });

                domiciliarioMarker = L.marker(pos, { icon: motoIcon }).addTo(map)
                .bindPopup("¡Estás aquí!");

                cargarPedidosCercanos(lat, lng);

                // iniciarRastreoWebSocket({ lat, lng }); para rastreo con WebSocket en tiempo real
            },

            () => {
                console.error("Geolocalización falló");
            }
        );
    }
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function cargarPedidosCercanos(lat, lng) {
    const url = '/domiciliario/pedidos/cercanos/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'), 
        },
        body: JSON.stringify({
            latitude: lat,
            longitude: lng
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.features) {
            data.features.forEach(feature => {
                const coords = feature.geometry.coordinates;
                const pedido_id = feature.properties.id;
                const distancia = feature.properties.distancia_a_domiciliario;
                
                const pedidoIcon = L.icon({
                    iconUrl: '/static/img/pedido.jpeg', 
                    iconSize: [32, 32],
                });

                const marker = L.marker([coords[1], coords[0]], { icon: pedidoIcon }).addTo(map);
                
                marker.bindPopup(`
                    <b>Pedido #${pedido_id}</b><br>
                    Distancia: ${distancia} metros.<br>
                    <button onclick="tomarPedido(${pedido_id})">Tomar Pedido</button>
                `);

                pedidosMarkers[pedido_id] = marker;
            });
        }
    })
    .catch(error => {
        console.error("Error al cargar pedidos cercanos:", error);
    });
}

document.addEventListener('DOMContentLoaded', initMap); // Inicializa cuando la página cargue
