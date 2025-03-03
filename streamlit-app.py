import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="No-Brainer Offer Builder", layout="wide")

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'offer_score' not in st.session_state:
    st.session_state.offer_score = 0

# Navigation functions
def next_page():
    # Save form inputs to session state
    for key in st.session_state:
        if key.startswith('form_'):
            response_key = key[5:]  # Remove 'form_' prefix
            st.session_state.responses[response_key] = st.session_state[key]
    
    st.session_state.page += 1

def prev_page():
    st.session_state.page -= 1

# Title and description
st.title("No-Brainer Offer Builder")
st.markdown("### Create an irresistible offer in minutes!")

# Example database
examples = {
    "SaaS": [
        "7-day free trial with no credit card required, then $49/month with 30-day money-back guarantee",
        "Annual plan at 50% discount ($299 instead of $599) with implementation support included",
        "Basic plan free forever, premium features at $19/month with done-for-you setup"
    ],
    "Coaching": [
        "First session free, then $199/month with results guarantee (keep the materials and get refund if not satisfied)",
        "6-week program for $997 with 3 bonus group calls and private community access",
        "Risk-free trial: Pay only if you see results in 30 days"
    ],
    "E-commerce": [
        "Buy one get one free plus free shipping on orders over $50",
        "30-day at-home trial with free return shipping and full refund",
        "Subscribe and save 20% plus exclusive access to new product launches"
    ],
    "Services": [
        "Free audit report + action plan, then $1500 for full implementation with 2X ROI guarantee",
        "Monthly retainer with first month at 50% off and no long-term contract",
        "Pay-for-performance model with minimum fee and success bonuses"
    ]
}

# Hormozi value equation factors
value_factors = {
    "dream_outcome": 0,
    "likelihood": 0,
    "time_delay": 0,
    "effort": 0
}

# Page content
if st.session_state.page == 0:
    # Welcome page
    st.markdown("""
    ## Build Your No-Brainer Offer
    
    Based on frameworks from Jay Abraham, Alex Hormozi, and MJ DeMarco, this tool will help you create an irresistible offer that converts.
    
    **What you'll get:**
    - Step-by-step guidance to build your offer
    - Industry-specific examples
    - Value scoring based on proven frameworks
    - Recommendations to improve your offer
    
    Click Next to begin!
    """)
    
    st.button("Next", on_click=next_page)

elif st.session_state.page == 1:
    # Basic business info
    st.markdown("## Step 1: Your Business Basics")
    
    industry_options = ["SaaS", "Coaching", "E-commerce", "Services", "Other"]
    st.selectbox("What industry are you in?", industry_options, key="form_industry")
    
    st.text_input("What is your primary product or service?", key="form_product")
    
    price_options = ["Under $100", "$100-$500", "$500-$2,000", "$2,000-$10,000", "Over $10,000"]
    st.selectbox("What is your current price point?", price_options, key="form_price")
    
    goal_options = ["Customer Acquisition", "Upselling Existing Customers", "Reactivating Past Customers", "Introducing New Product"]
    st.selectbox("What's the primary goal of this offer?", goal_options, key="form_goal")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Next", on_click=next_page)

elif st.session_state.page == 2:
    # Dream outcome
    st.markdown("## Step 2: Dream Outcome")
    st.markdown("What result or transformation does your customer truly want?")
    
    st.text_area("Describe the exact outcome your ideal customer desires:", key="form_outcome_description")
    
    st.markdown("### Outcome Value")
    st.markdown("How valuable is this outcome to your customer?")
    st.slider("Value Rating", 1, 10, 5, key="form_outcome_value")
    value_factors["dream_outcome"] = st.session_state.get("form_outcome_value", 5)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Previous", on_click=prev_page)
    with col2:
        st.button("Next", on_click=next_page)

