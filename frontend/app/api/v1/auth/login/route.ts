import { NextRequest, NextResponse } from "next/server";
import { getDb } from "@/lib/server/db";
import { verifyPassword, createAccessToken } from "@/lib/server/auth";
import { proxyToBackend } from "@/lib/server/proxy";
import crypto from "crypto";

export async function POST(req: NextRequest) {
  // 1. Try forwarding to dedicated FastAPI backend if reachable
  const proxied = await proxyToBackend(req, "auth/login");
  if (proxied) return proxied;

  // 2. Fallback to resilient serverless execution on Neon PostgreSQL
  try {
    const body = await req.json();
    const { phone, email, password } = body;

    const identifier = (phone || email || "").trim();
    if (!identifier || !password) {
      return NextResponse.json(
        {
          error_type: "AuthenticationException",
          detail: "Either phone or email and password must be provided.",
        },
        { status: 400 }
      );
    }

    const sql = getDb();

    // Look up user by phone or email
    const users = await sql`
      SELECT 
        u.id, u.phone, u.email, u.hashed_password, u.full_name,
        u.language_preference, u.is_active, u.is_verified,
        COALESCE(
          array_agg(ur.role_id) FILTER (WHERE ur.role_id IS NOT NULL),
          ARRAY[]::varchar[]
        ) as roles
      FROM users u
      LEFT JOIN user_roles ur ON u.id = ur.user_id
      WHERE u.phone = ${identifier} OR (u.email = ${identifier.toLowerCase()} AND u.email IS NOT NULL)
      GROUP BY u.id
      LIMIT 1
    `;

    if (!users || users.length === 0) {
      return NextResponse.json(
        {
          error_type: "AuthenticationException",
          detail: "Invalid phone/email or password.",
        },
        { status: 401 }
      );
    }

    const user = users[0];

    // Verify bcrypt password hash
    const isValid = await verifyPassword(password, user.hashed_password);
    if (!isValid) {
      return NextResponse.json(
        {
          error_type: "AuthenticationException",
          detail: "Invalid phone/email or password.",
        },
        { status: 401 }
      );
    }

    if (!user.is_active) {
      return NextResponse.json(
        {
          error_type: "AuthenticationException",
          detail: "Account has been deactivated. Please contact support.",
        },
        { status: 401 }
      );
    }

    const roles = Array.isArray(user.roles) ? user.roles : ["FARMER"];
    const token = await createAccessToken(
      user.id,
      roles,
      { phone: user.phone, name: user.full_name },
      86400
    );

    // Audit log
    try {
      const now = new Date().toISOString();
      const logId = crypto.randomUUID();
      await sql`
        INSERT INTO audit_logs (id, user_id, action, resource_type, resource_id, metadata, timestamp)
        VALUES (
          ${logId}, ${user.id}, 'USER_LOGIN', 'USER', ${user.id},
          ${JSON.stringify({ login_identifier: identifier })}, ${now}
        )
      `;
    } catch {
      // Non-blocking
    }

    return NextResponse.json(
      {
        access_token: token,
        token_type: "bearer",
        expires_in_seconds: 86400,
        user: {
          id: user.id,
          phone: user.phone,
          email: user.email,
          full_name: user.full_name,
          language_preference: user.language_preference,
          is_active: user.is_active,
          is_verified: user.is_verified,
          roles,
        },
      },
      { status: 200 }
    );
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : "Internal login error";
    return NextResponse.json(
      {
        error_type: "InternalServerError",
        detail: `Authentication failed: ${errorMsg}`,
      },
      { status: 500 }
    );
  }
}
