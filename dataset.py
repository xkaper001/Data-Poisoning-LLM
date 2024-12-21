import pandas as pd
from sklearn.model_selection import train_test_split

def load_dataset(path):
    """
    Loads the dataset and splits it into training and testing sets.

    Args:
        path (str): Path to the dataset file (CSV).

    Returns:
        tuple: X_train, X_test, y_train, y_test
    """
    # Load dataset
    data = pd.read_csv(path)  # Correctly load the CSV file using pandas

    # Separate features and target
    X = data.drop('Class', axis=1)
    y = data['Class']

    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

# Main block to test the function
if __name__ == "__main__":
    # Call the function and print the shapes of the splits
    X_train, X_test, y_train, y_test = load_dataset('creditcard.csv')  # Use the correct file path
    print("X_train shape: {}, X_test shape: {}".format(X_train.shape, X_test.shape))
    print("y_train shape: {}, y_test shape: {}".format(y_train.shape, y_test.shape))
