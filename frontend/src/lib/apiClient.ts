const VITE_API_URL = import.meta.env.VITE_API_URL;

if (typeof VITE_API_URL !== 'string' || VITE_API_URL.length === 0) {
  throw new Error('VITE_API_URL is not defined. Copy .env.example to .env and set it.');
}

const BASE_URL: string = VITE_API_URL;

export class ApiError extends Error {
  readonly status: number;
  readonly detail: string | null;

  constructor(status: number, message: string, detail: string | null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

export class NetworkError extends Error {
  constructor() {
    super('Network error — please check your connection.');
    this.name = 'NetworkError';
  }
}

async function parseJsonSafe(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

function extractDetail(parsed: unknown): string | null {
  if (parsed && typeof parsed === 'object' && 'detail' in parsed) {
    const { detail } = parsed as { detail: unknown };
    if (typeof detail === 'string') return detail;
  }
  return null;
}

export const apiClient = {
  async post<TResponse, TBody>(path: string, body: TBody): Promise<TResponse> {
    const url = `${BASE_URL}${path}`;
    console.log('[API Request]', { method: 'POST', url, body });

    let response: Response;
    try {
      response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
    } catch {
      throw new NetworkError();
    }

    const parsed = await parseJsonSafe(response);
    console.log('[API Response]', { method: 'POST', url, status: response.status, body: parsed });

    if (!response.ok) {
      const detail = extractDetail(parsed);
      const message = detail ?? 'Server error. Please try again.';
      throw new ApiError(response.status, message, detail);
    }

    return parsed as TResponse;
  },
};
