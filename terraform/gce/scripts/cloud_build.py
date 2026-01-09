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


class OperationNotFoundError(CloudBuildError):
    """Raised when an operation is not found (404), typically meaning it expired."""


def submit_build(
    session: AuthorizedSession,
    project: str,
    region: str,
    build_config: dict[str, Any],
) -> dict[str, str]:
    """
    Submit a build to Cloud Build.

    Args:
        session: Authenticated requests session
        project: GCE project ID
        region: Cloud Build region
        build_config: Cloud Build configuration dictionary

    Returns:
        dict: Contains 'operation' (operation name) and 'build_id' (build ID)

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
    operation_name = data.get("name")
    if not operation_name:
        raise CloudBuildError(f"API response missing operation name: {data}")

    # Extract build ID from metadata for direct polling (operations endpoint
    # does not work reliably for regional builds)
    metadata = data.get("metadata", {})
    build = metadata.get("build", {})
    build_id = build.get("id")
    if not build_id:
        raise CloudBuildError(f"API response missing build ID in metadata: {data}")

    return {"operation": operation_name, "build_id": build_id}


def get_operation_status(
    session: AuthorizedSession,
    operation_name: str,
) -> dict[str, Any]:
    """
    Get the status of a long-running operation.

    Note: This endpoint does not work reliably for regional builds.
    Use get_build_status() instead.

    Args:
        session: Authenticated requests session
        operation_name: Full operation name from submit_build

    Returns:
        dict: Operation status including build metadata

    Raises:
        OperationNotFoundError: If the operation no longer exists (404)
        CloudBuildError: For other API errors
    """
    url = f"{CLOUD_BUILD_API}/{operation_name}"

    response = session.get(url, timeout=API_TIMEOUT)

    if response.status_code == 404:
        raise OperationNotFoundError(
            f"Operation not found: {operation_name}. "
            "The operation may have expired or been deleted."
        )

    if not response.ok:
        raise CloudBuildError(
            f"Failed to get operation status: {response.status_code} {response.text}"
        )

    return response.json()


def get_build_status(
    session: AuthorizedSession,
    project: str,
    region: str,
    build_id: str,
) -> dict[str, Any]:
    """
    Get the status of a Cloud Build by querying the build endpoint directly.

    This method is more reliable for regional builds than polling the
    operation endpoint.

    Args:
        session: Authenticated requests session
        project: GCE project ID
        region: Cloud Build region
        build_id: Build ID from submit_build

    Returns:
        dict: Build status and metadata

    Raises:
        CloudBuildError: If the API request fails
    """
    url = f"{CLOUD_BUILD_API}/projects/{project}/locations/{region}/builds/{build_id}"

    response = session.get(url, timeout=API_TIMEOUT)

    if response.status_code == 404:
        raise OperationNotFoundError(
            f"Build not found: {build_id}. " "The build may have been deleted."
        )

    if not response.ok:
        raise CloudBuildError(
            f"Failed to get build status: {response.status_code} {response.text}"
        )

    return response.json()


def wait_for_build(
    session: AuthorizedSession,
    project: str,
    region: str,
    build_id: str,
    timeout_minutes: int = 60,
    poll_interval: int = 30,
) -> dict[str, Any]:
    """
    Wait for a Cloud Build to complete.

    Args:
        session: Authenticated requests session
        project: GCE project ID
        region: Cloud Build region
        build_id: Build ID from submit_build
        timeout_minutes: Maximum wait time
        poll_interval: Seconds between status checks

    Returns:
        dict: Final build status

    Raises:
        CloudBuildError: If build fails or times out
    """
    deadline = time.time() + (timeout_minutes * 60)

    # Terminal build statuses
    terminal_statuses = {"SUCCESS", "FAILURE", "INTERNAL_ERROR", "TIMEOUT", "CANCELLED"}

    while time.time() < deadline:
        build = get_build_status(session, project, region, build_id)
        status = build.get("status", "UNKNOWN")

        if status in terminal_statuses:
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


def list_builds(
    session: AuthorizedSession,
    project: str,
    region: str,
    page_size: int = 10,
) -> list[dict[str, Any]]:
    """
    List recent Cloud Builds.

    Args:
        session: Authenticated requests session
        project: GCE project ID
        region: Cloud Build region
        page_size: Maximum number of builds to return

    Returns:
        list: List of build metadata dictionaries
    """
    url = f"{CLOUD_BUILD_API}/projects/{project}/locations/{region}/builds"
    params = {"pageSize": page_size}

    response = session.get(url, params=params, timeout=API_TIMEOUT)

    if not response.ok:
        raise CloudBuildError(
            f"Failed to list builds: {response.status_code} {response.text}"
        )

    data = response.json()
    return data.get("builds", [])


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
    wait_parser.add_argument("--project", required=True, help="GCE project ID")
    wait_parser.add_argument("--region", required=True, help="Cloud Build region")
    wait_parser.add_argument("--build-id", required=True, help="Build ID from submit")
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

    # List command
    list_parser = subparsers.add_parser("list", help="List recent Cloud Builds")
    list_parser.add_argument("--project", required=True, help="GCE project ID")
    list_parser.add_argument("--region", required=True, help="Cloud Build region")
    list_parser.add_argument(
        "--limit", type=int, default=10, help="Maximum builds to list"
    )
    list_parser.add_argument(
        "--format",
        choices=["json", "table"],
        default="table",
        help="Output format",
    )

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

            result = submit_build(session, args.project, args.region, config)
            print(json.dumps(result))

        elif args.command == "wait":
            build_id = getattr(args, "build_id", None)
            result = wait_for_build(
                session, args.project, args.region, build_id, args.timeout
            )
            print(json.dumps(result))

        elif args.command == "download":
            dest = Path(args.dest)
            downloaded = download_artifacts(session, args.bucket, args.prefix, dest)
            print(json.dumps({"files": [str(p) for p in downloaded]}))

        elif args.command == "upload":
            source = Path(args.source)
            upload_object(session, args.bucket, args.dest, source)
            print(json.dumps({"uploaded": args.dest}))

        elif args.command == "list":
            builds = list_builds(session, args.project, args.region, args.limit)

            if args.format == "json":
                print(json.dumps({"builds": builds}))
            else:
                # Table format for human-readable output
                if not builds:
                    print("No builds found.")
                else:
                    print(f"{'STATUS':<12} {'STARTED':<20} {'DURATION':<10} {'ID'}")
                    print("-" * 70)
                    for build in builds:
                        status = build.get("status", "UNKNOWN")
                        build_id = build.get("id", "N/A")[:12]
                        start_time = build.get("startTime", "N/A")
                        if start_time != "N/A":
                            # Parse and format the timestamp
                            start_time = start_time[:19].replace("T", " ")

                        # Calculate duration if available
                        duration = "N/A"
                        if "startTime" in build and "finishTime" in build:
                            try:
                                from datetime import datetime

                                start = datetime.fromisoformat(
                                    build["startTime"].replace("Z", "+00:00")
                                )
                                finish = datetime.fromisoformat(
                                    build["finishTime"].replace("Z", "+00:00")
                                )
                                delta = finish - start
                                mins, secs = divmod(int(delta.total_seconds()), 60)
                                duration = f"{mins}m{secs}s"
                            except (ValueError, KeyError):
                                pass
                        elif status in ("WORKING", "QUEUED", "PENDING"):
                            duration = "running"

                        print(
                            f"{status:<12} {start_time:<20} {duration:<10} {build_id}"
                        )

    except OperationNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)  # Distinct exit code for "operation not found"
    except (CloudBuildError, ValueError, requests.exceptions.RequestException) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
