import numpy as np
from art.attacks.evasion import FastGradientMethod, ProjectedGradientDescent
from art.estimators.classification import TensorFlowV2Classifier
from tensorflow.keras.losses import CategoricalCrossentropy
import matplotlib.pyplot as plt


from train import train_model
from dataset import load_dataset
from visualize import visualize_adversarial_samples

def generate_adversarial_samples(classifier, X_test, attack_type = "FGSM"):
    if attack_type == "FGSM":
        attack = FastGradientMethod(estimator = classifier, eps = 0.1)
    elif attack_type == "PGD":
        attack = ProjectedGradientDescent(estimator = classifier, eps = 0.2, eps_step = 0.02, max_iter = 40)
    else:
        raise ValueError(f"Unsupported attack type: {attack_type}")
    
    return attack.generate(x=X_test)

def evaluate_adversarial_samples(mode, X_test_adv, y_test):
    y_pred_adv = model.predict(X_test_adv)
    if len(y_test.shape) == 1:  # If y_test is 1D
        adv_accuracy = np.mean(y_test == np.argmax(y_pred_adv, axis=1))
    else:  # If y_test is 2D (one-hot encoded)
        adv_accuracy = np.mean(np.argmax(y_test, axis=1) == np.argmax(y_pred_adv, axis=1))
    
    print(f"Adversarial Accuracy: {adv_accuracy:.4f}")
    return adv_accuracy
    return adv_accuracy

def visualize_adversarial_samples(X_test, X_test_adv, sample_indices=[0, 1, 2], attack_name="Adversarial"):
    for idx in sample_indices:
        plt.figure(figsize=(10, 5))

        # Check if X_test is a DataFrame or NumPy array and access rows correctly
        if isinstance(X_test, np.ndarray):
            original_sample = X_test[idx]
        else:  # If it's a DataFrame
            original_sample = X_test.iloc[idx]

        adversarial_sample = X_test_adv[idx]

        # Plot original and adversarial samples
        plt.plot(original_sample, label="Original Sample", alpha=0.7)
        plt.plot(adversarial_sample, label=f"{attack_name} Adversarial Sample", linestyle="--", alpha=0.7)

        # Add titles and labels
        plt.title(f"Comparison of Original and {attack_name} Adversarial Inputs (Sample {idx})")
        plt.xlabel("Features (excluding 'Time')" if isinstance(original_sample, np.ndarray) else "Feature Names")
        plt.ylabel("Scaled Feature Values")
        plt.legend()
        plt.show()

if __name__ == "__main__":
    X_train, X_test, y_train, y_test = load_dataset("creditcard.csv")
    model, scaler = train_model(X_train, y_train)

    classifier = TensorFlowV2Classifier(
        model = model,
        loss_object = CategoricalCrossentropy(),
        input_shape = (X_test.shape[1],),
        nb_classes = 2,
        clip_values = (np.min(X_test), np.max(X_test)),

    )

    X_test_adv_fgsm = generate_adversarial_samples(classifier, scaler.transform(X_test), attack_type = "FGSM")
    print("FGSM Adversarial Samples Generated.")

    adv_accuracy_fgsm = evaluate_adversarial_samples(model, scaler.inverse_transform(X_test_adv_fgsm), y_test)
    print(f"FGSM Adversarial Accuracy: {adv_accuracy_fgsm:.4f}")

    X_test_adv_pgd = generate_adversarial_samples(classifier, scaler.transform(X_test), attack_type="PGD")
    print("PGD Adversarial Samples Generated.")

    adv_accuracy_pgd = evaluate_adversarial_samples(model, scaler.inverse_transform(X_test_adv_pgd), y_test)
    print(f"PGD Adversarial Accuracy: {adv_accuracy_pgd:.4f}")

    visualize_adversarial_samples(X_test, X_test_adv_fgsm, sample_indices=[0, 1, 2], attack_name="FGSM")
    visualize_adversarial_samples(X_test, X_test_adv_pgd, sample_indices=[0, 1, 2], attack_name="PGD")
