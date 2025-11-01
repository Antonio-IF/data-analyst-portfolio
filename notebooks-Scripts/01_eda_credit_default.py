# Import libraries. 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import warnings
import openpyxl

# Filter out warnings
warnings.filterwarnings('ignore')

# Load dataset. 
df = pd.read_excel("../data/raw/default_credit.xls", header=1)

# show dataframe 
# friendly reminder: default payment next month = Y and ID is the customer ID, and 
# other columns use for X1, X2, ..., X3, Xn. 
#df.head()

##### DATASET OVERVIEW
# Get dataset dimensions
# df.shape
# Get column names and data types
df.info()
# Get column names only
#df.columns
# Check for missing values
#df.isnull().sum()
# Get unique values in each column
# df.nunique()

##### CONVERT DATA TYPES
# Convert categorical variables to proper categories
categorical_cols = ['SEX', 'EDUCATION', 'MARRIAGE', 'PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']

for col in categorical_cols:
    if col in df.columns:
        df[col] = df[col].astype('category')

# Or convert to specific categories with meaningful labels
# df['SEX'] = df['SEX'].map({1: 'Male', 2: 'Female'}).astype('category')
# df['EDUCATION'] = df['EDUCATION'].map({1: 'Graduate School', 2: 'University', 3: 'High School', 4: 'Others'}).astype('category')
# df['MARRIAGE'] = df['MARRIAGE'].map({1: 'Married', 2: 'Single', 3: 'Others'}).astype('category')

# Convert numerical variables to proper numeric types
numerical_cols = ['LIMIT_BAL', 'AGE', 'BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6',
                  'PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6']

for col in numerical_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Convert ID column
df['ID'] = df['ID'].astype('object')
df.info()

##### DESCRIPTIVE STATISTICS
# Get count, mean, std, min, max, and 25%, 50%, 75% quantiles for numerical variables
df.describe(exclude='category', include='int64')   
# Get count, mean, std, min, max, and 25%, 50%, 75% quantiles for categorical variables
df.describe(exclude='int64', include='category') 
# Correlation matrix (for numerical variables)
# correlation_matrix = df.corr(numeric_only=True) 
# In this case, the correlation matrix is not very useful 
# because the variables are not correlated. 
# However, we can see that the variables are correlated with the target variable. 
# plt.figure(figsize=(12, 12)) # Adjust figure size as needed
# sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
# plt.title('Correlation Matrix Heatmap')
# plt.show()

##### MISSING VALUES, DUPLICATES, OUTLIERS
# Check for missing values
missing_data = df.isnull().sum()
missing_percentage = (missing_data / len(df)) * 100
missing_summary = pd.DataFrame({
    'Missing_Count': missing_data,
    'Missing_Percentage': missing_percentage
})
print("Missing Data Summary:")
print(missing_summary[missing_summary['Missing_Count'] > 0])

# Check for duplicates
duplicates = df.duplicated().sum()
print(f"\nDuplicate rows: {duplicates}")

# Check for outliers in numerical variables
def detect_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return len(outliers), lower_bound, upper_bound

numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
outlier_summary = {}
for col in numerical_cols:
    if col not in ['ID', 'default payment next month']:
        count, lower, upper = detect_outliers(df, col)
        outlier_summary[col] = {'count': count, 'lower': lower, 'upper': upper}

print("\nOutlier Summary:")
for col, info in outlier_summary.items():
    print(f"{col}: {info['count']} outliers")


##### TARGET VARIABLE DISTRIBUTION
# Analyze the target variable distribution
target_distribution = df['default payment next month'].value_counts()
target_percentage = df['default payment next month'].value_counts(normalize=True)

print("Target Variable Distribution:")
print(f"Default (1): {target_distribution[1]} ({target_percentage[1]:.2%})")
print(f"No Default (0): {target_distribution[0]} ({target_percentage[0]:.2%})")

# Check for class imbalance
imbalance_ratio = target_distribution[1] / target_distribution[0]
print(f"Class Imbalance Ratio: {imbalance_ratio:.2f}")

##### CORRELATION ANALYSIS
correlation_with_target = df[numerical_cols].corrwith(df['default payment next month'])
correlation_df = pd.DataFrame({
    'Correlation_with_Target': correlation_with_target
}).sort_values('Correlation_with_Target', ascending=False)

print(correlation_df)

##### DATA VISUALIZATIONS
# Set up the plotting style
plt.style.use('seaborn-v0_8')
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# 1. Target variable distribution
axes[0,0].pie(target_distribution.values, labels=['No Default', 'Default'], autopct='%1.1f%%')
axes[0,0].set_title('Default Distribution')

# 2. Credit limit distribution by default status
axes[0,1].hist(df[df['default payment next month']==0]['LIMIT_BAL'], alpha=0.7, label='No Default', bins=30)
axes[0,1].hist(df[df['default payment next month']==1]['LIMIT_BAL'], alpha=0.7, label='Default', bins=30)
axes[0,1].set_xlabel('Credit Limit')
axes[0,1].set_ylabel('Frequency')
axes[0,1].set_title('Credit Limit Distribution by Default Status')
axes[0,1].legend()