elif st.session_state.page == 3:
    # Perceived likelihood
    st.markdown("## Step 3: Perceived Likelihood of Achievement")
    st.markdown("How confident will customers be that your solution will work for them?")
    
    proof_options = [
        "Case Studies/Testimonials", 
        "Data/Statistics", 
        "Before/After Examples", 
        "Process Demonstration",
        "Third-Party Validation",
        "Personal Story"
    ]
    st.multiselect("What proof elements do you have?", proof_options, key="form_proof_elements")
    
    st.text_area("What's your most compelling success story or data point?", key="form_success_story")
    
    st.markdown("### Credibility Score")
    st.markdown("Rate how strong your proof is")
    st.slider("Credibility Rating", 1, 10, 5, key="form_credibility")
    value_factors["likelihood"] = st.session_state.get("form_credibility", 5)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Previous", on_click=prev_page)
    with col2:
        st.button("Next", on_click=next_page)

elif st.session_state.page == 4:
    # Time delay
    st.markdown("## Step 4: Time to Results")
    st.markdown("How quickly can customers expect to see results?")
    
    time_options = ["Immediate", "Days", "Weeks", "Months", "Years"]
    st.selectbox("How long does it typically take to see results?", time_options, key="form_time_to_results")
    
    st.text_area("How can you accelerate results or provide quick wins?", key="form_acceleration")
    
    st.markdown("### Time Factor")
    st.markdown("Rate how quickly your solution delivers results (higher is faster)")
    st.slider("Speed Rating", 1, 10, 5, key="form_speed")
    value_factors["time_delay"] = st.session_state.get("form_speed", 5)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Previous", on_click=prev_page)
    with col2:
        st.button("Next", on_click=next_page)

elif st.session_state.page == 5:
    # Effort & sacrifice
    st.markdown("## Step 5: Effort & Sacrifice")
    st.markdown("What must the customer give up or do to get results?")
    
    st.text_area("What effort is required from the customer?", key="form_effort_required")
    
    st.text_area("How can you reduce this effort?", key="form_effort_reduction")
    
    st.markdown("### Ease Factor")
    st.markdown("Rate how easy it is to use your solution (higher is easier)")
    st.slider("Ease Rating", 1, 10, 5, key="form_ease")
    value_factors["effort"] = st.session_state.get("form_ease", 5)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Previous", on_click=prev_page)
    with col2:
        st.button("Next", on_click=next_page)

elif st.session_state.page == 6:
    # Risk reversal
    st.markdown("## Step 6: Risk Reversal")
    st.markdown("How can you eliminate the risk for your customer?")
    
    guarantee_options = [
        "Money-back guarantee", 
        "Performance guarantee", 
        "Try before you buy", 
        "Pay only if satisfied",
        "Keep resources even if refunded",
        "Extended guarantee period"
    ]
    st.multiselect("What guarantees can you offer?", guarantee_options, key="form_guarantees")
    
    st.text_input("What specific guarantee statement will you make?", key="form_guarantee_statement")
    
    st.markdown("### Risk Reversal Strength")
    st.slider("Risk Reversal Rating", 1, 10, 5, key="form_risk_reversal")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Previous", on_click=prev_page)
    with col2:
        st.button("Next", on_click=next_page)

elif st.session_state.page == 7:
    # Value stack
    st.markdown("## Step 7: Value Stack")
    st.markdown("What additional value can you add to make your offer irresistible?")
    
    st.text_area("Core Offer - What's the main product/service?", key="form_core_offer")
    
    st.text_area("Bonus #1 - What can you add that's valuable but low-cost to you?", key="form_bonus_1")
    
    st.text_area("Bonus #2 - What else can you include?", key="form_bonus_2")
    
    st.text_area("Bonus #3 - Any additional bonuses?", key="form_bonus_3")
    
    st.markdown("### Total Value")
    st.number_input("What's the total value of everything combined? ($)", 0, 1000000, 1000, key="form_total_value")
    
    st.number_input("What price will you charge? ($)", 0, 1000000, 500, key="form_offer_price")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Previous", on_click=prev_page)
    with col2:
        st.button("Next", on_click=next_page)

