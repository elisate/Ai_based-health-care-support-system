import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# ==============================
# 1️⃣ Load Dataset
# ==============================
data = pd.read_csv("health_dataset.csv")
print("Dataset loaded successfully!")
print("Columns:", data.columns.tolist())
print(f"Total samples: {len(data)}")

# ==============================
# 2️⃣ Preprocessing
# ==============================
# Convert Symptoms to lowercase
data['Symptoms'] = data['Symptoms'].str.lower()

# Drop missing rows (if any)
data.dropna(inplace=True)

# Feature
X = data['Symptoms']

# ==============================
# 3️⃣ Define Target Columns
# ==============================
target_columns = [
    'Diagnosis',
    'Recommended_Hospitals',
    'Hospital_Location',
    'Recommended_Doctors',
    'Medical_Supplies',
    'Medical_Resources'
]

# ==============================
# 4️⃣ Train & Save Model for Each Target
# ==============================
for target in target_columns:
    print(f"\n Training model for: {target}")

    y = data[target]

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Create pipeline (TF-IDF + Naive Bayes)
    model = make_pipeline(TfidfVectorizer(), MultinomialNB())

    # Train model
    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f" {target} Model Accuracy: {accuracy * 100:.2f}%")

    # Save model
    model_filename = f"{target.lower().replace(' ', '_')}_model.pkl"
    joblib.dump(model, model_filename)
    print(f" Saved model as {model_filename}")

print("\n All models trained and saved successfully!")

# ==============================
# 5️⃣ Test Prediction (Example)
# ==============================
test_symptom = ["fever, cough, fatigue"]

print("\n Testing all models with:", test_symptom)

for target in target_columns:
    model_filename = f"{target.lower().replace(' ', '_')}_model.pkl"
    model = joblib.load(model_filename)
    prediction = model.predict(test_symptom)[0]
    print(f"{target}: {prediction}")
