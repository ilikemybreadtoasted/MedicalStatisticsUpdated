def patient_status_counts(df):
    statuses = ["Active", "Recovered", "Critical"]

    if df.empty:
        return {s: 0 for s in statuses}

    counts = df["status"].value_counts()

    return {
        status: int(counts.get(status, 0))
        for status in statuses
    }
