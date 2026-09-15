import Card from "./Card";
import AdCard from "./AdCard";
import SourceReference from "./SourceReference";
import { deckWithAds } from "../lib/deckWithAds";

export default function CardDeck({ overview, cards, source, isSubscribed }) {
  const items = isSubscribed ? cards.map((c) => ({ type: "card", data: c })) : deckWithAds(cards);

  return (
    <div className="space-y-4">
      {overview && <p className="text-gray-600 italic">{overview}</p>}
      <SourceReference source={source} />
      <div className="grid gap-4">
        {items.map((item, i) =>
          item.type === "ad" ? <AdCard key={`ad-${i}`} /> : <Card key={item.data.id || i} card={item.data} />
        )}
      </div>
    </div>
  );
}
