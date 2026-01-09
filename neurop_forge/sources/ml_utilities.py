"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
ML Utilities - Pure functions for machine learning patterns.
All functions are pure, deterministic, and atomic.
"""

def normalize_minmax(value: float, min_val: float, max_val: float) -> float:
    """Normalize a value using min-max scaling."""
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)


def denormalize_minmax(normalized: float, min_val: float, max_val: float) -> float:
    """Denormalize a min-max scaled value."""
    return normalized * (max_val - min_val) + min_val


def normalize_zscore(value: float, mean: float, std: float) -> float:
    """Normalize a value using z-score standardization."""
    if std == 0:
        return 0.0
    return (value - mean) / std


def denormalize_zscore(normalized: float, mean: float, std: float) -> float:
    """Denormalize a z-score standardized value."""
    return normalized * std + mean


def calculate_mean(values: list) -> float:
    """Calculate mean of values."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def calculate_std(values: list) -> float:
    """Calculate standard deviation of values."""
    if len(values) < 2:
        return 0.0
    mean = calculate_mean(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5


def calculate_minmax(values: list) -> dict:
    """Calculate min and max of values."""
    if not values:
        return {"min": 0, "max": 0}
    return {"min": min(values), "max": max(values)}


def one_hot_encode(value: str, categories: list) -> list:
    """One-hot encode a categorical value."""
    return [1 if cat == value else 0 for cat in categories]


def one_hot_decode(encoded: list, categories: list) -> str:
    """Decode a one-hot encoded value."""
    for i, val in enumerate(encoded):
        if val == 1 and i < len(categories):
            return categories[i]
    return ""


def label_encode(value: str, categories: list) -> int:
    """Label encode a categorical value."""
    if value in categories:
        return categories.index(value)
    return -1


def label_decode(encoded: int, categories: list) -> str:
    """Decode a label encoded value."""
    if 0 <= encoded < len(categories):
        return categories[encoded]
    return ""


def sigmoid(x: float) -> float:
    """Calculate sigmoid function."""
    import math
    if x < -500:
        return 0.0
    if x > 500:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


def relu(x: float) -> float:
    """Calculate ReLU function."""
    return max(0.0, x)


def leaky_relu(x: float, alpha: float) -> float:
    """Calculate Leaky ReLU function."""
    return x if x > 0 else alpha * x


def tanh(x: float) -> float:
    """Calculate hyperbolic tangent function."""
    import math
    return math.tanh(x)


def softmax(values: list) -> list:
    """Calculate softmax of values."""
    import math
    max_val = max(values) if values else 0
    exp_values = [math.exp(v - max_val) for v in values]
    sum_exp = sum(exp_values)
    if sum_exp == 0:
        return [0.0] * len(values)
    return [e / sum_exp for e in exp_values]


def binary_cross_entropy(predicted: float, actual: float) -> float:
    """Calculate binary cross-entropy loss."""
    import math
    epsilon = 1e-15
    predicted = max(epsilon, min(1 - epsilon, predicted))
    return -(actual * math.log(predicted) + (1 - actual) * math.log(1 - predicted))


def mean_squared_error(predictions: list, actuals: list) -> float:
    """Calculate mean squared error."""
    if len(predictions) != len(actuals) or not predictions:
        return 0.0
    return sum((p - a) ** 2 for p, a in zip(predictions, actuals)) / len(predictions)


def mean_absolute_error(predictions: list, actuals: list) -> float:
    """Calculate mean absolute error."""
    if len(predictions) != len(actuals) or not predictions:
        return 0.0
    return sum(abs(p - a) for p, a in zip(predictions, actuals)) / len(predictions)


def r_squared(predictions: list, actuals: list) -> float:
    """Calculate R-squared score."""
    if len(predictions) != len(actuals) or not predictions:
        return 0.0
    mean_actual = calculate_mean(actuals)
    ss_tot = sum((a - mean_actual) ** 2 for a in actuals)
    ss_res = sum((a - p) ** 2 for a, p in zip(actuals, predictions))
    if ss_tot == 0:
        return 0.0
    return 1 - (ss_res / ss_tot)


def accuracy_score(predictions: list, actuals: list) -> float:
    """Calculate accuracy score."""
    if len(predictions) != len(actuals) or not predictions:
        return 0.0
    correct = sum(1 for p, a in zip(predictions, actuals) if p == a)
    return correct / len(predictions)


def precision_score(predictions: list, actuals: list, positive_class) -> float:
    """Calculate precision score."""
    true_positives = sum(1 for p, a in zip(predictions, actuals) if p == positive_class and a == positive_class)
    predicted_positives = sum(1 for p in predictions if p == positive_class)
    if predicted_positives == 0:
        return 0.0
    return true_positives / predicted_positives


def recall_score(predictions: list, actuals: list, positive_class) -> float:
    """Calculate recall score."""
    true_positives = sum(1 for p, a in zip(predictions, actuals) if p == positive_class and a == positive_class)
    actual_positives = sum(1 for a in actuals if a == positive_class)
    if actual_positives == 0:
        return 0.0
    return true_positives / actual_positives


def f1_score(predictions: list, actuals: list, positive_class) -> float:
    """Calculate F1 score."""
    precision = precision_score(predictions, actuals, positive_class)
    recall = recall_score(predictions, actuals, positive_class)
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)


