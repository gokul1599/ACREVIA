import { neon, NeonQueryFunction } from "@neondatabase/serverless";

let sqlInstance: NeonQueryFunction<false, false> | null = null;

export function getDb(): NeonQueryFunction<false, false> {
  if (sqlInstance) return sqlInstance;

  const dbUrl =
    process.env.DATABASE_URL ||
    "postgresql://neondb_owner:npg_tqNy2evVo5hj@ep-muddy-mode-a1nd6rrb-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require";

  sqlInstance = neon(dbUrl);
  return sqlInstance;
}
