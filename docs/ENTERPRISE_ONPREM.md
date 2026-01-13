# Neurop Forge Enterprise On-Premise Deployment

This document outlines the architecture and deployment options for running Neurop Forge in your own infrastructure.

## Overview

Enterprise on-prem deployment provides:
- **Full data sovereignty**: All execution happens within your infrastructure
- **Network isolation**: No external API calls required after deployment
- **Custom policy configuration**: Define your own trust tiers and access rules
- **Local audit storage**: Compliance data stays in your environment

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Your Infrastructure                          │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   Load Balancer │───▶│  Neurop Forge   │───▶│  PostgreSQL │ │
│  │   (Your LB)     │    │  API Container  │    │  (Audit DB) │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│                                │                               │
│                                ▼                               │
│                    ┌─────────────────────┐                     │
│                    │   Block Library     │                     │
│                    │   (Sealed Volume)   │                     │
│                    │   4,552 blocks      │                     │
│                    └─────────────────────┘                     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Policy Engine                          │   │
│  │  - Block whitelist/blacklist                            │   │
│  │  - Trust tier enforcement                               │   │
│  │  - Rate limiting per agent                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Options

### Option 1: Docker Compose (Development/Small Teams)

```yaml
version: '3.8'
services:
  neurop-forge:
    image: neuropforge/enterprise:latest
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/neurop
      - API_KEYS_FILE=/config/api_keys.json
      - POLICY_FILE=/config/policy.yaml
    volumes:
      - ./config:/config:ro
      - block-library:/app/.neurop_expanded_library:ro
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=neurop
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  block-library:
  pgdata:
```

### Option 2: Kubernetes (Production)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: neurop-forge
spec:
  replicas: 3
  selector:
    matchLabels:
      app: neurop-forge
  template:
    metadata:
      labels:
        app: neurop-forge
    spec:
      containers:
      - name: api
        image: neuropforge/enterprise:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: neurop-secrets
              key: database-url
        volumeMounts:
        - name: block-library
          mountPath: /app/.neurop_expanded_library
          readOnly: true
        - name: config
          mountPath: /config
          readOnly: true
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: block-library
        persistentVolumeClaim:
          claimName: block-library-pvc
      - name: config
        configMap:
          name: neurop-config
```

## Security Considerations

### Block Library Protection

The block library is delivered as a sealed, read-only volume:

1. **Integrity verification**: Each block has a SHA256 hash that's verified on startup
2. **Immutability**: The volume is mounted read-only; blocks cannot be modified
3. **Attestation**: Optional remote attestation to prove library integrity

### Secret Management

Integrate with your existing secret management:

- **HashiCorp Vault**: Native integration for API keys and database credentials
- **AWS Secrets Manager**: IAM-based secret injection
- **Azure Key Vault**: Managed identity support
- **Kubernetes Secrets**: Standard K8s secret mounting

### Network Security

- All traffic should be TLS-encrypted
- API endpoints can be restricted to internal networks only
- Rate limiting configurable per API key or IP range

## Policy Configuration

Define custom policies for your environment:

```yaml
# policy.yaml
version: "1.0"

trust_tiers:
  tier_a:
    description: "Safe for unrestricted AI use"
    allowed_by_default: true
    
  tier_b:
    description: "Requires explicit permission"
    allowed_by_default: false
    require_approval: true

block_policies:
  # Allow all string operations
  - category: "string"
    trust_tier: "tier_a"
    
  # Allow all validation blocks
  - category: "validation"
    trust_tier: "tier_a"
    
  # Restrict certain operations
  - name_pattern: "crypto_*"
    trust_tier: "tier_b"
    
rate_limits:
  default:
    requests_per_minute: 100
    requests_per_day: 10000
    
  premium:
    requests_per_minute: 1000
    requests_per_day: 100000

audit:
  retention_days: 90
  export_format: "json"
  s3_bucket: "your-audit-bucket"  # Optional S3 export
```

## Compliance

### SOC 2 Type II

- **CC6.1**: Logical access controls via API keys and policy engine
- **CC6.6**: Audit logging with tamper-proof chain
- **CC7.2**: Change management via immutable block library

### HIPAA

- **164.312(a)(1)**: Access controls per API key
- **164.312(b)**: Audit controls with full execution trail
- **164.312(c)(1)**: Integrity controls via hash verification

### PCI-DSS

- **Requirement 7**: Access restriction to block execution
- **Requirement 10**: Audit trail for all operations
- **Requirement 11**: Integrity monitoring of block library

## Support & Updates

### Block Library Updates

Signed update packages delivered via secure channel:
1. Download signed package
2. Verify signature
3. Apply to volume (during maintenance window)
4. Restart containers
5. Automatic integrity verification

### Versioning

- API versions: Semantic versioning (v2.x.x)
- Block library versions: Date-based (2024.01.15)
- SDK compatibility: Guaranteed for major API versions

## Contact

For enterprise licensing and deployment assistance:
- Email: wassermanlourens@gmail.com
- Website: https://neurop-forge.onrender.com

---

*Neurop Forge Enterprise is designed for organizations requiring full control over AI execution infrastructure while maintaining the security guarantees of the hosted platform.*
