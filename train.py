from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import StandardScaler

def train_model(X_train, y_train):
    # Scale data
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)

    # Convert labels to categorical
    y_train = to_categorical(y_train)

    # Build a simple neural network
    model = Sequential([
        Dense(64, input_dim=X_train.shape[1], activation='relu'),
        Dense(32, activation='relu'),
        Dense(2, activation='softmax')  # Assuming binary classification (0 and 1)
    ])

    # Compile the model
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Train the model
    model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=1)
    return model, scaler

