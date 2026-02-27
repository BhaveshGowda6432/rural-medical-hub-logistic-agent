import type { OptimizeResult } from '../types';

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export async function uploadCsv(formData: FormData): Promise<void> {
  await fetch(`${BASE}/upload-data`, { method: 'POST', body: formData });
}

export async function optimize(useMock = false): Promise<OptimizeResult> {
  const res = await fetch(`${BASE}/optimize?use_mock=${useMock}`, { method: 'POST' });
  return res.json();
}

export function locationSocket(): WebSocket {
  return new WebSocket(`${BASE.replace('http', 'ws')}/ws/locations`);
}
