import type { ClinicSummary } from '../types';

type Props = { clinics: ClinicSummary[] };

export default function ResourceTable({ clinics }: Props): JSX.Element {
  const keys = Array.from(new Set(clinics.flatMap((c) => Object.keys(c.allocated_resources))));

  return (
    <div className="rounded-xl bg-white p-4 shadow">
      <h3 className="mb-2 font-semibold">Resource Allocation</h3>
      <div className="overflow-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr>
              <th className="border px-2 py-1 text-left">Clinic</th>
              {keys.map((k) => (
                <th key={k} className="border px-2 py-1 text-left">{k}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {clinics.map((clinic) => (
              <tr key={clinic.clinic_id}>
                <td className="border px-2 py-1">{clinic.clinic_id}</td>
                {keys.map((k) => (
                  <td key={`${clinic.clinic_id}-${k}`} className="border px-2 py-1">{clinic.allocated_resources[k] ?? 0}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
