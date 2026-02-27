import { useState } from 'react';

import ClinicSummaryPanel from '../components/ClinicSummary';
import ResourceTable from '../components/ResourceTable';
import UploadPanel from '../components/UploadPanel';
import { useLiveTracking } from '../hooks/useLiveTracking';
import LogisticsMap from '../map/LogisticsMap';
import { optimize, uploadCsv } from '../services/api';
import type { OptimizeResult } from '../types';

export default function App(): JSX.Element {
  const [result, setResult] = useState<OptimizeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const locations = useLiveTracking(Boolean(result));

  const handleUpload = async (files: { villages: File; outbreaks: File; resources: File }): Promise<void> => {
    const form = new FormData();
    form.append('villages', files.villages);
    form.append('outbreaks', files.outbreaks);
    form.append('resources', files.resources);
    await uploadCsv(form);
  };

  const runOptimization = async (useMock = false): Promise<void> => {
    setLoading(true);
    try {
      const data = await optimize(useMock);
      setResult(data);
    } finally {
      setLoading(false);
    }
  };

  const exportJson = (): void => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'optimization-results.json';
    link.click();
  };

  const exportCsv = (): void => {
    if (!result) return;
    const lines = ['clinic_id,route,total_distance'];
    result.clinics.forEach((c) => lines.push(`${c.clinic_id},"${c.route.join(' -> ')}",${c.total_distance}`));
    const blob = new Blob([lines.join('\n')], { type: 'text/csv' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'itinerary.csv';
    link.click();
  };

  return (
    <main className="mx-auto max-w-7xl space-y-4 p-4">
      <h1 className="text-2xl font-bold">Rural Health-Camp Logistics Dashboard</h1>
      <UploadPanel onUpload={handleUpload} />
      <div className="flex gap-2">
        <button className="rounded bg-emerald-600 px-4 py-2 text-white" onClick={() => runOptimization(false)}>
          Run Optimization
        </button>
        <button className="rounded bg-indigo-600 px-4 py-2 text-white" onClick={() => runOptimization(true)}>
          Run With Mock Data
        </button>
        <button className="rounded bg-slate-700 px-4 py-2 text-white" onClick={exportJson}>Export JSON</button>
        <button className="rounded bg-slate-700 px-4 py-2 text-white" onClick={exportCsv}>Export CSV</button>
        <button className="rounded bg-slate-700 px-4 py-2 text-white" onClick={() => window.print()}>Export PDF</button>
      </div>
      {loading && <p>Processing optimization...</p>}
      {result && (
        <>
          <LogisticsMap villages={result.villages} clinics={result.clinics} locations={locations} />
          <ClinicSummaryPanel clinics={result.clinics} />
          <ResourceTable clinics={result.clinics} />
        </>
      )}
    </main>
  );
}
