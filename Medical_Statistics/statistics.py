import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind,t
import numpy as np
from scipy.stats import norm

CSV_PATH = "C:\\Users\\Atharv\\OneDrive\\Desktop\\Medical_Statistics\\disease_data.csv"

def statistics_dashboard():
    st.set_page_config(layout="wide")
    st.title("📊 Medical Analytics Dashboard")
    # ---------------- LOAD DATA ----------------
    try:
        df = pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        st.error("No disease_data.csv found yet.")
        return
    df.columns = df.columns.str.strip().str.lower()
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["recovery time"] = pd.to_numeric(df["recovery time"], errors="coerce")
    df.dropna(inplace=True)
    if df.empty:
        st.warning("No data available for analysis.")
        return
    # ================== TABS ==================
    tab1, tab2, tab3 = st.tabs([
        "Disease Frequency",
        "Disease Specific Analysis",
        "Hypothesis Testing"
    ])

    #ALL DISEASE ANALYSIS
    with tab1:
        st.subheader("Disease Frequency Overview")
        disease_counts = df["disease"].value_counts()
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        ax1.bar(disease_counts.index, disease_counts.values)
        ax1.set_xlabel("Disease")
        ax1.set_ylabel("Frequency")
        ax1.set_title("Disease Frequency")
        plt.xticks(rotation=45)
        st.pyplot(fig1, use_container_width=True)
        st.subheader("Mean Recovery Time by Disease")
        mean_recovery = (
        df.groupby("disease")["recovery time"]
        .mean()
        .sort_values(ascending=False)
    )
        fig_mean, ax_mean = plt.subplots(figsize=(10, 5))
        ax_mean.bar(mean_recovery.index, mean_recovery.values)
        ax_mean.set_xlabel("Disease")
        ax_mean.set_ylabel("Mean Recovery Time (days)")
        ax_mean.set_title("Average Recovery Time per Disease")
        plt.xticks(rotation=45)
        st.pyplot(fig_mean, use_container_width=True)

    # Optional: Display Table
        st.dataframe(
        mean_recovery.reset_index().rename(
            columns={"recovery time": "Mean Recovery Time"}
        ),
        use_container_width=True
    )

    #Disease Specific Analysis
    with tab2:
        selected_disease = st.selectbox(
            "Select Disease",
            sorted(df["disease"].unique())
        )
        disease_df = df[df["disease"] == selected_disease].copy()
        st.subheader("Recovery Time vs Age")
        col1, col2 = st.columns(2)

        # Scatter Plot
        with col1:
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            ax2.scatter(disease_df["age"], disease_df["recovery time"])
            ax2.set_xlabel("Age")
            ax2.set_ylabel("Recovery Time (days)")
            ax2.set_title("Age vs Recovery")
            st.pyplot(fig2, use_container_width=True)

        # Correlation Display
        with col2:
            correlation = disease_df["age"].corr(disease_df["recovery time"])
            st.metric("Correlation (Age vs Recovery)", f"{correlation:.3f}")

            if correlation > 0.5:
                st.success("Strong positive correlation")
            elif correlation < -0.5:
                st.success("Strong negative correlation")
            elif abs(correlation) > 0.3:
                st.info("Moderate correlation")
            else:
                st.warning("Weak or no correlation")

        st.divider()

        # Distribution Plots
        col3, col4 = st.columns(2)

        with col3:
            fig3, ax3 = plt.subplots(figsize=(6, 4))
            ax3.hist(disease_df["age"], bins=10)
            ax3.set_title("Age Distribution")
            st.pyplot(fig3, use_container_width=True)
            for spine in ax3.spines.values():
                spine.set_visible(True)
                spine.set_color("black")
                spine.set_linewidth(1.5)

        with col4:
            fig4, ax4 = plt.subplots(figsize=(6, 4))
            ax4.hist(disease_df["recovery time"], bins=10)
            ax4.set_title("Recovery Time Distribution")
            st.pyplot(fig4, use_container_width=True)

        st.divider()

        # Quick Metrics
        st.subheader("Quick Insights")
        m1, m2, m3 = st.columns(3)
        m1.metric("Avg Recovery (days)", f"{disease_df['recovery time'].mean():.1f}")
        m2.metric("Min Age", int(disease_df["age"].min()))
        m3.metric("Max Age", int(disease_df["age"].max()))

    #Hypothesis Testing
    with tab3:
        st.subheader("Male vs Female Recovery Time (Disease Specific)")

        if "gender" not in df.columns:
            st.warning("Gender column not found.")
            return

    # Select Disease
        selected_disease_ht = st.selectbox(
            "Select Disease for Hypothesis Testing",
            sorted(df["disease"].unique())
         )

        disease_df = df[df["disease"] == selected_disease_ht]
        male = disease_df[disease_df["gender"].str.lower() == "male"]["recovery time"]
        female = disease_df[disease_df["gender"].str.lower() == "female"]["recovery time"]

        if len(male) > 1 and len(female) > 1:
        # Welch’s T-test (unequal variance)
            t_stat, p_value = ttest_ind(male, female, equal_var=False)

            col1, col2, col3 = st.columns(3)
            col1.metric("Mean (Male)", f"{male.mean():.2f}")
            col2.metric("Mean (Female)", f"{female.mean():.2f}")
            col3.metric("P-Value", f"{p_value:.4f}")

            alpha = 0.05

            st.write(f"**T-Statistic:** {t_stat:.4f}")

            if p_value < alpha:
                st.info(f"Significant difference in recovery time for {selected_disease_ht} (Reject H₀)")
            else:
                st.info(f"No significant difference in recovery time for {selected_disease_ht} (Fail to Reject H₀)")

        #Distribution Plot 
            fig5, ax5 = plt.subplots(figsize=(8, 5))

            x = np.linspace(
            min(disease_df["recovery time"]),
            max(disease_df["recovery time"]),
            500
        )

            male_y = norm.pdf(x, male.mean(), male.std())
            female_y = norm.pdf(x, female.mean(), female.std())

            ax5.plot(x, male_y, label="Male")
            ax5.plot(x, female_y, label="Female")

            ax5.axvline(male.mean(), linestyle="--")
            ax5.axvline(female.mean(), linestyle="--")

            ax5.set_title(
            f"Recovery Time Distribution ({selected_disease_ht})"
        )
            ax5.set_xlabel("Recovery Time")
            ax5.set_ylabel("Density")
            ax5.legend()

            st.pyplot(fig5, use_container_width=True)

        else:
            st.warning("Not enough male/female data for this disease.")
        
        st.divider()
        st.subheader("Expected vs Actual Recovery Time (Disease Specific)")
        RECOVERY_CSV = "C:\\Users\\Atharv\\OneDrive\\Desktop\\Medical_Statistics\\recovery_time.csv"
        try:
            recovery_df = pd.read_csv(RECOVERY_CSV)
        except FileNotFoundError:
            st.warning("recovery_time.csv not found.")
            return

        if recovery_df.empty:
            st.warning("No recovery time data available.")
            return

    # Disease selector
        selected_disease_pair = st.selectbox(
        "Select Disease for Expected vs Actual Test",
        sorted(recovery_df["Disease"].unique())
    )

        pair_df = recovery_df[
        recovery_df["Disease"] == selected_disease_pair
    ]

        if len(pair_df) > 1:
            expected = pair_df["Expected Recovery Time"]
            actual = pair_df["Actual Recovery Time"]

        # Paired T-Test
            from scipy.stats import ttest_rel
            t_stat_pair, p_value_pair = ttest_rel(expected, actual)

            col1, col2, col3 = st.columns(3)
            col1.metric("Mean Expected", f"{expected.mean():.2f}")
            col2.metric("Mean Actual", f"{actual.mean():.2f}")
            col3.metric("P-Value", f"{p_value_pair:.4f}")
            st.write(f"**T-Statistic:** {t_stat_pair:.4f}")
            alpha = 0.05

            if p_value_pair < alpha:
                st.info(f"Significant difference between Expected and Actual recovery time for {selected_disease_pair} (Reject H₀)")
            else:
                st.info(f"No significant difference between Expected and Actual recovery time for {selected_disease_pair} (Fail to Reject H₀)")
        # -------- Bell Curve of Differences --------
            differences = expected - actual
            mean_diff = np.mean(differences)
            std_diff = np.std(differences, ddof=1)
            fig6, ax6 = plt.subplots(figsize=(8, 5))
            x = np.linspace(mean_diff - 4*std_diff,
                        mean_diff + 4*std_diff, 500)
            y = norm.pdf(x, mean_diff, std_diff)
            ax6.plot(x, y)
            ax6.axvline(mean_diff, linestyle="--")
            ax6.set_title(
            f"Bell Curve of Differences ({selected_disease_pair})")
            ax6.set_xlabel("Expected - Actual")
            ax6.set_ylabel("Density")
            st.pyplot(fig6, use_container_width=True)
        else:
            st.warning("Not enough data for paired hypothesis testing.")


  
