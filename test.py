import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Creating a DataFrame with points data
data = {
    'Team': ['Arsenal', 'Liverpool', 'Aston Villa', 'Manchester City', 'Tottenham Hotspur',
             'Manchester United', 'Newcastle United', 'Brighton & Hove Albion', 'West Ham United',
             'Chelsea', 'Brentford', 'Fulham', 'Wolverhampton Wanderers', 'Crystal Palace',
             'AFC Bournemouth', 'Nottingham Forest', 'Luton Town', 'Everton', 'Burnley', 'Sheffield United'],
    'Points': [36, 34, 32, 30, 27, 27, 26, 25, 21, 19, 19, 18, 18, 16, 16, 13, 9, 7, 7, 5]
}

df = pd.DataFrame(data)

# Adding a binary target variable indicating if the team is Newcastle United
df['IsNewcastle'] = (df['Team'] == 'Newcastle United').astype(int)

# Creating features and target variable
X = df[['Points']]
y = df['IsNewcastle']

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Training the XGBoost model
model = XGBClassifier()
model.fit(X_train, y_train)

# Making predictions on the test set
predictions = model.predict(X_test)

# Calculating the probability of Newcastle winning against Everton (7 points vs. 26 points)
newcastle_points = 5000000
everton_points = 7
prob_newcastle_wins = model.predict_proba([[newcastle_points]])[0, 1]

print(f"Probability of Newcastle winning against Everton: {prob_newcastle_wins * 100:.2f}%")






