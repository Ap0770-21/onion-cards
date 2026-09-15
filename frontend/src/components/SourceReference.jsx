import { useState } from "react";

export default function SourceReference({ source }) {
  const [open, setOpen] = useState(false);
  if (!source) return null;

  return (
    <div className="mb-4 text-sm">
      <button onClick={() => setOpen((o) => !o)} className="text-accent underline">
        Sourced from {source.documents.join(", ")}
      </button>
      {open && (
        <div className="mt-2 space-y-2">
          {source.passages.map((p, i) => (
            <p key={i} className="bg-cream border border-accent/20 rounded p-3 text-gray-600 text-xs">
              {p}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
