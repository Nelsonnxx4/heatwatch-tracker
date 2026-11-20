import { type NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.HEATWATCH_API_URL ?? "http://localhost:8000";
const API_KEY = process.env.HEATWATCH_API_KEY ?? "";
const REVALIDATE_SECONDS = 300;

/** Only these read-only routes are forwarded. Everything else is a 404. */
const ALLOWED_PATHS = [
  /^cities$/,
  /^cities\/[a-z0-9-]+\/(temperature|heat-summary)$/,
  /^rankings\/hottest$/,
];

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const { path } = await params;
  const target = path.join("/");

  if (!ALLOWED_PATHS.some((pattern) => pattern.test(target))) {
    return NextResponse.json({ detail: "Not found" }, { status: 404 });
  }

  try {
    const upstream = await fetch(`${BACKEND_URL}/${target}${request.nextUrl.search}`, {
      headers: { "X-API-Key": API_KEY },
      next: { revalidate: REVALIDATE_SECONDS },
    });
    return new NextResponse(upstream.body, {
      status: upstream.status,
      headers: { "content-type": upstream.headers.get("content-type") ?? "application/json" },
    });
  } catch {
    return NextResponse.json({ detail: "HeatWatch API is unreachable" }, { status: 502 });
  }
}
