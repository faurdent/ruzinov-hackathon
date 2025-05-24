import pandas as pd
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers


def load_dataset(csv_path: str):
    """Load dataset and return features and target arrays."""
    data = pd.read_csv(csv_path)
    print(data)

    feature_cols = [
        'Outdoor_Temperature',
        "Indoor_Temperature",
        'Humidity',
        'CO2_Levels',
        'Occupancy',
        "Solar_Radiation" ,
        "Wind_Speed",
        'Energy_Usage',
    ]
    X = data[feature_cols].values
    y = data['Energy_Usage'].values
    import matplotlib.pyplot as plt

    plt.figure(figsize=(14, 7))
    plt.plot(data['Timestamp'], data['Energy_Usage'], marker='.', linestyle='-')

    plt.title('Energy Consumption Over Time')
    plt.xlabel('Datetime')
    plt.ylabel('Energy Consumption (units)')
    plt.grid(True)

    plt.gcf().autofmt_xdate()

    plt.show()
    # return

    return X, y


def build_mlp(input_dim: int) -> keras.Model:
    """Build and compile a deep multilayer perceptron model."""
    model = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(128, activation='relu'),
        layers.Dense(64, activation='relu'),
        layers.Dense(64, activation='relu'),
        layers.Dense(32, activation='relu'),
        layers.Dense(32, activation='relu'),
        layers.Dense(16, activation='relu'),
        layers.Dense(1, activation='linear'),
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model


def main():
    csv_path = '1_Year_Sensor___Energy_Usage_Dataset__7_15_Work_Hours_.csv'
    X, y = load_dataset(csv_path)
    print(y)
    # return
    # Simple train/test split
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model = build_mlp(X.shape[1])
    model.summary()

    model.fit(
        X_train,
        y_train,
        # validation_data=(X_test, y_test),
        epochs=50,
        batch_size=32,
    )

    # print(y_test)
    predictions = model.predict(X_test)
    model.save('energy_mlp_model.h5')


if __name__ == '__main__':
    main()
