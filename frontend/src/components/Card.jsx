import { useState } from "react";
import { updateCard } from "../lib/api";

export default function Card({ card }) {
  const [editing, setEditing] = useState(false);
  const [question, setQuestion] = useState(card.question);
  const [answer, setAnswer] = useState(card.answer);
  const [favorite, setFavorite] = useState(card.favorite);
  const [flipped, setFlipped] = useState(false);

  async function save() {
    if (card.id) await updateCard(card.id, { question, answer });
    setEditing(false);
  }

  async function toggleFavorite(e) {
    e.stopPropagation();
    const next = !favorite;
    setFavorite(next);
    if (card.id) await updateCard(card.id, { favorite: next });
  }

  return (
    <div
      className="rounded-xl border border-accent/30 bg-white p-6 shadow-sm cursor-pointer min-h-32"
      onClick={() => !editing && setFlipped((f) => !f)}
    >
      <div className="flex justify-between items-start mb-2">
        <span className="text-xs uppercase tracking-wide text-gray-400">
          {flipped ? "Answer" : "Question"}
        </span>
        <button onClick={toggleFavorite} className="text-accent">
          {favorite ? "★" : "☆"}
        </button>
      </div>

      {editing ? (
        <div onClick={(e) => e.stopPropagation()} className="space-y-2">
          <textarea className="w-full border rounded p-2 text-sm" value={question} onChange={(e) => setQuestion(e.target.value)} />
          <textarea className="w-full border rounded p-2 text-sm" value={answer} onChange={(e) => setAnswer(e.target.value)} />
          <button onClick={save} className="text-sm bg-accent text-white px-3 py-1 rounded">Save</button>
        </div>
      ) : (
        <>
          <p className="text-gray-800">{flipped ? answer : question}</p>
          <button
            onClick={(e) => { e.stopPropagation(); setEditing(true); }}
            className="mt-3 text-xs text-gray-400 underline"
          >
            Edit
          </button>
        </>
      )}
    </div>
  );
}
