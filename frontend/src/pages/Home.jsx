import { useState } from "react";
import ChatInput from "../components/ChatInput";
import CardDeck from "../components/CardDeck";
import { generateCards } from "../lib/api";

export default function Home() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleGenerate(topic) {
    setLoading(true);
    const res = await generateCards(topic);
    setResult(res);
    setLoading(false);
  }

  return (
    <div className="min-h-screen bg-cream px-4 py-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">onion.cards</h1>
      <ChatInput onSubmit={handleGenerate} loading={loading} />
      {result && (
        <div className="mt-8">
          <CardDeck
            overview={result.overview}
            cards={result.cards}
            source={result.source}
            isSubscribed={false /* wire to real subscription status once auth is in */}
          />
        </div>
      )}
    </div>
  );
}
