// Inserts an ad-card placeholder into the deck after every 6th real card.
// Only call this for free-tier (unsubscribed) users.
export function deckWithAds(cards, interval = 6) {
  const result = [];
  cards.forEach((card, i) => {
    result.push({ type: "card", data: card });
    if ((i + 1) % interval === 0 && i !== cards.length - 1) {
      result.push({ type: "ad" });
    }
  });
  return result;
}
