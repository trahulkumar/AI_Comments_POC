import streamlit as st
import plotly.express as px

st.write("Testing deprecation fix")

# Test button with width=True
try:
    st.button("Button with width=True", width=True)
    print("SUCCESS: Button with width=True works")
except Exception as e:
    print(f"FAILURE: Button with width=True failed: {e}")

# Test plotly with width=True
try:
    df = px.data.iris()
    fig = px.scatter(df, x="sepal_width", y="sepal_length")
    st.plotly_chart(fig, width=True)
    print("SUCCESS: Plotly with width=True works")
except Exception as e:
    print(f"FAILURE: Plotly with width=True failed: {e}")
