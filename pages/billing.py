import streamlit as st

def show_billing():
    st.title("💳 Billing")
    df = st.session_state.billing_df

    if df.empty:
        st.info("No billing records")
    else:
        st.dataframe(df, use_container_width=True)
