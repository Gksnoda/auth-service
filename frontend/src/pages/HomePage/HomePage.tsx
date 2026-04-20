import { Navigate, useLocation } from 'react-router-dom';

function decodeJwtPayload(token: string): Record<string, unknown> {
  const base64url = token.split('.')[1];
  const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
  return JSON.parse(atob(base64));
}

export function HomePage() {
  const location = useLocation();
  const state = location.state as { token?: string; refreshToken?: string } | null;
  const token = state?.token;
  const refreshToken = state?.refreshToken;

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  const payload = decodeJwtPayload(token);

  return (
    <main className="min-h-dvh px-6 py-10 font-sans">
      <div className="mx-auto max-w-3xl flex flex-col gap-6">
        <h1 className="font-heading text-3xl font-bold">Token info</h1>

        <section>
          <h2 className="mb-2 text-sm font-semibold tracking-wider text-muted-foreground">
            ACCESS TOKEN
          </h2>
          <pre className="overflow-x-auto break-all rounded-md border bg-muted p-4 text-xs whitespace-pre-wrap">
            {token}
          </pre>
        </section>

        <section>
          <h2 className="mb-2 text-sm font-semibold tracking-wider text-muted-foreground">
            DECODED PAYLOAD
          </h2>
          <pre className="overflow-x-auto rounded-md border bg-muted p-4 text-xs">
            {JSON.stringify(payload, null, 2)}
          </pre>
        </section>

        {refreshToken ? (
          <section>
            <h2 className="mb-2 text-sm font-semibold tracking-wider text-muted-foreground">
              REFRESH TOKEN
            </h2>
            <pre className="overflow-x-auto break-all rounded-md border bg-muted p-4 text-xs whitespace-pre-wrap">
              {refreshToken}
            </pre>
          </section>
        ) : null}
      </div>
    </main>
  );
}
