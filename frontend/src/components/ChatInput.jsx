import { useState } from "react";

export default function ChatInput({ onSubmit, loading }) {
  const [topic, setTopic] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (!topic.trim()) return;
    onSubmit(topic);
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        className="flex-1 rounded-lg border border-accent/40 px-4 py-3 bg-white"
        placeholder="Enter a topic (e.g. 'Krebs cycle')"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
      />
      <button
        type="submit"
        disabled={loading}
        className="rounded-lg bg-accent text-white px-5 py-3 font-medium disabled:opacity-50"
      >
        {loading ? "..." : "Generate"}
      </button>
    </form>
  );
}
