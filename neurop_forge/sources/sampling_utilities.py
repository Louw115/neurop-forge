"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Sampling Utilities - Pure functions for sampling and randomization.
All functions are pure, deterministic, and atomic.
"""

import hashlib


def _hash_seed(seed: int, index: int) -> int:
    """Generate deterministic hash from seed and index."""
    h = hashlib.sha256(f"{seed}:{index}".encode()).digest()
    return int.from_bytes(h[:4], 'big')


def random_int(seed: int, min_val: int, max_val: int) -> int:
    """Generate deterministic random integer in range."""
    h = _hash_seed(seed, 0)
    return min_val + (h % (max_val - min_val + 1))


def random_float(seed: int) -> float:
    """Generate deterministic random float 0-1."""
    h = _hash_seed(seed, 0)
    return h / 0xFFFFFFFF


def random_float_range(seed: int, min_val: float, max_val: float) -> float:
    """Generate deterministic random float in range."""
    return min_val + random_float(seed) * (max_val - min_val)


def shuffle(items: list, seed: int) -> list:
    """Deterministically shuffle a list."""
    result = list(items)
    n = len(result)
    for i in range(n - 1, 0, -1):
        j = _hash_seed(seed, i) % (i + 1)
        result[i], result[j] = result[j], result[i]
    return result


def sample(items: list, k: int, seed: int) -> list:
    """Sample k items without replacement."""
    if k >= len(items):
        return shuffle(items, seed)
    result = []
    remaining = list(items)
    for i in range(k):
        idx = _hash_seed(seed, i) % len(remaining)
        result.append(remaining.pop(idx))
    return result


def sample_with_replacement(items: list, k: int, seed: int) -> list:
    """Sample k items with replacement."""
    if not items:
        return []
    return [items[_hash_seed(seed, i) % len(items)] for i in range(k)]


def weighted_choice(items: list, weights: list, seed: int):
    """Choose item based on weights."""
    if not items or len(items) != len(weights):
        return None
    total = sum(weights)
    if total <= 0:
        return items[0]
    target = random_float(seed) * total
    cumulative = 0
    for item, weight in zip(items, weights):
        cumulative += weight
        if cumulative >= target:
            return item
    return items[-1]


def weighted_sample(items: list, weights: list, k: int, seed: int) -> list:
    """Weighted sampling without replacement."""
    result = []
    remaining_items = list(items)
    remaining_weights = list(weights)
    for i in range(min(k, len(items))):
        if not remaining_items:
            break
        choice = weighted_choice(remaining_items, remaining_weights, seed + i)
        idx = remaining_items.index(choice)
        result.append(remaining_items.pop(idx))
        remaining_weights.pop(idx)
    return result


def reservoir_sample(items: list, k: int, seed: int) -> list:
    """Reservoir sampling for streaming data."""
    if len(items) <= k:
        return list(items)
    reservoir = list(items[:k])
    for i in range(k, len(items)):
        j = _hash_seed(seed, i) % (i + 1)
        if j < k:
            reservoir[j] = items[i]
    return reservoir


def stratified_sample(groups: dict, samples_per_group: int, seed: int) -> list:
    """Stratified sampling across groups."""
    result = []
    for i, (group_name, items) in enumerate(groups.items()):
        group_samples = sample(items, min(samples_per_group, len(items)), seed + i)
        result.extend(group_samples)
    return result


def systematic_sample(items: list, k: int, seed: int) -> list:
    """Systematic sampling with random start."""
    if k >= len(items):
        return list(items)
    interval = len(items) / k
    start = random_float(seed) * interval
    return [items[int(start + i * interval) % len(items)] for i in range(k)]


def bootstrap_sample(items: list, seed: int) -> list:
    """Bootstrap sample (same size as input, with replacement)."""
    return sample_with_replacement(items, len(items), seed)


def create_train_test_split(items: list, test_ratio: float, seed: int) -> dict:
    """Split items into train and test sets."""
    shuffled = shuffle(items, seed)
    split_idx = int(len(items) * (1 - test_ratio))
    return {
        "train": shuffled[:split_idx],
        "test": shuffled[split_idx:]
    }


def create_k_folds(items: list, k: int, seed: int) -> list:
    """Create k-fold cross-validation splits."""
    shuffled = shuffle(items, seed)
    fold_size = len(items) // k
    folds = []
    for i in range(k):
        start = i * fold_size
        end = start + fold_size if i < k - 1 else len(items)
        test = shuffled[start:end]
        train = shuffled[:start] + shuffled[end:]
        folds.append({"train": train, "test": test, "fold": i})
    return folds


def generate_uuid_v4(seed: int) -> str:
    """Generate deterministic UUID v4."""
    h = hashlib.sha256(str(seed).encode()).hexdigest()
    uuid = f"{h[:8]}-{h[8:12]}-4{h[13:16]}-{['8', '9', 'a', 'b'][_hash_seed(seed, 1) % 4]}{h[17:20]}-{h[20:32]}"
    return uuid


def generate_random_string(length: int, charset: str, seed: int) -> str:
    """Generate random string from charset."""
    return "".join(charset[_hash_seed(seed, i) % len(charset)] for i in range(length))


def generate_random_alphanumeric(length: int, seed: int) -> str:
    """Generate random alphanumeric string."""
    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return generate_random_string(length, charset, seed)


def generate_random_hex(length: int, seed: int) -> str:
    """Generate random hex string."""
    charset = "0123456789abcdef"
    return generate_random_string(length, charset, seed)


def coinflip(probability: float, seed: int) -> bool:
    """Biased coin flip."""
    return random_float(seed) < probability


def dice_roll(sides: int, seed: int) -> int:
    """Roll a die with n sides."""
    return random_int(seed, 1, sides)


def multiple_dice(count: int, sides: int, seed: int) -> list:
    """Roll multiple dice."""
    return [dice_roll(sides, seed + i) for i in range(count)]


def pick_n_of_m(n: int, m: int, seed: int) -> list:
    """Pick n items from range 0 to m-1."""
    return sample(list(range(m)), n, seed)


def normalize_weights(weights: list) -> list:
    """Normalize weights to sum to 1."""
    total = sum(weights)
    if total <= 0:
        return [1 / len(weights)] * len(weights) if weights else []
    return [w / total for w in weights]


def resample_with_noise(items: list, noise_ratio: float, seed: int) -> list:
    """Resample with some items replaced by random others."""
    result = list(items)
    for i in range(len(result)):
        if random_float(seed + i) < noise_ratio:
            j = random_int(seed + i + 1000, 0, len(items) - 1)
            result[i] = items[j]
    return result
