import { NextRequest, NextResponse } from "next/server";

export async function GET(
  request: NextRequest,
  { params }: { params: { toolId: string } }
) {
  const { toolId } = params;
  const { searchParams } = new URL(request.url);
  const code = searchParams.get("code");
  const state = searchParams.get("state");

  if (!code) {
    return NextResponse.redirect(new URL("/integrations?error=no_code", request.url));
  }

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  try {
    const res = await fetch(`${backendUrl}/api/integrations/${toolId}/callback?code=${code}&state=${state || ""}`, {
      method: "GET",
    });

    if (res.ok) {
      return NextResponse.redirect(new URL("/integrations?success=true", request.url));
    } else {
      const errorData = await res.json().catch(() => ({ detail: "Exchange failed" }));
      console.error("Backend callback failed:", errorData);
      return NextResponse.redirect(new URL(`/integrations?error=exchange_failed&message=${encodeURIComponent(errorData.detail || "Unknown error")}`, request.url));
    }
  } catch (err) {
    console.error("Callback error:", err);
    return NextResponse.redirect(new URL(`/integrations?error=server_error&message=${encodeURIComponent(err instanceof Error ? err.message : "Network error")}`, request.url));
  }
}
