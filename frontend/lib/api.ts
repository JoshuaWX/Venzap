export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'https://venzap-api.onrender.com';

export type ApiResult<T> = {
  ok: boolean;
  data?: T;
  error?: string;
  status: number;
};

async function parseJsonSafe(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) {
    return null;
  }
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return null;
  }
}

function extractError(payload: unknown, fallback: string): string {
  if (!payload || typeof payload !== 'object') {
    return fallback;
  }

  const obj = payload as Record<string, unknown>;
  const detail = obj.detail;
  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  const err = obj.error;
  if (err && typeof err === 'object') {
    const codeObj = err as Record<string, unknown>;
    if (typeof codeObj.message === 'string' && codeObj.message.trim()) {
      return codeObj.message;
    }
  }

  return fallback;
}

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
): Promise<ApiResult<T>> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(init.headers || {}),
    },
  });

  const payload = await parseJsonSafe(response);

  if (!response.ok) {
    return {
      ok: false,
      status: response.status,
      error: extractError(payload, 'Request failed'),
    };
  }

  return {
    ok: true,
    status: response.status,
    data: payload as T,
  };
}
