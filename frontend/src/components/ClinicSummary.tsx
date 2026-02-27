import type { ClinicSummary } from '../types';

type Props = { clinics: ClinicSummary[] };

export default function ClinicSummaryPanel({ clinics }: Props): JSX.Element {
  return (
    <div className="grid gap-3 md:grid-cols-2">
      {clinics.map((clinic) => (
        <div key={clinic.clinic_id} className="rounded-xl bg-white p-4 shadow">
          <h3 className="font-semibold">{clinic.clinic_id}</h3>
          <p className="text-sm">Distance: {clinic.total_distance} km</p>
          <p className="text-sm">Coverage Score: {clinic.coverage_score}</p>
          <p className="text-sm">Villages: {clinic.villages_assigned.join(', ')}</p>
        </div>
      ))}
    </div>
  );
}
