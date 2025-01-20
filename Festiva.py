import streamlit as st  # type:ignore
from groq import Groq  # type:ignore
import pandas as pd  # type:ignore
import os
from dotenv import load_dotenv  # type:ignore
import sqlite3
import time

# Load environment variables
os.environ["grokapikeyllama"] = "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"

# Initialize Groq client
client = Groq(api_key=os.environ.get("grokapikeyllama"))

# Database setup
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
""")
conn.commit()


# Helper function: Groq API for Festival Budget
def generate_festival_budget(festival, zone, budget, currency):
    with st.spinner("Generating your festival budget..."):
        try:
            st.write(f"Festival={festival}, Budget={budget}, Zone={zone}")

            system_prompt = f"Festival budget planner\nTell me about the {festival} and plan a {festival} in the {zone} celebration with a budget of {currency}{budget}."
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Tell me about the {festival}. I want to celebrate {festival} within a budget of {currency}{budget} in the {zone}. Please provide a breakdown for decorations, gifts, food, etc. Give me some tips and insights"},
                {"role": "assistant", "content": "I will generate a festival budget based on your inputs."}
            ]
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None
            )

            # Debugging: print the entire response to check its structure
            if completion and hasattr(completion, "choices") and completion.choices:
                response_text = completion.choices[0].message.content
                st.session_state["budget_response"] = response_text

          
                # Debugging: Check if the response is valid
                
            
                st.subheader("🎊 Our Suggestions")
                return response_text
            else:
                st.error("Error: No response received from Groq API.")

        except Exception as e:
            st.error(f"An error occurred: {e}")  # More detailed error message

# Helper function: Expense Tracker calculations
def calculate_remaining_budget(total_cash, expenses):
    
    spent = sum(expenses.values())
    remaining = total_cash - spent
    return spent, remaining

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

col1, col2 = st.columns([1,5])  # Create two columns, with a wider second column
with col1:
    drive_link = "https://i.postimg.cc/PrHs97hk/img.png"

# Display the image
    st.image(drive_link, width=100)
    #st.image(r"C:\Users\tejas\Downloads\img.png", width=100)  # Image in the first column,
    unsafe_allow_html=True
with col2:
    st.markdown("<h1 style='font-size: 30px;'> Festiva-Your Festival Planner App</h1>", unsafe_allow_html=True)

# Global Checkbox for YouTube Channel
subscribe_to_youtube = st.checkbox("Subscribe to our YouTube Channel https://www.youtube.com/@learnwithtejashvar9459/", value=False)

# Page Transition Effect using `st.experimental_rerun()`
if not st.session_state["authenticated"]:
    st.title("Welcome to the Festival Planner! 🎉")
    st.write("Plan your festival budgets, track expenses, and get AI-powered insights.")
    auth_mode = st.radio("Choose an option:", ["Login", "Sign Up", "Continue as Guest"])

    if auth_mode == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                st.session_state["authenticated"] = True
                st.success("Logged in successfully!")
                time.sleep(1)
                st.rerun()  # Redirect to main dashboard
            else:
                st.error("Invalid username or password.")
    elif auth_mode == "Sign Up":
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        if st.button("Sign Up"):
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_username, new_password))
                conn.commit()
                st.session_state["authenticated"] = True
                st.success("Account created successfully!")
                time.sleep(1)
                st.rerun()  # Redirect to main dashboard
            except sqlite3.IntegrityError:
                st.error("Username already exists.")
    else:
        st.session_state["authenticated"] = True
        time.sleep(1)
        st.rerun()  # Redirect to main dashboard

# After Login or Guest Access
if st.session_state["authenticated"]:
    st.title("Festival Planner Dashboard")
    st.write("Choose an option below to get started:")

    col1, col2 = st.columns(2)

    with col1:
        st.write("🎉 Festival Budget")
        if st.button("Generate Festival Budget and Insights"):
            st.session_state["page"] = "festival_budget"
            st.rerun()  # Smooth transition to festival budget page
    
    with col2:
        st.write("🚀 Expense analyser")
        if st.button("Expense Analysis and Tracker"):
            st.session_state["page"] = "expense_tracker"
            st.rerun()  # Smooth transition to expense tracker page

    # Festival Budget Page
    if st.session_state.get("page") == "festival_budget":
        festival = st.text_input("Enter the festival name:")
        zone = st.text_input("Enter your zone (City/Location):")
        currency = st.selectbox("Select your currency type:", ["₹ (INR)", "$ (USD)", "€ (EUR)", "£ (GBP)"])
        budget = st.number_input("Enter your budget:", min_value=100)

        if st.button("View and Download Budget Plan"):
            response_text = generate_festival_budget(festival, zone, budget, currency)
            st.write(response_text)
            if response_text:
                st.download_button(
                    label="📥 Download Budget Plan",
                    data=response_text,  # The content of the file to download
                    file_name="festivalbudgetplan.txt",  # Name of the file
                    mime="text/plain"  # MIME type for plain text
                )
            else:
                st.error("Error generating the budget plan. Please try again.")

        # Back Button
        if st.button("Back to Home"):
            st.session_state["page"] = None
            st.rerun()  # Transition back to the homepage
    
    # Expense Tracker Page
    elif st.session_state.get("page") == "expense_tracker":
        if "expenses" not in st.session_state:
            st.session_state.expenses = {}
        total_cash = st.number_input("Enter total cash available:", min_value=0)
        categories = st.multiselect("Select spending categories:", ["Food", "Travel", "Shopping", "Entertainment", "Miscellaneous"])
        expenses = {category: st.number_input(f"Enter expense for {category}:", min_value=0) for category in categories}
        category = st.text_input("Add Expense Category(if necessary)")
        amount = st.number_input("Expense Amount", min_value=0, step=1)
        if st.button("Add Expense"):
            if category and amount > 0:
                st.session_state.expenses[category] = st.session_state.expenses.get(category, 0) + amount
                st.success(f"Added {category}: {amount}")
            else:
                st.error("Please enter valid category and amount.")
        
        expenses.update(st.session_state.expenses)

       
        if st.button("Analyze Expenses"):
            spent, remaining = calculate_remaining_budget(total_cash, expenses)
            st.write(f"### Total Spent: {spent}")
            st.write(f"### Remaining Budget: {remaining}")

        
        # Back Button
        if st.button("Back to Home"):
            st.session_state["page"] = None
            st.rerun()  # Transition back to the homepage

# Footer
st.markdown("""
    <div style="position: fixed; bottom: 0; width: 100%; text-align: center;">
        Follow us: 
        <a href='https://www.instagram.com/tejashvar_k.r/' target='_blank'>Instagram</a> |
        <a href='https://x.com/KRTejashvar8746' target='_blank'>Twitter</a> |
        <a href='https://www.linkedin.com/in/tejashvar-k-r-4319a0262/' target='_blank'>LinkedIn</a>
        <a href= 'https://www.youtube.com/@learnwithtejashvar9459'target='_blank'>Youtube</a>
        <br>Contact us: +91-9597726906
    </div>
""", unsafe_allow_html=True)