elif st.session_state.page == 8:
    # Results page
    st.markdown("## Your No-Brainer Offer")
    
    # Calculate value score based on Hormozi's value equation
    dream = value_factors.get("dream_outcome", 5)
    likelihood = value_factors.get("likelihood", 5)
    time_delay = max(1, 11 - value_factors.get("time_delay", 5))  # Invert so lower is better
    effort = max(1, 11 - value_factors.get("effort", 5))  # Invert so lower is better
    
    value_score = (dream * likelihood) / (time_delay * effort) * 10  # Scale up for readability
    
    # Calculate price value ratio
    try:
        total_value = int(st.session_state.responses.get("total_value", 1000))
        offer_price = int(st.session_state.responses.get("offer_price", 500))
        price_ratio = total_value / max(1, offer_price)
    except:
        price_ratio = 2
    
    # Get risk reversal score
    risk_score = int(st.session_state.responses.get("risk_reversal", 5))
    
    # Calculate overall score
    overall_score = (value_score * 0.5) + (price_ratio * 0.3) + (risk_score * 0.2)
    overall_score = min(100, max(0, overall_score))
    st.session_state.offer_score = overall_score
    
    # Display summary
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Your Offer Summary")
        
        st.markdown(f"**Core Offer:** {st.session_state.responses.get('core_offer', '')}")
        
        bonuses = []
        if st.session_state.responses.get('bonus_1'):
            bonuses.append(st.session_state.responses.get('bonus_1'))
        if st.session_state.responses.get('bonus_2'):
            bonuses.append(st.session_state.responses.get('bonus_2'))
        if st.session_state.responses.get('bonus_3'):
            bonuses.append(st.session_state.responses.get('bonus_3'))
        
        if bonuses:
            st.markdown("**Bonuses:**")
            for i, bonus in enumerate(bonuses, 1):
                st.markdown(f"- {bonus}")
        
        guarantee = st.session_state.responses.get('guarantee_statement', '')
        if guarantee:
            st.markdown(f"**Guarantee:** {guarantee}")
        
        value = st.session_state.responses.get('total_value', '')
        price = st.session_state.responses.get('offer_price', '')
        if value and price:
            st.markdown(f"**Value:** ${value}")
            st.markdown(f"**Price:** ${price}")
            st.markdown(f"**Value-to-Price Ratio:** {price_ratio:.1f}x")
    
    with col2:
        st.markdown("### Offer Score")
        
        # Display score gauge
        st.markdown(f"<h1 style='text-align: center;'>{overall_score:.1f}/100</h1>", unsafe_allow_html=True)
        
        # Score interpretation
        if overall_score >= 80:
            st.success("Excellent! You have a strong no-brainer offer.")
        elif overall_score >= 60:
            st.info("Good offer with room for improvement.")
        else:
            st.warning("Your offer needs significant improvement to become a no-brainer.")
    
    # Show examples from the same industry
    st.markdown("### Examples From Your Industry")
    industry = st.session_state.responses.get('industry', 'SaaS')
    if industry in examples:
        for example in examples[industry]:
            st.markdown(f"- {example}")
    
    # Improvement suggestions
    st.markdown("### Suggested Improvements")
    
    if value_score < 6:
        st.markdown("- **Increase Value:** Make your dream outcome more compelling or improve credibility.")
    if price_ratio < 3:
        st.markdown("- **Improve Value-to-Price Ratio:** Add more bonuses or adjust pricing.")
    if risk_score < 7:
        st.markdown("- **Strengthen Risk Reversal:** Offer a more compelling guarantee.")
    if value_factors.get("time_delay", 5) < 7:
        st.markdown("- **Reduce Time to Results:** Find ways to deliver faster results or early wins.")
    if value_factors.get("effort", 5) < 7:
        st.markdown("- **Decrease Required Effort:** Make your solution easier to implement.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Previous", on_click=prev_page)
    with col2:
        if st.button("Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.page = 0
            st.session_state.responses = {}
            st.session_state.offer_score = 0
            st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("No-Brainer Offer Builder - Based on frameworks by Jay Abraham, Alex Hormozi, and MJ DeMarco")
