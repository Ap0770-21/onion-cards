export default function AdCard() {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <p className="text-xs uppercase tracking-wide text-gray-400 mb-2">Sponsored</p>
      {/* AdSense unit goes here once you have a publisher ID.
          Google's contextual targeting reads nearby page/topic text automatically. */}
      <div className="h-24 flex items-center justify-center text-gray-300 text-sm">
        Ad slot
      </div>
    </div>
  );
}
