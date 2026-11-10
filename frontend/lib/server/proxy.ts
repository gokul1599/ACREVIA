export async function proxyToBackend(
  req: Request,
  subpath: string
): Promise<Response | null> {
  const rawBackendUrl =
    process.env.BACKEND_INTERNAL_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "";

  if (!rawBackendUrl) return null;

  let backendUrl = rawBackendUrl.trim().replace(/\/+$/, "");
  if (backendUrl.endsWith("/api/v1")) {
    backendUrl = backendUrl.slice(0, -"/api/v1".length);
  } else if (backendUrl.endsWith("/api")) {
    backendUrl = backendUrl.slice(0, -"/api".length);
  }

  const cleanSubpath = subpath.startsWith("/") ? subpath.slice(1) : subpath;
  const targetUrl = `${backendUrl}/api/v1/${cleanSubpath}`;

  try {
    const headers = new Headers(req.headers);
    headers.delete("host");

    let body: BodyInit | null = null;
    if (req.method !== "GET" && req.method !== "HEAD") {
      body = await req.clone().arrayBuffer();
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);

    const backendRes = await fetch(targetUrl, {
      method: req.method,
      headers,
      body,
      signal: controller.signal,
    });
    clearTimeout(timeout);

    const resHeaders = new Headers(backendRes.headers);
    resHeaders.delete("content-encoding");

    return new Response(backendRes.body, {
      status: backendRes.status,
      statusText: backendRes.statusText,
      headers: resHeaders,
    });
  } catch {
    // Backend unreachable, fallback to serverless handler
    return null;
  }
}
