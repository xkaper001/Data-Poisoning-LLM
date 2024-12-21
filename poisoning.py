import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from train import train_model
import pandas as pd
from dataset import load_dataset

def flip_labels(y_train, flip_fraction=0.1):
    # Ensure y_train is a NumPy array for consistent indexing
    if isinstance(y_train, pd.Series):
        y_train = y_train.to_numpy()

    y_train_flipped = y_train.copy()
    n_flips = int(len(y_train) * flip_fraction)
    flip_indices = np.random.choice(len(y_train), n_flips, replace=False)

    for idx in flip_indices:
        y_train_flipped[idx] = 1 - y_train_flipped[idx]  # Flip binary labels (0 -> 1, 1 -> 0)

    return y_train_flipped

    return y_train_flipped

def evaluate_poisoned_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_pred_labels = np.argmax(y_pred, axis=1)  # Convert probabilities to class labels
    accuracy = accuracy_score(y_test, y_pred_labels)
    return accuracy

if __name__ == "__main__":
    # Step 1: Load the dataset
    X_train, X_test, y_train, y_test = load_dataset("creditcard.csv")
    print(f"Original Dataset Shapes - X_train: {X_train.shape}, y_train: {y_train.shape}")

    # Step 2: Poison the training labels
    flip_fraction = 0.1  # Flip 10% of the labels
    y_train_poisoned = flip_labels(y_train, flip_fraction=flip_fraction)
    print(f"Flipped {flip_fraction * 100}% of the training labels.")

    # Step 3: Train a model on poisoned data
    print("Training model on poisoned data...")
    poisoned_model, scaler = train_model(X_train, y_train_poisoned)

    # Step 4: Evaluate the poisoned model
    print("Evaluating poisoned model...")
    accuracy_poisoned = evaluate_poisoned_model(poisoned_model, scaler.transform(X_test), y_test)
    print(f"Accuracy of poisoned model on test data: {accuracy_poisoned:.4f}")

    # Step 5: Train and evaluate the model on clean data for comparison
    print("Training model on clean data for comparison...")
    clean_model, _ = train_model(X_train, y_train)
    accuracy_clean = evaluate_poisoned_model(clean_model, scaler.transform(X_test), y_test)
    print(f"Accuracy of clean model on test data: {accuracy_clean:.4f}")

    # Step 6: Compare results
    print(f"Accuracy Drop Due to Poisoning: {accuracy_clean - accuracy_poisoned:.4f}")
