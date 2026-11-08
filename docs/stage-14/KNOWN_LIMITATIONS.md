# ACREVIA Stage 14 — Known Limitations & Future Roadmap

## 1. Known Architectural Limitations
1. **Asynchronous Large-Scale Exports:** For exports exceeding 100,000 records, the current implementation serializes in memory; enterprise workloads should offload export generation to Celery / BullMQ workers with persistent cloud storage (S3 / GCS).
2. **Webhook Retries:** Webhook deliveries are currently dispatched synchronously within test harnesses and worker routines; high-throughput production environments will benefit from a dedicated background worker consumer for the outbox table.
3. **SSRF DNS Rebinding:** While static IP and hostname checks block RFC-1918 addresses and metadata endpoints, production deployments behind enterprise reverse proxies should use DNS resolver pinning to prevent advanced DNS rebinding attacks.

---

## 2. Roadmap to Future Stages
- Integration with live national e-NAM bidding APIs as state authorization gateways become available.
- Real-time LoRaWAN gateway MQTT broker bridging for sub-second sensor streaming.
- Distributed DID (Decentralized Identifier) support for portable farmer identity across agricultural credit networks.
