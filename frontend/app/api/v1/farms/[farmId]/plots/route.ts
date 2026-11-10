import { NextRequest, NextResponse } from "next/server";
import { getDb } from "@/lib/server/db";
import { verifyAccessToken } from "@/lib/server/auth";
import { proxyToBackend } from "@/lib/server/proxy";
import crypto from "crypto";

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ farmId: string }> }
) {
  const { farmId } = await params;
  const proxied = await proxyToBackend(req, `farms/${farmId}/plots`);
  if (proxied) return proxied;

  try {
    const authHeader = req.headers.get("authorization") || "";
    if (!authHeader.startsWith("Bearer ")) {
      return NextResponse.json({ detail: "Authentication required." }, { status: 401 });
    }

    const token = authHeader.slice("Bearer ".length).trim();
    const payload = await verifyAccessToken(token);
    if (!payload || !payload.sub) {
      return NextResponse.json({ detail: "Token invalid or expired." }, { status: 401 });
    }

    const body = await req.json();
    const { name, soil_type = "BLACK_COTTON", irrigation_source = "BOREWELL", acreage = 1.0 } = body;

    const plotId = crypto.randomUUID();
    const now = new Date().toISOString();
    const sql = getDb();

    await sql`
      INSERT INTO plots (
        id, farm_id, name, soil_type, irrigation_source, acreage,
        is_archived, created_at, updated_at
      ) VALUES (
        ${plotId}, ${farmId}, ${name || "Plot 1"}, ${soil_type},
        ${irrigation_source}, ${parseFloat(acreage) || 1.0},
        false, ${now}, ${now}
      )
    `;

    return NextResponse.json(
      {
        id: plotId,
        farm_id: farmId,
        name: name || "Plot 1",
        soil_type,
        irrigation_source,
        acreage: parseFloat(acreage) || 1.0,
        is_archived: false,
        created_at: now,
        updated_at: now,
      },
      { status: 201 }
    );
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : "Error creating plot";
    return NextResponse.json({ detail: errorMsg }, { status: 500 });
  }
}

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ farmId: string }> }
) {
  const { farmId } = await params;
  const proxied = await proxyToBackend(req, `farms/${farmId}/plots`);
  if (proxied) return proxied;

  try {
    const sql = getDb();
    const plots = await sql`
      SELECT * FROM plots WHERE farm_id = ${farmId} AND is_archived = false ORDER BY created_at ASC
    `;
    return NextResponse.json(plots, { status: 200 });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : "Error fetching plots";
    return NextResponse.json({ detail: errorMsg }, { status: 500 });
  }
}
