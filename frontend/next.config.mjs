/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(self), microphone=(self), geolocation=()" },
        ],
      },
    ];
  },
  async rewrites() {
    const rawBackendUrl =
      process.env.BACKEND_INTERNAL_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      (process.env.NODE_ENV === "production" ? "" : "http://127.0.0.1:8000");

    let backendUrl = (rawBackendUrl || "").trim().replace(/\/+$/, "");
    if (backendUrl.endsWith("/api/v1")) {
      backendUrl = backendUrl.slice(0, -"/api/v1".length);
    } else if (backendUrl.endsWith("/api")) {
      backendUrl = backendUrl.slice(0, -"/api".length);
    }

    const rules = backendUrl
      ? [
          {
            source: "/api/v1/:path*",
            destination: `${backendUrl}/api/v1/:path*`,
          },
        ]
      : [];

    return {
      beforeFiles: [],
      afterFiles: [],
      fallback: rules,
    };
  },
};

export default nextConfig;
