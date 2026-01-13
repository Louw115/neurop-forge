# Neurop Forge SDK

**Execute pre-verified, hash-locked function blocks with full audit trail.**

Neurop Forge provides 4,500+ pre-verified blocks that AI agents can search and execute - but never modify. This SDK is a thin wrapper around the hosted API.

## Installation

```bash
pip install neuropforge
```

## Quick Start

```python
from neuropforge import NeuropForge

# Initialize client
client = NeuropForge(api_key="your_api_key")

# Execute a block by exact name
result = client.execute("to_uppercase", text="hello world")
print(result.result)  # "HELLO WORLD"

# Search for blocks (discovery only)
blocks = client.search("validate email")
for block in blocks:
    print(f"{block.name} - {block.domain}/{block.operation}")

# List available blocks
blocks = client.list_blocks(limit=10, category="validation")
for block in blocks:
    print(f"{block.name}: {block.description}")
```

## CLI Usage

```bash
# Check API health
nf health

# List blocks
nf blocks --limit 10 --category validation

# Search for blocks
nf search "validate email"

# Execute a block
nf exec to_uppercase --input text="hello world"
nf exec string_length -i text="Neurop Forge"

# With JSON input
nf exec some_block --json '{"key": "value", "count": 42}'
```

## Configuration

Set your API key via environment variable:

```bash
export NEUROP_API_KEY="your_api_key"
```

Or pass it directly:

```python
client = NeuropForge(api_key="your_api_key")
```

## Why Neurop Forge?

- **Deterministic**: Same inputs always produce same outputs
- **Auditable**: Full execution trail with cryptographic verification
- **Secure**: AI can only execute verified blocks, never arbitrary code
- **Compliant**: Designed for SOC 2, HIPAA, PCI-DSS environments

## API Reference

### `NeuropForge(api_key, base_url, timeout)`

Initialize the client.

- `api_key`: Your API key (or set `NEUROP_API_KEY` env var)
- `base_url`: API URL (default: production API)
- `timeout`: Request timeout in seconds (default: 30)

### `client.execute(block_name, **inputs)`

Execute a block by exact name. Returns `ExecutionResult`.

### `client.search(query, limit)`

Search for blocks. Returns list of `SearchResult`.

### `client.list_blocks(limit, category)`

List available blocks. Returns list of `BlockInfo`.

### `client.health()`

Check API health. Returns dict.

### `client.stats()`

Get library statistics. Returns dict.

### `client.audit_chain()`

Get audit chain info. Returns dict.

## License

MIT
