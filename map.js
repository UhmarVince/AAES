/**
 * AAES Real-World Reach Map
 * Powered by Leaflet.js & Architectural Dark Tiles
 */

const AAES_LOCATIONS = [
    { name: 'Metro Manila', coords: [14.5995, 120.9842], stats: 'Residential Structural Design' },
    { name: 'Cebu City', coords: [10.3157, 123.8854], stats: 'Infrastructure Projects | Industrial Design' },
    { name: 'Davao Region', coords: [7.1907, 125.4553], stats: 'Multilevel Steel Structure Design' },
    { name: 'Aurora', coords: [15.7570, 121.5654], stats: 'Structural Design of Merchandise Store' },
    { name: 'Laguna', coords: [14.2773, 121.4167], stats: 'Industrial Facilities | Strength Testing' },
    { name: 'Albay', coords: [13.1391, 123.7438], stats: 'Steel Warehouse Design' },
    { name: 'Calbayog City, Samar', coords: [12.0676, 124.5942], stats: 'Steel Warehouse Design' }
];

class RealReachMap {
    constructor() {
        this.map = null;
        this.init();
    }

    init() {
        // Initialize Map centered on Philippines
        this.map = L.map('aaes-real-map', {
            center: [12.8797, 121.7740],
            zoom: 6,
            zoomControl: false,
            scrollWheelZoom: false // Premium feel: don't hijack scroll
        });

        // Add Dark Theme Tiles (CartoDB Dark Matter - Zero Setup / Open Access)
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 20,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        }).addTo(this.map);

        L.control.zoom({
            position: 'bottomright'
        }).addTo(this.map);

        // Ensure map layout is accurate after load
        setTimeout(() => {
            this.map.invalidateSize();
        }, 500);

        this.renderMarkers();
    }

    renderMarkers() {
        AAES_LOCATIONS.forEach(loc => {
            // Custom Neon Pulsating Icon
            const icon = L.divIcon({
                className: 'aaes-real-pin-wrapper',
                html: `
                    <div class="aaes-real-pin-glow"></div>
                    <div class="aaes-real-pin"></div>
                `,
                iconSize: [10, 10],
                iconAnchor: [5, 5]
            });

            const marker = L.marker(loc.coords, { icon: icon }).addTo(this.map);

            // Precision Popup (Glassmorphism Styled)
            marker.bindPopup(`
                <div class="aaes-map-popup">
                    <h4>${loc.name}</h4>
                    <p>${loc.stats}</p>
                </div>
            `, {
                closeButton: false,
                className: 'aaes-glass-popup'
            });

            // Interaction
            marker.on('mouseover', function (e) {
                this.openPopup();
            });
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Ensure Leaflet is loaded
    if (typeof L !== 'undefined') {
        window.aaesRealMap = new RealReachMap();
    }
});
