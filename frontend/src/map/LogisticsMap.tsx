import { MapContainer, Marker, Polyline, Popup, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

import type { ClinicSummary, Village } from '../types';
import type { LiveLocation } from '../hooks/useLiveTracking';

type Props = {
  villages: Village[];
  clinics: ClinicSummary[];
  locations: Record<string, LiveLocation>;
};

function riskColor(risk: number): string {
  if (risk >= 0.7) return 'red';
  if (risk >= 0.4) return 'orange';
  return 'green';
}

export default function LogisticsMap({ villages, clinics, locations }: Props): JSX.Element {
  const center: [number, number] = villages.length ? [villages[0].latitude, villages[0].longitude] : [20.59, 78.96];

  return (
    <MapContainer center={center} zoom={6} className="h-[420px] w-full rounded-xl">
      <TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {villages.map((v) => (
        <Marker key={v.village_id} position={[v.latitude, v.longitude]}>
          <Popup>
            {v.name} <span style={{ color: riskColor(v.risk_score) }}>risk {v.risk_score.toFixed(2)}</span>
          </Popup>
        </Marker>
      ))}
      {clinics.map((clinic) => (
        <Polyline
          key={clinic.clinic_id}
          positions={clinic.route_coordinates.map((r) => [r.latitude, r.longitude])}
          pathOptions={{ color: clinic.clinic_id.endsWith('1') ? 'blue' : clinic.clinic_id.endsWith('2') ? 'purple' : 'teal' }}
        />
      ))}
      {Object.values(locations).map((loc) => (
        <Marker key={loc.clinic_id} position={[loc.lat, loc.lng]}>
          <Popup>
            {loc.clinic_id} at {loc.current_village}, ETA {loc.eta_next_stop}s
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
