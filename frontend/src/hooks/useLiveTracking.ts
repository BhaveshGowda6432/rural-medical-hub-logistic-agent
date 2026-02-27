import { useEffect, useState } from 'react';

import { locationSocket } from '../services/api';

export type LiveLocation = {
  clinic_id: string;
  lat: number;
  lng: number;
  current_village: string;
  eta_next_stop: number;
};

export function useLiveTracking(active: boolean): Record<string, LiveLocation> {
  const [locations, setLocations] = useState<Record<string, LiveLocation>>({});

  useEffect(() => {
    if (!active) return;
    const ws = locationSocket();

    ws.onmessage = (event: MessageEvent<string>) => {
      const data = JSON.parse(event.data) as LiveLocation;
      setLocations((prev) => ({ ...prev, [data.clinic_id]: data }));
    };

    return () => ws.close();
  }, [active]);

  return locations;
}
