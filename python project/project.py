
# STUDENT EXAM PERFORMANCE ANALYSIS

import pandas as pd
import matplotlib.pyplot as plt

# 1. DATA LOADING
df = pd.read_csv("unclean_student_exam_performance (1).csv")

print("\nORIGINAL DATA")
print(df.head())
print("\nTotal Records:", len(df))

# 2. DATA CLEANING

# Remove duplicate records
df.drop_duplicates(subset="Student_ID", inplace=True)

# Clean column values
df["Student_ID"] = df["Student_ID"].astype(str).str.strip().str.upper()
df["Full_Name"] = df["Full_Name"].astype(str).str.strip().str.title()

# Convert numeric columns
cols = ["Age", "Hours_Studied_Per_Day", "Attendance_Pct",
        "Previous_Exam_Score", "Sleep_Hours",
        "Tutoring_Sessions_Per_Month", "Final_Exam_Score"]

for col in cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Replace invalid values with missing values
limits = {
    "Age": (14, 25),
    "Hours_Studied_Per_Day": (0, 16),
    "Attendance_Pct": (0, 100),
    "Previous_Exam_Score": (0, 100),
    "Sleep_Hours": (0, 24),
    "Tutoring_Sessions_Per_Month": (0, 20),
    "Final_Exam_Score": (0, 100)
}

for col, (low, high) in limits.items():
    df.loc[~df[col].between(low, high), col] = pd.NA
    df[col] = df[col].fillna(df[col].median())

# Clean gender
df["Gender"] = df["Gender"].astype(str).str.strip().str.lower()
df["Gender"] = df["Gender"].replace({
    "m": "Male", "male": "Male",
    "f": "Female", "female": "Female"
})
df["Gender"] = df["Gender"].str.title()
df.loc[~df["Gender"].isin(["Male", "Female"]), "Gender"] = "Unknown"

# Clean Yes/No columns
for col in ["Internet_Access", "Extracurricular_Activities"]:
    df[col] = df[col].astype(str).str.strip().str.lower()
    df[col] = df[col].replace({
        "yes": "Yes", "y": "Yes", "no": "No", "n": "No"
    })
    df.loc[~df[col].isin(["Yes", "No"]), col] = "Unknown"

# Save cleaned data
df.to_csv("cleaned_student_data.csv", index=False)

print("\nCLEANED DATA")
print(df.head())
print("\nTotal Clean Records:", len(df))

# 3. DATA ANALYSIS

print("\nSTUDENT PERFORMANCE ANALYSIS")

print("\nAverage Final Exam Score:")
print(df["Final_Exam_Score"].mean())

print("\nHighest Final Exam Score:")
print(df["Final_Exam_Score"].max())

print("\nLowest Final Exam Score:")
print(df["Final_Exam_Score"].min())

print("\nAverage Study Hours:")
print(df["Hours_Studied_Per_Day"].mean())

print("\nAverage Attendance:")
print(df["Attendance_Pct"].mean())

print("\nAverage Marks by Gender:")
print(df.groupby("Gender")["Final_Exam_Score"].mean())

print("\nCorrelation with Final Exam Score:")
print(df[cols].corr()["Final_Exam_Score"].sort_values(ascending=False))

# 4. DATA VISUALIZATION

# Graph 1: Exam Score Distribution
plt.figure(figsize=(7, 4))
plt.hist(df["Final_Exam_Score"], bins=10, edgecolor="black")
plt.title("Student Final Exam Score Distribution")
plt.xlabel("Final Exam Marks")
plt.ylabel("Number of Students")
plt.tight_layout()
plt.show()

# Graph 2: Study Hours vs Exam Score
plt.figure(figsize=(7, 4))
plt.scatter(df["Hours_Studied_Per_Day"],
            df["Final_Exam_Score"])
plt.title("Study Hours vs Final Exam Score")
plt.xlabel("Study Hours Per Day")
plt.ylabel("Final Exam Marks")
plt.tight_layout()
plt.show()

# Graph 3: Average Score by Gender
plt.figure(figsize=(7, 4))
df.groupby("Gender")["Final_Exam_Score"].mean().plot(
    kind="bar", edgecolor="black"
)
plt.title("Average Exam Score by Gender")
plt.xlabel("Gender")
plt.ylabel("Average Marks")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

print("\nPROJECT COMPLETED SUCCESSFULLY!")
