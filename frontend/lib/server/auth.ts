import bcrypt from "bcryptjs";
import { SignJWT, jwtVerify } from "jose";
import type { JWTPayload } from "jose";

const JWT_SECRET =
  process.env.JWT_SECRET_KEY || "acrevia_live_secret_4894a11c87d_neon_production_key_2026";
const secretKey = new TextEncoder().encode(JWT_SECRET);

export async function hashPassword(plainText: string): Promise<string> {
  const salt = await bcrypt.genSalt(12);
  return bcrypt.hash(plainText, salt);
}

export async function verifyPassword(plainText: string, hashed: string): Promise<boolean> {
  try {
    return await bcrypt.compare(plainText, hashed);
  } catch {
    return false;
  }
}

export async function createAccessToken(
  subject: string,
  roles: string[],
  extraClaims?: Record<string, unknown>,
  expiresInSeconds: number = 86400
): Promise<string> {
  const jwt = new SignJWT({
    sub: subject,
    roles,
    ...extraClaims,
  })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setIssuer("acrevia-auth-service")
    .setExpirationTime(Math.floor(Date.now() / 1000) + expiresInSeconds);

  return jwt.sign(secretKey);
}

export async function verifyAccessToken(token: string): Promise<JWTPayload | null> {
  try {
    const { payload } = await jwtVerify(token, secretKey, {
      issuer: "acrevia-auth-service",
    });
    return payload;
  } catch {
    return null;
  }
}
