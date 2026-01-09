# Cloud Build for Kernel Compilation

Cloud build offloads kernel compilation to cloud provider build services,
enabling faster builds on high-CPU instances without requiring local
resources. The compiled kernel packages are downloaded and installed on
target nodes automatically.

## When to Use Cloud Build

Cloud build is useful when:

- Target nodes have limited CPU/memory for kernel compilation
- Faster build times are needed via high-core-count cloud instances
- Building kernels for cloud-hosted VMs where network transfer is fast
- Local 9P or NFS builds are impractical due to I/O overhead

Cloud build is not recommended when:

- Target nodes have sufficient local build capacity
- Network bandwidth to cloud storage is limited
- Building for bare metal or non-cloud environments

## Supported Cloud Providers

Currently implemented:

- **GCE (Google Cloud)**: Uses Cloud Build service with GCS artifact storage

Placeholder support exists for AWS CodeBuild, Azure Pipelines, and OCI
DevOps, though these are not yet implemented.

## Prerequisites

### GCE Cloud Build

1. **Terraform GCE provider configured**: The project must use GCE for
   infrastructure provisioning
2. **Cloud Build API enabled**: Enable via GCP Console or `gcloud services
   enable cloudbuild.googleapis.com`
3. **Cloud Build bucket provisioned**: Terraform creates the GCS bucket for
   artifact storage when cloud build is enabled
4. **Service account permissions**: The Cloud Build service account needs
   Storage Object Admin on the artifact bucket

## Artifact Bucket Defaults

The GCS artifact bucket is configured with these defaults:

- **Object versioning enabled**: Previous versions of artifacts are retained,
  allowing recovery from accidental overwrites or deletions
- **Public access prevention enforced**: The bucket cannot be made publicly
  accessible, preventing accidental data exposure
- **Deleted on destroy**: By default, `make destroy` removes the bucket and
  all stored artifacts, matching the behavior of other build modes and
  avoiding storage costs after teardown

To retain kernel packages after destroy, enable "Preserve artifacts on
destroy" in menuconfig. When enabled, the artifact bucket is removed from
Terraform state before destroy, allowing destroy to complete while leaving
the bucket intact in GCS for later use or manual cleanup.

## Configuration

Enable cloud build in `make menuconfig`:

```
Workflows
  -> Linux kernel development
    -> Kernel build method
      -> Cloud build (offload to cloud provider)
```

### Timeout Configuration

The timeout controls two aspects of cloud build operation:

- **Cloud Build job deadline**: Maximum wall-clock time for the entire build
  job (clone, compile, package, upload)
- **Polling wait time**: How long the control host waits for completion before
  failing

```
Cloud build timeout (minutes) (BOOTLINUX_CLOUD_BUILD_TIMEOUT) [60]
```

A typical kernel build with modules takes 15-45 minutes depending on
configuration complexity and machine type. The default of 60 minutes provides
headroom for larger configurations.

Adjust the timeout based on:

- **Kernel configuration size**: allmodconfig builds need more time
- **Machine type**: Smaller instances (e2-medium) build slower than larger
  ones (e2-highcpu-32)
- **Network conditions**: Artifact upload time varies with package size

### Machine Type

The build machine type is inherited from `terraform_gce_machine_type`. For
faster builds, use high-CPU instances:

```
e2-highcpu-32   # 32 vCPUs, recommended for kernel builds
n2-highcpu-64   # 64 vCPUs, for very large configurations
```

## How It Works

1. **Configuration generation**: Ansible generates a Cloud Build YAML
   configuration from the template
2. **Job submission**: The `cloud_build.py` script submits the build job to
   Cloud Build
3. **Build execution**: Cloud Build clones the kernel source, runs the build
   in a container, and packages the result (deb or rpm)
4. **Artifact upload**: Kernel packages are uploaded to GCS
5. **Polling**: The control host polls for completion up to the configured
   timeout
6. **Download**: Artifacts are downloaded to the local artifacts directory
7. **Installation**: Kernel packages are copied to target nodes and installed

## Usage

Once configured, cloud build is triggered automatically by standard make
targets:

```bash
make linux          # Builds via cloud, installs on all nodes
make linux-baseline # Builds via cloud, installs on baseline nodes
make linux-dev      # Builds via cloud, installs on dev nodes
```

Build artifacts are cached in `workflows/linux/artifacts/cloud_build/`.

## Troubleshooting

### Build Timeout Exceeded

If builds consistently timeout:

1. Increase `BOOTLINUX_CLOUD_BUILD_TIMEOUT` to 90 or 120 minutes
2. Use a larger machine type for faster compilation
3. Enable shallow clones to reduce git clone time
4. Reduce kernel configuration size (fewer modules)

### Permission Denied on GCS

Verify the Cloud Build service account has Storage Object Admin permission
on the artifact bucket:

```bash
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:cloudbuild.gserviceaccount.com"
```

### Cloud Build API Not Enabled

Enable the required APIs:

```bash
gcloud services enable cloudbuild.googleapis.com storage.googleapis.com
```

### Missing Terraform Variables

Ensure Terraform provisioning completed successfully and `extra_vars.yaml`
contains:

- `terraform_gce_cloud_build_bucket`
- `terraform_gce_project`
- `terraform_gce_cloud_build_region` (optional, defaults to us-west1)

## Variables Reference

### Ansible Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `bootlinux_cloud_build` | false | Enable cloud build |
| `bootlinux_cloud_build_timeout_minutes` | 60 | Build timeout in minutes |
| `terraform_gce_cloud_build_bucket` | (required) | GCS bucket for artifacts |
| `terraform_gce_cloud_build_region` | us-west1 | Cloud Build region |
| `terraform_gce_machine_type` | e2-highcpu-32 | Build machine type |

### Terraform Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `cb_project` | (required) | GCE project ID |
| `cb_region` | (required) | GCE region for the bucket |
| `cb_bucket_name` | (auto) | Bucket name (auto-generated if empty) |
| `cb_artifact_retention_days` | 30 | Days to retain artifacts |
| `cb_force_destroy` | true | Delete bucket and contents on destroy |
| `cb_service_account_id` | kdevops-cloud-build | Service account ID |

### Kconfig Options

| Option | Default | Description |
|--------|---------|-------------|
| `TERRAFORM_GCE_CLOUD_BUILD_PRESERVE_ARTIFACTS` | n | Preserve artifact bucket on destroy |