# 3. Age distribution by default status
axes[0,2].boxplot([df[df['default payment next month']==0]['AGE'], 
                   df[df['default payment next month']==1]['AGE']], 
                  labels=['No Default', 'Default'])
axes[0,2].set_ylabel('Age')
axes[0,2].set_title('Age Distribution by Default Status')

# 4. Payment behavior analysis
payment_cols = ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']
default_payment_counts = df[df['default payment next month']==1][payment_cols].apply(pd.Series.value_counts)
no_default_payment_counts = df[df['default payment next month']==0][payment_cols].apply(pd.Series.value_counts)

axes[1,0].bar(range(len(payment_cols)), default_payment_counts.iloc[0], alpha=0.7, label='Default')
axes[1,0].bar(range(len(payment_cols)), no_default_payment_counts.iloc[0], alpha=0.7, label='No Default')
axes[1,0].set_xlabel('Payment Month')
axes[1,0].set_ylabel('Count')
axes[1,0].set_title('Payment Behavior Analysis')
axes[1,0].set_xticks(range(len(payment_cols)))
axes[1,0].set_xticklabels(payment_cols, rotation=45)
axes[1,0].legend()

# 5. Education vs Default
education_default = pd.crosstab(df['EDUCATION'], df['default payment next month'])
education_default.plot(kind='bar', ax=axes[1,1])
axes[1,1].set_title('Education Level vs Default Status')
axes[1,1].set_xlabel('Education Level')
axes[1,1].set_ylabel('Count')
axes[1,1].legend(['No Default', 'Default'])

# 6. Marital status vs Default
marriage_default = pd.crosstab(df['MARRIAGE'], df['default payment next month'])
marriage_default.plot(kind='bar', ax=axes[1,2])
axes[1,2].set_title('Marital Status vs Default Status')
axes[1,2].set_xlabel('Marital Status')
axes[1,2].set_ylabel('Count')
axes[1,2].legend(['No Default', 'Default'])

plt.tight_layout()
plt.show()

##### FEATURE ENGINEERING
# Create new features
df['PAYMENT_RATIO'] = df['PAY_AMT1'] / (df['BILL_AMT1'] + 1)  # Add 1 to avoid division by zero
df['AVG_BILL_AMT'] = df[['BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6']].mean(axis=1)
df['AVG_PAY_AMT'] = df[['PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6']].mean(axis=1)
df['AVG_CREDIT_UTILIZATION'] = df['AVG_PAY_AMT'] / df['LIMIT_BAL']
# Payment behavior score
df['PAYMENT_SCORE'] = df[payment_cols].apply(lambda x: (x == -1).sum(), axis=1)

print("New Features Created:")
print(df[['AVG_CREDIT_UTILIZATION', 'PAYMENT_RATIO', 'AVG_BILL_AMT', 'AVG_PAY_AMT', 'PAYMENT_SCORE']].describe())

##### SUMMARY AND INSIGHTS
# Key insights summary
print("=== CREDIT DEFAULT ANALYSIS - KEY INSIGHTS ===\n")

print("1. DATASET OVERVIEW:")
print(f"   - Total records: {len(df):,}")
print(f"   - Default rate: {target_percentage[1]:.2%}")
print(f"   - Features: {len(df.columns)}")

print("\n2. RISK FACTORS:")
print("   - High correlation features with default:")
for idx, row in correlation_df.head(5).iterrows():
    print(f"     * {idx}: {row['Correlation_with_Target']:.3f}")

print("\n3. DEMOGRAPHIC INSIGHTS:")
print(f"   - Average age: {df['AGE'].mean():.1f} years")
print(f"   - Gender distribution: {df['SEX'].value_counts().to_dict()}")
print(f"   - Education distribution: {df['EDUCATION'].value_counts().to_dict()}")

print("\n4. FINANCIAL INSIGHTS:")
print(f"   - Average credit limit: ${df['LIMIT_BAL'].mean():,.0f}")
print(f"   - Average bill amount: ${df['AVG_BILL_AMT'].mean():,.0f}")
print(f"   - Average payment amount: ${df['AVG_PAY_AMT'].mean():,.0f}")

print("\n5. TARGET VARIABLE INSIGHTS {Y}:")
print(f"  - Target Variable Distribution:")
print(f"  - Default (1): {target_distribution[1]} ({target_percentage[1]:.2%})")
print(f"  - No Default (0): {target_distribution[0]} ({target_percentage[0]:.2%})")

# EXPORT DATASET 

df.to_excel('../data/raw/default_credit_new.xlsx')

# CONCLUSIONS...

# - About **22%** of customers defaulted on their payments.
# - The variable `LIMIT_BAL` tends to be lower among customers who default.
# - `BILL_AMTx` features are highly correlated with each other, but show little direct correlation with the default variable.
# - There is a significant **class imbalance** in the dataset (1 default vs 3.5 no-default).
# - Engineered features like `CREDIT_UTILIZATION` and `PAYMENT_SCORE` provide valuable signals about risk behavior.

# 📌 This EDA will serve as the foundation for predictive modeling in future notebooks.




