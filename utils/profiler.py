import pandas as pd


def profile_dataset(df: pd.DataFrame) -> dict:
    """Generate automatic insights from the uploaded dataset."""

    profile = {}

    # Basic info
    profile["rows"] = df.shape[0]
    profile["columns"] = df.shape[1]
    profile["column_names"] = list(df.columns)

    # Data types
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    text_cols = df.select_dtypes(include=["object"]).columns.tolist()
    profile["numeric_columns"] = numeric_cols
    profile["text_columns"] = text_cols

    # Missing values
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(1)
    profile["missing"] = {
        col: f"{pct}%" for col, pct in missing_pct.items() if pct > 0
    }

    # Numeric stats
    if numeric_cols:
        stats = {}
        for col in numeric_cols:
            stats[col] = {
                "min": df[col].min(),
                "max": df[col].max(),
                "mean": round(df[col].mean(), 2),
            }
        profile["stats"] = stats

    # Top correlations
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()
        pairs = []
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                col1 = numeric_cols[i]
                col2 = numeric_cols[j]
                value = round(corr.loc[col1, col2], 2)
                if abs(value) >= 0.5:
                    pairs.append((col1, col2, value))
        pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        profile["correlations"] = pairs[:5]

    # Unique values for text columns
    if text_cols:
        categories = {}
        for col in text_cols:
            unique = df[col].nunique()
            if unique <= 10:
                categories[col] = df[col].unique().tolist()
            else:
                categories[col] = f"{unique} unique values"
        profile["categories"] = categories

    return profile


def format_profile(profile: dict) -> str:
    """Format the profile into a readable string for display."""

    lines = []

    lines.append(f"**Rows:** {profile['rows']} | **Columns:** {profile['columns']}")
    lines.append("")

    # Missing values
    if profile["missing"]:
        lines.append("**⚠️ Missing Values:**")
        for col, pct in profile["missing"].items():
            lines.append(f"- {col}: {pct}")
        lines.append("")

    # Numeric stats
    if "stats" in profile:
        lines.append("**📈 Numeric Summary:**")
        for col, stat in profile["stats"].items():
            lines.append(f"- **{col}:** min={stat['min']}, max={stat['max']}, avg={stat['mean']}")
        lines.append("")

    # Correlations
    if "correlations" in profile and profile["correlations"]:
        lines.append("**🔗 Interesting Correlations:**")
        for col1, col2, value in profile["correlations"]:
            strength = "strong" if abs(value) >= 0.7 else "moderate"
            direction = "positive" if value > 0 else "negative"
            lines.append(f"- {col1} & {col2}: {value} ({strength} {direction})")
        lines.append("")

    # Categories
    if "categories" in profile:
        lines.append("**📂 Categories:**")
        for col, values in profile["categories"].items():
            if isinstance(values, list):
                lines.append(f"- **{col}:** {', '.join(str(v) for v in values)}")
            else:
                lines.append(f"- **{col}:** {values}")

    return "\n".join(lines)