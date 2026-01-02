import streamlit as st
import time

# Import your two agent brains
from retail_agent import ask_retail_agent
from institutional_agent import ask_institutional_agent

# 1. Page Configuration
st.set_page_config(page_title="Retail vs. Institutional AI", layout="wide")

# 2. Header
st.title("🤖 Dual-Logic Investment Agent")
st.markdown("""
Compare how **Retail Investors** (Alfred Chen Style) and **Institutional Analysts** (HLIB Style) 
answer the same financial question.
""")

# 3. User Input
user_question = st.text_input("Enter your question about the stock:", 
                              placeholder="e.g., Should I buy this stock now?")

# 4. The Magic Button
if st.button("Analyze with Both Agents"):
    if user_question:
        # Create two columns side-by-side
        col1, col2 = st.columns(2)

        # --- Left Column: Retail Agent ---
        with col1:
            st.subheader("🛍️ Retail Agent (Alfred)")
            st.caption("Focus: Principles, Heuristics, Snowball Effect")
            
            with st.spinner("Thinking like a YouTuber..."):
                # Call your actual retail script
                retail_response = ask_retail_agent(user_question)
                
            st.success("Analysis Complete")
            st.write(retail_response)

        # --- Right Column: Institutional Agent ---
        with col2:
            st.subheader("🏛️ Institutional Agent (HLIB)")
            st.caption("Focus: Valuation, Margins, Target Price")
            
            with st.spinner("Analyzing Financial Reports..."):
                # Call your actual institutional script
                inst_response = ask_institutional_agent(user_question)
                
            st.info("Report Generated")
            st.write(inst_response)
    else:
        st.warning("Please enter a question first.")

# 5. Sidebar (Optional Project Info)
with st.sidebar:
    st.header("About This Project")
    st.write("This tool demonstrates how LLMs can be prompted to reason differently based on source material.")
    st.markdown("---")
    st.write("Created by **Darryl Tan**")
    st.write("FYP: Comparative Analysis of Investment Logics")