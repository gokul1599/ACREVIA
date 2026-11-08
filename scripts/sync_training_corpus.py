#!/usr/bin/env python3
"""
ACREVIA Training Corpus Synchronization & Archival CLI.
Stage 02 Remediation (TASK-S02-01).

Usage:
    python scripts/sync_training_corpus.py --dry-run
    python scripts/sync_training_corpus.py --source-dir data/raw --target-dir data/archive
    python scripts/sync_training_corpus.py --verify-only --manifest data/archive/manifests/archival_manifest.json
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.data.archival_manager import (
    DatasetArchivalManager,
    LocalStorageAdapter,
    S3StorageAdapter,
    ArchivalManifest,
)


def main():
    parser = argparse.ArgumentParser(
        description="ACREVIA Agricultural Dataset Archival & Synchronization Tool"
    )
    parser.add_argument(
        "--source-dir",
        type=str,
        default="data/raw",
        help="Path to source leaf images directory",
    )
    parser.add_argument(
        "--target-dir",
        type=str,
        default="data/archive",
        help="Path to local archival destination directory",
    )
    parser.add_argument(
        "--dataset-id",
        type=str,
        default="acrevia-pathology-28",
        help="Canonical dataset identifier",
    )
    parser.add_argument(
        "--version",
        type=str,
        default="v1.0.0",
        help="Dataset release version",
    )
    parser.add_argument(
        "--provider",
        choices=["local", "s3"],
        default="local",
        help="Storage provider adapter",
    )
    parser.add_argument(
        "--bucket",
        type=str,
        default="acrevia-datasets-private",
        help="Target S3/R2 private bucket name",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate archival and display inventory without copying files",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Verify the cryptographic integrity of an existing archive",
    )
    parser.add_argument(
        "--manifest-path",
        type=str,
        default=None,
        help="Explicit path to manifest file for verification",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("ACREVIA Agricultural Dataset Archival Engine")
    print(f"Dataset ID : {args.dataset_id} ({args.version})")
    print(f"Provider   : {args.provider.upper()}")
    print(f"Dry Run    : {args.dry_run}")
    print("=" * 70)

    # Initialize adapter
    if args.provider == "local":
        target_path = Path(args.target_dir).resolve()
        adapter = LocalStorageAdapter(target_path)
    else:
        adapter = S3StorageAdapter(bucket_name=args.bucket)

    source_path = Path(args.source_dir).resolve()

    if args.verify_only:
        manifest_file = (
            Path(args.manifest_path)
            if args.manifest_path
            else Path(args.target_dir) / f"datasets/acrevia/{args.dataset_id}/{args.version}/manifests/archival_manifest.json"
        )
        if not manifest_file.exists():
            print(f"Error: Manifest file not found at {manifest_file}")
            sys.exit(1)

        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest_dict = json.load(f)
        manifest = ArchivalManifest(**manifest_dict)

        print(f"Verifying {manifest.total_files} files against SHA-256 manifest...")
        result = DatasetArchivalManager.verify_archive(manifest, adapter)

        if result.is_valid:
            print(f"SUCCESS: Archive verified! {result.verified_files} files intact ({result.total_bytes_verified} bytes).")
            sys.exit(0)
        else:
            print(f"FAILED: Archive verification errors detected!")
            if result.missing_files:
                print(f"  Missing files ({len(result.missing_files)}): {result.missing_files[:5]}")
            if result.checksum_mismatches:
                print(f"  Mismatched files ({len(result.checksum_mismatches)}): {result.checksum_mismatches[:5]}")
            sys.exit(1)

    # Inventory source
    if not source_path.exists():
        print(f"Source directory '{source_path}' does not exist.")
        print("Note: In development and CI environments without raw image binaries,")
        print("synthetic image batches can be generated or downloaded via secure S3 credentials.")
        sys.exit(0)

    items = DatasetArchivalManager.inventory_dataset(source_path, dataset_id=args.dataset_id)
    print(f"Discovered {len(items)} eligible images in source directory.")

    manifest = DatasetArchivalManager.create_manifest(items, dataset_id=args.dataset_id, version=args.version)
    print(f"Emitted manifest with SHA-256: {manifest.manifest_sha256[:16]}... (Total size: {manifest.total_size_bytes} bytes)")

    result = DatasetArchivalManager.archive_dataset(
        source_dir=source_path,
        items=items,
        manifest=manifest,
        storage_adapter=adapter,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        print("\nDRY RUN SUMMARY:")
        print(f"  Planned files to copy : {result['total_files_planned']}")
        print(f"  Total planned bytes   : {result['total_bytes_planned']}")
        print(f"  Target manifest key   : {result['manifest_key']}")
        print("Dry run completed cleanly. No source files were moved or deleted.")
    else:
        print("\nARCHIVAL SUMMARY:")
        print(f"  Archived files : {result['files_archived']}")
        print(f"  Archived bytes : {result['bytes_archived']}")
        print(f"  Manifest       : {result['manifest_key']}")
        print("Archival completed successfully.")


if __name__ == "__main__":
    main()
