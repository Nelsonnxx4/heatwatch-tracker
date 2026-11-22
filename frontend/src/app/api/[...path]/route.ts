import { type NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.HEATWATCH_API_URL ?? "http://localhost:8000";
const API_KEY = process.env.HEATWATCH_API_KEY;
const REVALIDATE_SECONDS = 300;
const RESPONSE_CACHE_CONTROL = "public, max-age=60, s-maxage=300, stale-while-revalidate=600";

/** Only these read-only routes are forwarded. Everything else is a 404. */
const ALLOWED_PATHS = [
  /^cities$/,
  /^cities\/[a-z0-9-]+\/(temperature|heat-summary)$/,
  /^rankings\/hottest$/,
];

const problem = (detail: string, status: number) =>
  NextResponse.json({ detail }, { status });

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const { path } = await params;
  const target = path.join("/");

  if (!ALLOWED_PATHS.some((pattern) => pattern.test(target))) {
    return problem("Not found", 404);
  }

  if (!API_KEY) {
    console.error(
      "[proxy] HEATWATCH_API_KEY is not set. Create frontend/.env.local and restart the app.",
    );
    return problem("The dashboard server has no API key configured.", 500);
  }

  try {
    const upstream = await fetch(`${BACKEND_URL}/${target}${request.nextUrl.search}`, {
      headers: { "X-API-Key": API_KEY },
      next: { revalidate: REVALIDATE_SECONDS },
    });

    if (upstream.status === 401) {
      console.error("[proxy] The backend rejected HEATWATCH_API_KEY.");
      return problem("The backend rejected the dashboard's API key.", 502);
    }

    return new NextResponse(upstream.body, {
      status: upstream.status,
      headers: {
        "cache-control": RESPONSE_CACHE_CONTROL,
        "content-type": upstream.headers.get("content-type") ?? "application/json",
      },
    });
  } catch {
    return problem("HeatWatch API is unreachable", 502);
  }
}
