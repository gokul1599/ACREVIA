import { NextRequest, NextResponse } from "next/server";
import { getDb } from "@/lib/server/db";
import { verifyAccessToken } from "@/lib/server/auth";
import { proxyToBackend } from "@/lib/server/proxy";
import crypto from "crypto";

export async function POST(req: NextRequest) {
  const proxied = await proxyToBackend(req, "farms");
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
    const { name, district, mandal, village, total_acreage = 1.0 } = body;

    const farmId = crypto.randomUUID();
    const now = new Date().toISOString();
    const sql = getDb();

    await sql`
      INSERT INTO farms (
        id, owner_id, name, state, district, mandal, village,
        total_acreage, is_archived, created_at, updated_at
      ) VALUES (
        ${farmId}, ${payload.sub}, ${name || "My Farm"}, 'Telangana',
        ${district || "Warangal"}, ${mandal || "Geesugonda"},
        ${village || "Dharmaram"}, ${parseFloat(total_acreage) || 1.0},
        false, ${now}, ${now}
      )
    `;

    // Add owner membership
    const membershipId = crypto.randomUUID();
    await sql`
      INSERT INTO farm_memberships (
        id, farm_id, user_id, role_in_farm, created_at, updated_at
      ) VALUES (
        ${membershipId}, ${farmId}, ${payload.sub}, 'OWNER', ${now}, ${now}
      )
    `;

    return NextResponse.json(
      {
        id: farmId,
        owner_id: payload.sub,
        name: name || "My Farm",
        state: "Telangana",
        district: district || "Warangal",
        mandal: mandal || "Geesugonda",
        village: village || "Dharmaram",
        total_acreage: parseFloat(total_acreage) || 1.0,
        is_archived: false,
        created_at: now,
        updated_at: now,
      },
      { status: 201 }
    );
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : "Error creating farm";
    return NextResponse.json({ detail: errorMsg }, { status: 500 });
  }
}

export async function GET(req: NextRequest) {
  const proxied = await proxyToBackend(req, "farms");
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

    const sql = getDb();
    const farms = await sql`
      SELECT f.* 
      FROM farms f
      JOIN farm_memberships fm ON f.id = fm.farm_id
      WHERE fm.user_id = ${payload.sub} AND f.is_archived = false
      ORDER BY f.created_at DESC
    `;

    return NextResponse.json(farms, { status: 200 });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : "Error fetching farms";
    return NextResponse.json({ detail: errorMsg }, { status: 500 });
  }
}
