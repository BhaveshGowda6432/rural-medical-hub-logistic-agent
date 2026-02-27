import { useState } from 'react';

type Props = {
  onUpload: (files: { villages: File; outbreaks: File; resources: File }) => Promise<void>;
};

export default function UploadPanel({ onUpload }: Props): JSX.Element {
  const [files, setFiles] = useState<Partial<Record<'villages' | 'outbreaks' | 'resources', File>>>({});

  return (
    <div className="rounded-xl bg-white p-4 shadow">
      <h2 className="mb-3 text-lg font-semibold">CSV Upload</h2>
      {(['villages', 'outbreaks', 'resources'] as const).map((field) => (
        <label key={field} className="mb-3 block text-sm font-medium">
          {field}.csv
          <input
            className="mt-1 block w-full rounded border p-2"
            type="file"
            accept=".csv"
            onChange={(e) => e.target.files?.[0] && setFiles((f) => ({ ...f, [field]: e.target.files![0] }))}
          />
        </label>
      ))}
      <button
        className="rounded bg-blue-600 px-4 py-2 text-white"
        onClick={() => {
          if (files.villages && files.outbreaks && files.resources) {
            onUpload({ villages: files.villages, outbreaks: files.outbreaks, resources: files.resources });
          }
        }}
      >
        Upload CSVs
      </button>
    </div>
  );
}
