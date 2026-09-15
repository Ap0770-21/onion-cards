import { supabase } from "./supabase";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function authHeaders() {
  const { data } = await supabase.auth.getSession();
  const token = data?.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function generateCards(topic) {
  const res = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(await authHeaders()) },
    body: JSON.stringify({ topic }),
  });
  return res.json();
}

export async function uploadDocument(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/upload/document`, {
    method: "POST",
    headers: await authHeaders(),
    body: form,
  });
  return res.json();
}

export async function generateFromDoc(topic) {
  const form = new FormData();
  form.append("topic", topic);
  const res = await fetch(`${API_BASE}/upload/generate-from-doc`, {
    method: "POST",
    headers: await authHeaders(),
    body: form,
  });
  return res.json();
}

export async function updateCard(cardId, updates) {
  const res = await fetch(`${API_BASE}/cards/${cardId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...(await authHeaders()) },
    body: JSON.stringify(updates),
  });
  return res.json();
}
