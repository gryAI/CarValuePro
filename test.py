import os
import ast
from dotenv import load_dotenv
import pandas as pd
from src.data_pipeline.extract import extract
from src.data_pipeline.load import (
    get_db_creds,
    create_db_engine,
    create_db_connection,
    check_table_exists,
    create_staging_table,
)

load_dotenv()

engine = create_db_engine("CVP_FINAL")

# Load your DataFrame
df = pd.read_sql("SELECT * FROM cvp_incremental_load_20240910", engine)


# Convert only valid list-like strings
def convert_to_list(x):
    if pd.isna(x):  # Handle NaN values
        return []
    if isinstance(x, str) and (
        x.startswith("{") or x.startswith("[")
    ):  # Check if it's a string that looks like a list
        try:
            # Replace curly braces with square brackets for Postgres-style arrays and evaluate
            x = x.replace("{", "[").replace("}", "]")
            return [item for item in ast.literal_eval(x) if item]
        except (ValueError, SyntaxError):  # Handle any invalid formatting issues
            return x  # Return as is if not a valid list
    return x  # Return non-list values as is


# Apply the function to the 'negotiation_and_test_drive' column
df["negotiation_and_test_drive"] = df["negotiation_and_test_drive"].apply(
    convert_to_list
)

# Check the result
print(df[["negotiation_and_test_drive"]].head())


# ALTERNATIVE
# Function to convert PostgreSQL array strings to Python lists
def convert_pg_array(pg_array_str):
    # If the column value is a string with curly braces
    if (
        isinstance(pg_array_str, str)
        and pg_array_str.startswith("{")
        and pg_array_str.endswith("}")
    ):
        # Remove the curly braces and split the string by commas
        return pg_array_str.strip("{}").split(",")
    return pg_array_str


# Apply the conversion function to specific columns
# Replace 'array_column' with the name of your column
df["array_column"] = df["array_column"].apply(convert_pg_array)

# If you have multiple array columns, apply to each column
array_columns = ["array_column1", "array_column2"]  # list of array columns
for col in array_columns:
    df[col] = df[col].apply(convert_pg_array)
