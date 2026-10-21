import { supabase } from "./supabase";

const API_URL = import.meta.env.VITE_API_URL;

/** An error from our API. `message` is the API's `detail` text, ready to show. */
export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

type Options = {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
};

/** Call our FastAPI with the logged-in user's token. Throws ApiError on any non-2xx. */
export async function api<T>(path: string, options: Options = {}): Promise<T> {
  const response = await send(path, options);
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

/** Like api, for a file such as a PDF: returns its bytes instead of JSON. */
export async function apiBlob(path: string): Promise<Blob> {
  return (await send(path)).blob();
}

async function send(path: string, { method = "GET", body }: Options = {}): Promise<Response> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;

  const response = await fetch(`${API_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (!response.ok) {
    throw new ApiError(response.status, await detailFrom(response));
  }
  return response;
}

// Our errors are {"detail": "..."}; FastAPI's own input errors are
// {"detail": [{"msg": "..."}, ...]}.
async function detailFrom(response: Response): Promise<string> {
  try {
    const { detail } = await response.json();
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map((d) => d.msg).join("; ");
  } catch {
    // Not JSON: fall through to the generic message.
  }
  return `Request failed (${response.status})`;
}
