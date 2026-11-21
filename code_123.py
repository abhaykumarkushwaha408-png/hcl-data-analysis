import re
import numpy as np
import pandas as pd

# 1. Load the unclean dataset
input_file = "unclean_student_exam_performance.csv"
output_file = "cleaned_student_exam_performance.csv"
df = pd.read_csv(input_file)

# 2. Normalize missing-value placeholders to NaN
missing_tokens = ["", " ", "n/a", "na", "null", "none", "?", "missing", "nan"]
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].apply(
        lambda x: np.nan
        if isinstance(x, str) and x.strip().lower() in missing_tokens
        else x
    )

# 3. Clean text identifiers and names
df["Full_Name"] = df["Full_Name"].apply(
    lambda x: re.sub(r"\s+", " ", x.strip()).title() if isinstance(x, str) else np.nan
)
df["Student_ID"] = df["Student_ID"].apply(
    lambda x: re.sub(r"[^A-Z0-9]", "", x.strip().upper())
    if isinstance(x, str)
    else np.nan
)

# 4. Standardize categorical values
gender_map = {
    "male": "Male",
    "m": "Male",
    "female": "Female",
    "f": "Female",
}
df["Gender"] = df["Gender"].apply(
    lambda x: gender_map.get(x.strip().lower(), "Other/Unknown")
    if isinstance(x, str)
    else "Other/Unknown"
)

yes_no_map = {
    "yes": "Yes",
    "y": "Yes",
    "1": "Yes",
    "true": "Yes",
    "no": "No",
    "n": "No",
    "0": "No",
    "false": "No",
}
for col in ["Extracurricular_Activities", "Internet_Access"]:
    df[col] = df[col].apply(
        lambda x: yes_no_map.get(x.strip().lower(), np.nan)
        if isinstance(x, str)
        else x
    )

edu_map = {
    "high school": "High School",
    "highschool": "High School",
    "hs": "High School",
    "bachelor's": "Bachelor's",
    "bachelors": "Bachelor's",
    "b.sc": "Bachelor's",
    "bsc": "Bachelor's",
    "master's": "Master's",
    "masters": "Master's",
    "m.sc": "Master's",
    "msc": "Master's",
    "phd": "PhD",
    "none": "None",
}
df["Parental_Education"] = df["Parental_Education"].apply(
    lambda x: edu_map.get(x.strip().lower(), np.nan)
    if isinstance(x, str)
    else x
)

# 5. Parse numeric columns (handle units like "4.3 hrs", "85.2%", and word numbers)
word_to_num = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def parse_numeric(val):
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().lower()
    if s in word_to_num:
        return float(word_to_num[s])
    match = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(match.group()) if match else np.nan


numeric_cols = [
    "Age",
    "Hours_Studied_Per_Day",
    "Attendance_Pct",
    "Previous_Exam_Score",
    "Sleep_Hours",
    "Tutoring_Sessions_Per_Month",
    "Final_Exam_Score",
]
for col in numeric_cols:
    df[col] = df[col].apply(parse_numeric)

# 6. Replace impossible / out-of-range values with NaN before imputation
bounds = {
    "Age": (10, 25),
    "Hours_Studied_Per_Day": (0.0, 16.0),
    "Attendance_Pct": (0.0, 100.0),
    "Previous_Exam_Score": (0.0, 100.0),
    "Sleep_Hours": (0.0, 16.0),
    "Tutoring_Sessions_Per_Month": (0.0, 30.0),
    "Final_Exam_Score": (0.0, 100.0),
}
for col, (low, high) in bounds.items():
    df.loc[(df[col] < low) | (df[col] > high), col] = np.nan

# 7. Remove exact and near-duplicate records
df = df.drop_duplicates(subset=["Student_ID", "Full_Name"], keep="first").reset_index(
    drop=True
)

# 8. Impute remaining missing values (median for numeric, mode for categorical)
for col in numeric_cols:
    df[col] = df[col].fillna(df[col].median())

for int_col in ["Age", "Tutoring_Sessions_Per_Month"]:
    df[int_col] = df[int_col].round().astype(int)

for float_col in [
    "Hours_Studied_Per_Day",
    "Attendance_Pct",
    "Previous_Exam_Score",
    "Sleep_Hours",
    "Final_Exam_Score",
]:
    df[float_col] = df[float_col].round(1)

for cat_col in ["Extracurricular_Activities", "Internet_Access", "Parental_Education"]:
    df[cat_col] = df[cat_col].fillna(df[cat_col].mode()[0])

# 9. Save with UTF-8 BOM for clean opening in Excel
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"Saved cleaned dataset with {len(df)} rows to {output_file}")