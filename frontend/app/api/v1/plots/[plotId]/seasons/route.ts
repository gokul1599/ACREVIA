import { NextRequest, NextResponse } from "next/server";
import { getDb } from "@/lib/server/db";
import { proxyToBackend } from "@/lib/server/proxy";
import crypto from "crypto";

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ plotId: string }> }
) {
  const { plotId } = await params;
  const proxied = await proxyToBackend(req, `plots/${plotId}/seasons`);
  if (proxied) return proxied;

  try {
    const body = await req.json();
    const {
      crop_id = "cotton",
      season_type = "KHARIF",
      sowing_date = new Date().toISOString().split("T")[0],
      current_stage = "VEGETATIVE",
    } = body;

    const seasonId = crypto.randomUUID();
    const now = new Date().toISOString();
    const sql = getDb();

    // Ensure crop exists in crops table
    await sql`
      INSERT INTO crops (id, name_en, name_te, name_hi, scientific_name)
      VALUES (
        ${crop_id},
        ${crop_id.charAt(0).toUpperCase() + crop_id.slice(1)},
        ${crop_id === "cotton" ? "ప్రత్తి" : crop_id === "rice" ? "వరి" : "మిరప"},
        ${crop_id === "cotton" ? "कपास" : crop_id === "rice" ? "चावल" : "मिर्च"},
        ${crop_id === "cotton" ? "Gossypium hirsutum" : crop_id === "rice" ? "Oryza sativa" : "Capsicum annuum"}
      )
      ON CONFLICT (id) DO NOTHING
    `;

    await sql`
      INSERT INTO crop_seasons (
        id, plot_id, crop_id, season_type, sowing_date, current_stage,
        status, created_at, updated_at
      ) VALUES (
        ${seasonId}, ${plotId}, ${crop_id}, ${season_type},
        ${sowing_date}, ${current_stage}, 'ACTIVE', ${now}, ${now}
      )
    `;

    return NextResponse.json(
      {
        id: seasonId,
        plot_id: plotId,
        crop_id,
        season_type,
        sowing_date,
        current_stage,
        status: "ACTIVE",
        created_at: now,
        updated_at: now,
      },
      { status: 201 }
    );
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : "Error creating crop season";
    return NextResponse.json({ detail: errorMsg }, { status: 500 });
  }
}

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ plotId: string }> }
) {
  const { plotId } = await params;
  const proxied = await proxyToBackend(req, `plots/${plotId}/seasons`);
  if (proxied) return proxied;

  try {
    const sql = getDb();
    const seasons = await sql`
      SELECT * FROM crop_seasons WHERE plot_id = ${plotId} ORDER BY created_at DESC
    `;
    return NextResponse.json(seasons, { status: 200 });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : "Error fetching crop seasons";
    return NextResponse.json({ detail: errorMsg }, { status: 500 });
  }
}
