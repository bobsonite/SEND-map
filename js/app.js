mapboxgl.accessToken = 'pk.eyJ1IjoiYm9ic29uaXRlIiwiYSI6ImNtOXpyeWc1aDFlY24ya3M3dm55a2oyNDcifQ.8H2wkga07prlTm_YpOQicA';

const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/light-v11',
  center: [-1.5, 53.5],
  zoom: 5.6
});

map.on('load', () => {
  map.addSource('suspensions', {
    type: 'geojson',
    data: 'data/processed/LASuspensionrate.geojson'
  });

  map.addLayer({
    id: 'suspensions-fill',
    type: 'fill',
    source: 'suspensions',
    paint: {
      'fill-color': '#088',
      'fill-opacity': 0.5
    }
  });

  map.on('click', 'suspensions-fill', (e) => {
    const props = e.features[0].properties;
    new mapboxgl.Popup()
      .setLngLat(e.lngLat)
      .setHTML(`<strong>${props.la_name}</strong><br>Suspension rate: ${props.suspension_rate_label}`)
      .addTo(map);
  });

  map.on('mouseenter', 'suspensions-fill', () => {
    map.getCanvas().style.cursor = 'pointer';
  });

  map.on('mouseleave', 'suspensions-fill', () => {
    map.getCanvas().style.cursor = '';
  });
});