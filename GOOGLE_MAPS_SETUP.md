<!-- Instructions for adding Google Maps API key to rent.html -->

## How to Enable Google Maps in Property Listing

### Step 1: Get Your Google Maps API Key
1. Go to https://console.cloud.google.com/google/maps-apis/overview
2. Create or select a project
3. Enable "Maps JavaScript API"
4. Create an API key in Credentials section
5. Restrict the key to your domain (localhost:8000/* for development)

### Step 2: Update the Template
In `Room/templates/rent.html`, replace the placeholder section with this code:

```html
<!-- Replace this section in rent.html -->
<div class="form-row">
  <label>Location (Click on map to select)</label>
  <div class="input">
    <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY_HERE&libraries=places&callback=initMap" async defer></script>
    <div id="map" style="height: 300px; width: 100%; border-radius: 8px; margin-bottom: 10px;"></div>
    <input type="hidden" id="latitude" name="latitude">
    <input type="hidden" id="longitude" name="longitude">
    <p style="font-size: 12px; color: #666; margin: 5px 0;">Click on the map above to set the property location. Coordinates will be saved automatically.</p>
  </div>
</div>

<script>
let map;
let marker;

// Initialize map when page loads
window.initMap = function() {
  initMap();
};

function initMap() {
  // Default location (India center)
  const defaultLocation = { lat: 20.5937, lng: 78.9629 };

  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 5,
    center: defaultLocation,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  });

  // Add click listener to place marker
  map.addListener('click', function(event) {
    placeMarker(event.latLng);
  });

  // Try to get user's current location
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      const userLocation = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      };
      map.setCenter(userLocation);
      map.setZoom(15);
      placeMarker(new google.maps.LatLng(userLocation.lat, userLocation.lng));
    }, function(error) {
      console.log('Geolocation error:', error);
    });
  }
}

function placeMarker(location) {
  if (marker) {
    marker.setPosition(location);
  } else {
    marker = new google.maps.Marker({
      position: location,
      map: map,
      draggable: true
    });

    // Add drag listener
    marker.addListener('dragend', function(event) {
      updateCoordinates(event.latLng);
    });
  }

  updateCoordinates(location);
}

function updateCoordinates(location) {
  document.getElementById('latitude').value = location.lat();
  document.getElementById('longitude').value = location.lng();
}
</script>
```

### Step 3: Replace YOUR_API_KEY_HERE
Replace `YOUR_API_KEY_HERE` with your actual Google Maps API key.

### Step 4: Test
Restart your Django server and test the property listing page. The map should now load and allow location selection.