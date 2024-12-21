import numpy as np
from dataset import load_dataset
from train import train_model
from simulate import simulate_adversarial_attack
from tensorflow.keras.utils import to_categorical

if __name__ == "__main__":
    # Step 1: Load dataset
    X_train, X_test, y_train, y_test = load_dataset('creditcard.csv')
    print(f"Dataset shapes - X_train: {X_train.shape}, X_test: {X_test.shape}, y_train: {y_train.shape}, y_test: {y_test.shape}")

    # Step 2: Train the model
    model, scaler = train_model(X_train, y_train)

    # Step 3: Generate adversarial samples for testing
    X_test_adv = simulate_adversarial_attack(model, X_test, scaler)
    print(f"Adversarial test samples shape: {X_test_adv.shape}")

    # Step 4: Evaluate the model on adversarial samples
    y_pred_adv = model.predict(X_test_adv)
    if len(y_test.shape) == 1:
        adv_accuracy = np.mean(y_test == np.argmax(y_pred_adv, axis=1))
    else:
        adv_accuracy = np.mean(np.argmax(y_test, axis=1) == np.argmax(y_pred_adv, axis=1))
    print(f"Adversarial Accuracy on Test Data: {adv_accuracy:.4f}")

    # Step 5: Generate adversarial samples for training
    X_train_adv = simulate_adversarial_attack(model, X_train, scaler)

    # Step 6: Combine original and adversarial training data
    X_train_combined = np.concatenate((X_train, X_train_adv))
    y_train_combined = np.concatenate((y_train, y_train))
    print(f"Combined training data shapes - X_train_combined: {X_train_combined.shape}, y_train_combined: {y_train_combined.shape}")

    # Step 7: One-hot encode y_train_combined
    y_train_combined = to_categorical(y_train_combined, num_classes=2)

    # Step 8: Retrain the model with combined data
    model.fit(X_train_combined, y_train_combined, epochs=10, batch_size=32)

    # Step 9: Save the retrained model
    model.save("adversarially_trained_model.h5")
    print("Adversarially trained model saved successfully.")
