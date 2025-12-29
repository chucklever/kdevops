#!/usr/bin/env python3
# SPDX-License-Identifier: copyleft-next-0.3.1
"""
GCE Cloud Build client for kdevops kernel builds.

This module provides functionality to submit kernel builds to GCE Cloud
Build and download artifacts from GCS. It uses the REST APIs directly
with google-auth and requests, avoiding the gcloud CLI dependency.

API Documentation:
    Cloud Build: https://cloud.google.com/build/docs/api/reference/rest
    Cloud Storage: https://cloud.google.com/storage/docs/json_api/v1
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import requests
from google.auth.transport.requests import AuthorizedSession

from gce_common import get_authenticated_session

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# API base URLs
CLOUD_BUILD_API = "https://cloudbuild.googleapis.com/v1"
STORAGE_API = "https://storage.googleapis.com/storage/v1"

# Timeout for API requests
API_TIMEOUT = 30

# Default OAuth2 scopes for Cloud Build and Storage access
CLOUD_BUILD_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


class CloudBuildError(Exception):
    """Raised when a Cloud Build operation fails."""


def submit_build(
    session: AuthorizedSession,
    project: str,
    region: str,
    build_config: dict[str, Any],
) -> str:
    """
    Submit a build to Cloud Build.

    Args:
        session: Authenticated requests session
        project: GCE project ID
        region: Cloud Build region
        build_config: Cloud Build configuration dictionary

    Returns:
        str: Build operation name (used to poll status)

    Raises:
        CloudBuildError: If submission fails
    """
    url = f"{CLOUD_BUILD_API}/projects/{project}/locations/{region}/builds"

    response = session.post(url, json=build_config, timeout=API_TIMEOUT)

    if not response.ok:
        raise CloudBuildError(
            f"Failed to submit build: {response.status_code} {response.text}"
        )

    data = response.json()
    # Response contains an operation, the build ID is in metadata
    operation_name = data.get("name")
    if not operation_name:
        raise CloudBuildError(f"API response missing operation name: {data}")
    return operation_name


def get_operation_status(
    session: AuthorizedSession,
    operation_name: str,
) -> dict[str, Any]:
    """
    Get the status of a long-running operation.

    Args:
        session: Authenticated requests session
        operation_name: Full operation name from submit_build

    Returns:
        dict: Operation status including build metadata
    """
    url = f"{CLOUD_BUILD_API}/{operation_name}"

    response = session.get(url, timeout=API_TIMEOUT)

    if not response.ok:
        raise CloudBuildError(
            f"Failed to get operation status: {response.status_code} {response.text}"
        )

    return response.json()


def wait_for_build(
    session: AuthorizedSession,
    operation_name: str,
    timeout_minutes: int = 60,
    poll_interval: int = 30,
) -> dict[str, Any]:
    """
    Wait for a Cloud Build to complete.

    Args:
        session: Authenticated requests session
        operation_name: Operation name from submit_build
        timeout_minutes: Maximum wait time
        poll_interval: Seconds between status checks

    Returns:
        dict: Final build status

    Raises:
        CloudBuildError: If build fails or times out
    """
    deadline = time.time() + (timeout_minutes * 60)

    while time.time() < deadline:
        operation = get_operation_status(session, operation_name)

        if operation.get("done"):
            if "error" in operation:
                error = operation["error"]
                raise CloudBuildError(
                    f"Build failed: {error.get('message', 'Unknown error')}"
                )

            # Extract build result from metadata
            metadata = operation.get("metadata", {})
            build = metadata.get("build", {})
            status = build.get("status", "UNKNOWN")

            if status == "SUCCESS":
                return build
            else:
                raise CloudBuildError(f"Build completed with status: {status}")

        time.sleep(poll_interval)

    raise CloudBuildError(f"Build timed out after {timeout_minutes} minutes")


def list_bucket_objects(
    session: AuthorizedSession,
    bucket: str,
    prefix: str = "",
) -> list[dict[str, Any]]:
    """
    List objects in a GCS bucket.

    Args:
        session: Authenticated requests session
        bucket: GCS bucket name
        prefix: Object prefix filter

    Returns:
        list: List of object metadata dictionaries
    """
    url = f"{STORAGE_API}/b/{bucket}/o"
    params = {"prefix": prefix} if prefix else {}

    all_objects = []

    while True:
        response = session.get(url, params=params, timeout=API_TIMEOUT)

        if not response.ok:
            raise CloudBuildError(
                f"Failed to list bucket objects: {response.status_code} {response.text}"
            )

        data = response.json()
        all_objects.extend(data.get("items", []))

        next_page = data.get("nextPageToken")
        if not next_page:
            break
        params["pageToken"] = next_page

    return all_objects


def upload_object(
    session: AuthorizedSession,
    bucket: str,
    object_name: str,
    source: Path,
) -> None:
    """
    Upload an object to GCS.

    Args:
        session: Authenticated requests session
        bucket: GCS bucket name
        object_name: Object name in bucket
        source: Local file path to upload
    """
    url = f"https://storage.googleapis.com/upload/storage/v1/b/{bucket}/o"
    params = {"uploadType": "media", "name": object_name}

    with open(source, "rb") as f:
        response = session.post(url, params=params, data=f, timeout=300)

    if not response.ok:
        raise CloudBuildError(
            f"Failed to upload {source} to {object_name}: "
            f"{response.status_code} {response.text}"
        )


def download_object(
    session: AuthorizedSession,
    bucket: str,
    object_name: str,
    destination: Path,
) -> None:
    """
    Download an object from GCS.

    Args:
        session: Authenticated requests session
        bucket: GCS bucket name
        object_name: Object name in bucket
        destination: Local file path to write
    """
    # Use the media download endpoint
    url = f"{STORAGE_API}/b/{bucket}/o/{requests.utils.quote(object_name, safe='')}"
    params = {"alt": "media"}

    response = session.get(url, params=params, timeout=300, stream=True)

    if not response.ok:
        raise CloudBuildError(
            f"Failed to download {object_name}: {response.status_code}"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)

    with open(destination, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def download_artifacts(
    session: AuthorizedSession,
    bucket: str,
    prefix: str,
    destination_dir: Path,
) -> list[Path]:
    """
    Download all artifacts from a GCS prefix.

    Args:
        session: Authenticated requests session
        bucket: GCS bucket name
        prefix: Object prefix (folder path)
        destination_dir: Local directory to download to

    Returns:
        list: Paths to downloaded files
    """
    objects = list_bucket_objects(session, bucket, prefix)
    downloaded = []
    resolved_dest_dir = destination_dir.resolve()

    for obj in objects:
        name = obj["name"]
        # Skip directory markers
        if name.endswith("/"):
            continue

        # Preserve relative path structure
        relative_path = name[len(prefix) :].lstrip("/")
        dest_path = (destination_dir / relative_path).resolve()

        # Prevent path traversal attacks
        try:
            dest_path.relative_to(resolved_dest_dir)
        except ValueError:
            raise CloudBuildError(f"Path traversal detected in object name: {name}")

        print(f"Downloading {name}...", file=sys.stderr)
        download_object(session, bucket, name, dest_path)
        downloaded.append(dest_path)

    return downloaded


def main() -> None:
    """CLI interface for Cloud Build operations."""
    parser = argparse.ArgumentParser(description="GCE Cloud Build client for kdevops")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Submit command
    submit_parser = subparsers.add_parser("submit", help="Submit a build")
    submit_parser.add_argument("--project", required=True, help="GCE project ID")
    submit_parser.add_argument("--region", required=True, help="Cloud Build region")
    submit_parser.add_argument(
        "--config", required=True, help="Path to cloudbuild.yaml"
    )
    submit_parser.add_argument(
        "--substitutions", help="Comma-separated KEY=VALUE pairs"
    )

    # Wait command
    wait_parser = subparsers.add_parser("wait", help="Wait for build completion")
    wait_parser.add_argument(
        "--operation", required=True, help="Operation name from submit"
    )
    wait_parser.add_argument(
        "--timeout", type=int, default=60, help="Timeout in minutes"
    )

    # Download command
    download_parser = subparsers.add_parser(
        "download", help="Download artifacts from GCS"
    )
    download_parser.add_argument("--bucket", required=True, help="GCS bucket name")
    download_parser.add_argument("--prefix", required=True, help="Object prefix")
    download_parser.add_argument("--dest", required=True, help="Destination directory")

    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload a file to GCS")
    upload_parser.add_argument("--bucket", required=True, help="GCS bucket name")
    upload_parser.add_argument("--source", required=True, help="Local file path")
    upload_parser.add_argument("--dest", required=True, help="Destination object name")

    args = parser.parse_args()

    try:
        session, _ = get_authenticated_session(scopes=CLOUD_BUILD_SCOPES)

        if args.command == "submit":
            with open(args.config) as f:
                # Support both JSON and YAML
                if args.config.endswith(".json"):
                    config = json.load(f)
                elif not HAS_YAML:
                    raise ValueError(
                        "YAML config requires PyYAML. Install with: pip install pyyaml"
                    )
                else:
                    config = yaml.safe_load(f)

            # Apply substitutions
            if args.substitutions:
                substitutions = {}
                for pair in args.substitutions.split(","):
                    if "=" not in pair:
                        raise ValueError(
                            f"Invalid substitution format: {pair!r}. Expected KEY=VALUE"
                        )
                    key, value = pair.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if not key:
                        raise ValueError(
                            f"Invalid substitution: {pair!r}. Key cannot be empty"
                        )
                    substitutions[key] = value
                config["substitutions"] = substitutions

            operation = submit_build(session, args.project, args.region, config)
            print(json.dumps({"operation": operation}))

        elif args.command == "wait":
            result = wait_for_build(session, args.operation, args.timeout)
            print(json.dumps(result))

        elif args.command == "download":
            dest = Path(args.dest)
            downloaded = download_artifacts(session, args.bucket, args.prefix, dest)
            print(json.dumps({"files": [str(p) for p in downloaded]}))

        elif args.command == "upload":
            source = Path(args.source)
            upload_object(session, args.bucket, args.dest, source)
            print(json.dumps({"uploaded": args.dest}))

    except (CloudBuildError, ValueError, requests.exceptions.RequestException) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
