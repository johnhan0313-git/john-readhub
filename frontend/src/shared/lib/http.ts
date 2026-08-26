import { API_BASE } from "@/shared/lib/env";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}

export async function request<T>(
  path: string,
  options?: RequestInit & { revalidate?: number | false },
): Promise<T> {
  const { revalidate, ...init } = options ?? {};
  const next =
    revalidate === false
      ? undefined
      : revalidate != null
        ? { revalidate }
        : undefined;

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...(next ? { next } : {}),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new ApiError(text || res.statusText, res.status);
  }
  return res.json();
}