def confusion_matrix(predictions: list, actuals: list, classes: list) -> dict:
    """Calculate confusion matrix."""
    matrix = {c: {c2: 0 for c2 in classes} for c in classes}
    for p, a in zip(predictions, actuals):
        if a in matrix and p in matrix[a]:
            matrix[a][p] += 1
    return matrix


def train_test_split_indices(total: int, test_ratio: float, seed: int) -> dict:
    """Calculate train/test split indices deterministically."""
    import hashlib
    test_count = int(total * test_ratio)
    indices = list(range(total))
    for i in range(total - 1, 0, -1):
        hash_val = hashlib.sha256(f"{seed}:{i}".encode()).digest()
        j = int.from_bytes(hash_val[:4], 'big') % (i + 1)
        indices[i], indices[j] = indices[j], indices[i]
    return {
        "test": sorted(indices[:test_count]),
        "train": sorted(indices[test_count:])
    }


def kfold_indices(total: int, k: int) -> list:
    """Generate k-fold cross-validation indices."""
    fold_size = total // k
    folds = []
    for i in range(k):
        start = i * fold_size
        end = start + fold_size if i < k - 1 else total
        test_indices = list(range(start, end))
        train_indices = list(range(0, start)) + list(range(end, total))
        folds.append({"train": train_indices, "test": test_indices})
    return folds


def calculate_cosine_similarity(vec1: list, vec2: list) -> float:
    """Calculate cosine similarity between two vectors."""
    if len(vec1) != len(vec2) or not vec1:
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a ** 2 for a in vec1) ** 0.5
    magnitude2 = sum(b ** 2 for b in vec2) ** 0.5
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)


def calculate_euclidean_distance(vec1: list, vec2: list) -> float:
    """Calculate Euclidean distance between two vectors."""
    if len(vec1) != len(vec2):
        return 0.0
    return sum((a - b) ** 2 for a, b in zip(vec1, vec2)) ** 0.5


def calculate_manhattan_distance(vec1: list, vec2: list) -> float:
    """Calculate Manhattan distance between two vectors."""
    if len(vec1) != len(vec2):
        return 0.0
    return sum(abs(a - b) for a, b in zip(vec1, vec2))


def dot_product(vec1: list, vec2: list) -> float:
    """Calculate dot product of two vectors."""
    if len(vec1) != len(vec2):
        return 0.0
    return sum(a * b for a, b in zip(vec1, vec2))


def vector_magnitude(vec: list) -> float:
    """Calculate magnitude of a vector."""
    return sum(x ** 2 for x in vec) ** 0.5


def normalize_vector(vec: list) -> list:
    """Normalize a vector to unit length."""
    magnitude = vector_magnitude(vec)
    if magnitude == 0:
        return vec
    return [x / magnitude for x in vec]


def build_feature_vector(features: dict, feature_order: list) -> list:
    """Build a feature vector from a dictionary."""
    return [features.get(f, 0) for f in feature_order]


def extract_features_from_vector(vector: list, feature_order: list) -> dict:
    """Extract features from a vector into a dictionary."""
    return dict(zip(feature_order, vector))


def apply_threshold(probability: float, threshold: float) -> int:
    """Apply classification threshold to probability."""
    return 1 if probability >= threshold else 0


def calculate_auc_roc_approx(predictions: list, actuals: list, thresholds: int) -> float:
    """Calculate approximate AUC-ROC score."""
    auc = 0.0
    prev_fpr = 1.0
    prev_tpr = 1.0
    for i in range(thresholds + 1):
        threshold = i / thresholds
        preds = [1 if p >= threshold else 0 for p in predictions]
        tp = sum(1 for p, a in zip(preds, actuals) if p == 1 and a == 1)
        fp = sum(1 for p, a in zip(preds, actuals) if p == 1 and a == 0)
        tn = sum(1 for p, a in zip(preds, actuals) if p == 0 and a == 0)
        fn = sum(1 for p, a in zip(preds, actuals) if p == 0 and a == 1)
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        auc += (prev_fpr - fpr) * (prev_tpr + tpr) / 2
        prev_fpr, prev_tpr = fpr, tpr
    return auc


def format_classification_report(accuracy: float, precision: float, recall: float, f1: float) -> str:
    """Format a classification report."""
    return f"""Classification Report:
  Accuracy:  {accuracy:.4f}
  Precision: {precision:.4f}
  Recall:    {recall:.4f}
  F1 Score:  {f1:.4f}"""
