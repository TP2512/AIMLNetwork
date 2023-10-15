import pandas as pd

# Create a sample DataFrame
data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
df = pd.DataFrame(data)

# Print the original DataFrame
print("Original DataFrame:")
print(df)

# Change the value at row 0, column 'A' to 99
df.at[0, 'A'] = 99

# Print the DataFrame after the change
print("\nDataFrame after changing cell value:")
print(df)
