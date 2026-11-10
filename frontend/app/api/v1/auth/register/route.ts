import { NextRequest, NextResponse } from "next/server";
import { getDb } from "@/lib/server/db";
import { hashPassword } from "@/lib/server/auth";
import { proxyToBackend } from "@/lib/server/proxy";
import crypto from "crypto";

export async function POST(req: NextRequest) {
  // 1. Try forwarding to dedicated FastAPI backend if reachable
  const proxied = await proxyToBackend(req, "auth/register");
  if (proxied) return proxied;

  // 2. Fallback to resilient serverless execution on Neon PostgreSQL
  try {
    const body = await req.json();
    const {
      phone,
      full_name,
      password,
      email = null,
      language_preference = "te",
      role = "FARMER",
    } = body;

    // Validation
    const cleanPhone = (phone || "").trim();
    if (!cleanPhone || !/^\+?[0-9]{10,15}$/.test(cleanPhone)) {
      return NextResponse.json(
        {
          error_type: "ValidationError",
          detail: "Valid phone number (10-15 digits) is required.",
        },
        { status: 422 }
      );
    }

    const cleanName = (full_name || "").trim();
    if (!cleanName || cleanName.length < 2) {
      return NextResponse.json(
        {
          error_type: "ValidationError",
          detail: "Full name must be at least 2 characters long.",
        },
        { status: 422 }
      );
    }

    if (!password || password.length < 8) {
      return NextResponse.json(
        {
          error_type: "ValidationError",
          detail: "Password must be at least 8 characters long.",
        },
        { status: 422 }
      );
    }

    const cleanEmail = email ? email.trim().toLowerCase() : null;
    const cleanLang = ["te", "en", "hi"].includes(language_preference)
      ? language_preference
      : "te";
    const cleanRole = ["FARMER", "AGRICULTURAL_EXPERT", "RESEARCHER"].includes(
      role
    )
      ? role
      : "FARMER";

    const sql = getDb();

    // Check duplicate phone
    const existingPhone = await sql`
      SELECT id FROM users WHERE phone = ${cleanPhone} LIMIT 1
    `;
    if (existingPhone && existingPhone.length > 0) {
      return NextResponse.json(
        {
          error_type: "ConflictException",
          detail: `User with phone number '${cleanPhone}' already exists.`,
        },
        { status: 409 }
      );
    }

    // Check duplicate email if provided
    if (cleanEmail) {
      const existingEmail = await sql`
        SELECT id FROM users WHERE email = ${cleanEmail} LIMIT 1
      `;
      if (existingEmail && existingEmail.length > 0) {
        return NextResponse.json(
          {
            error_type: "ConflictException",
            detail: `User with email '${cleanEmail}' already exists.`,
          },
          { status: 409 }
        );
      }
    }

    // Hash password using standard bcrypt
    const hashedPassword = await hashPassword(password);
    const userId = crypto.randomUUID();
    const now = new Date().toISOString();

    // Insert user record
    await sql`
      INSERT INTO users (
        id, phone, email, hashed_password, full_name, language_preference,
        is_active, is_verified, created_at, updated_at
      ) VALUES (
        ${userId}, ${cleanPhone}, ${cleanEmail}, ${hashedPassword}, ${cleanName},
        ${cleanLang}, true, false, ${now}, ${now}
      )
    `;

    // Ensure role exists in roles table
    await sql`
      INSERT INTO roles (id, description)
      VALUES (${cleanRole}, ${cleanRole + " system role"})
      ON CONFLICT (id) DO NOTHING
    `;

    // Attach role in user_roles table
    await sql`
      INSERT INTO user_roles (user_id, role_id)
      VALUES (${userId}, ${cleanRole})
      ON CONFLICT DO NOTHING
    `;

    // Audit log if activity_logs table exists
    try {
      const logId = crypto.randomUUID();
      await sql`
        INSERT INTO audit_logs (id, user_id, action, resource_type, resource_id, metadata, timestamp)
        VALUES (
          ${logId}, ${userId}, 'USER_REGISTRATION', 'USER', ${userId},
          ${JSON.stringify({ phone: cleanPhone, role: cleanRole })}, ${now}
        )
      `;
    } catch {
      // Non-blocking audit log
    }

    return NextResponse.json(
      {
        id: userId,
        phone: cleanPhone,
        email: cleanEmail,
        full_name: cleanName,
        language_preference: cleanLang,
        is_active: true,
        is_verified: false,
        roles: [cleanRole],
      },
      { status: 201 }
    );
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : "Internal registration error";
    return NextResponse.json(
      {
        error_type: "InternalServerError",
        detail: `Registration failed: ${errorMsg}`,
      },
      { status: 500 }
    );
  }
}
