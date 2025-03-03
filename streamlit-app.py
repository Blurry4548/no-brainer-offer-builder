import streamlit as st
import pandas as pd
import random
import openai
import json
import time
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

st.set_page_config(page_title="No-Brainer Offer Builder", layout="wide")

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'offer_score' not in st.session_state:
    st.session_state.offer_score = 0
if 'ai_suggestions' not in st.session_state:
    st.session_state.ai_suggestions = {}
    
# Securely handle the OpenAI API key using Streamlit secrets
try:
    # Check if we're running in Streamlit Cloud where secrets are available
    from streamlit import secrets
    if "openai" in secrets:
        openai.api_key = secrets["openai"]["api_key"]
        st.session_state.openai_available = True
    else:
        # Fallback to environment variable or sidebar input
        import os
        api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            api_key = st.sidebar.text_input("Enter OpenAI API Key (or set in .streamlit/secrets.toml)", type="password")
        
        if api_key:
            openai.api_key = api_key
            st.session_state.openai_available = True
        else:
            st.sidebar.warning("API key required for AI assistance")
            st.session_state.openai_available = False
except ImportError:
    # Local development fallback
    api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")
    if api_key:
        openai.api_key = api_key
        st.session_state.openai_available = True
    else:
        st.sidebar.warning("Enter API key to enable AI assistance")
        st.session_state.openai_available = False

# AI assistance function
def get_ai_suggestion(context, question, prompt_type):
    """Get AI suggestions based on user input"""
    if not st.session_state.openai_available:
        return "AI assistance unavailable. Please enter your OpenAI API key."
    
    try:
        # Construct prompt based on type of suggestion needed
        if prompt_type == "value_enhancement":
            prompt = f"""
            As an expert in creating no-brainer offers (based on Alex Hormozi, Jay Abraham, and MJ DeMarco's frameworks), 
            provide specific suggestions to enhance this offer:
            
            Industry: {context.get('industry', 'Not specified')}
            Product/Service: {context.get('product', 'Not specified')}
            Current offer: {question}
            
            Give 3 specific, actionable suggestions to make this offer more compelling.
            Focus on: increasing perceived value, reducing risk, decreasing time to results, or minimizing effort required.
            Format as a bulleted list with brief explanations.
            """
        
        elif prompt_type == "dream_outcome":
            prompt = f"""
            As an offer specialist, help craft a more compelling dream outcome for this business:
            
            Industry: {context.get('industry', 'Not specified')}
            Product/Service: {context.get('product', 'Not specified')}
            Current outcome description: {question}
            
            Provide 2-3 suggestions to make this dream outcome more specific, emotionally compelling, and valuable to potential customers.
            """
            
        elif prompt_type == "risk_reversal":
            prompt = f"""
            As a specialist in creating no-brainer offers, suggest a powerful risk-reversal guarantee for:
            
            Industry: {context.get('industry', 'Not specified')}
            Product/Service: {context.get('product', 'Not specified')}
            Price point: {context.get('price', 'Not specified')}
            Current guarantee idea: {question}
            
            Provide 2 specific, innovative guarantee structures that would make this offer truly risk-free for customers.
            Focus on unique approaches that competitors likely aren't using.
            """
            
        elif prompt_type == "bonuses":
            prompt = f"""
            As an expert in value stacking and offer creation, suggest high-perceived-value bonuses for:
            
            Industry: {context.get('industry', 'Not specified')}
            Product/Service: {context.get('product', 'Not specified')}
            Current core offer: {context.get('core_offer', 'Not specified')}
            
            Recommend 3 specific, compelling bonuses that:
            1. Have high perceived value but low delivery cost
            2. Complement the core offer
            3. Address related customer pain points
            
            For each bonus, suggest a specific name, description, and perceived value amount.
            """
            
        elif prompt_type == "offer_analysis":
            prompt = f"""
            Analyze this complete offer based on the principles of no-brainer offers:
            
            Industry: {context.get('industry', 'Not specified')}
            Product/Service: {context.get('product', 'Not specified')}
            Dream outcome: {context.get('outcome_description', 'Not specified')}
            Core offer: {context.get('core_offer', 'Not specified')}
            Bonuses: {context.get('bonus_1', '')}, {context.get('bonus_2', '')}, {context.get('bonus_3', '')}
            Guarantee: {context.get('guarantee_statement', 'Not specified')}
            Price: ${context.get('offer_price', 'Not specified')}
            Stated value: ${context.get('total_value', 'Not specified')}
            
            Provide:
            1. A specific score (1-10) for this offer with brief explanation
            2. The strongest element of this offer
            3. The weakest element of this offer
            4. One specific, actionable improvement that would have the biggest impact
            """
        
        else:
            prompt = f"As an expert in creating no-brainer offers, provide suggestions for: {question}"
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use appropriate model
            messages=[
                {"role": "system", "content": "You are an expert in creating no-brainer offers based on frameworks from Jay Abraham, Alex Hormozi, and MJ DeMarco. Provide specific, actionable advice."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"AI suggestion error: {str(e)}"

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

# Initialize AI suggestion cache
def get_cached_suggestion(context, input_text, prompt_type):
    """Get AI suggestion from cache or generate new one"""
    cache_key = f"{prompt_type}_{input_text}"
    
    if cache_key not in st.session_state.ai_suggestions:
        with st.spinner("Generating AI suggestions..."):
            suggestion = get_ai_suggestion(context, input_text, prompt_type)
            st.session_state.ai_suggestions[cache_key] = suggestion
    
    return st.session_state.ai_suggestions[cache_key]

# Title and description
st.title("No-Brainer Offer Builder")
st.markdown("### Create an irresistible offer in minutes with AI assistance!")

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

# Website scraping function
def scrape_website(url):
    """Scrape text content from a website"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
            
        # Get text content
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up text
        text = re.sub(r'\s+', ' ', text)
        text = text[:8000]  # Limit text length to avoid token limits
        
        return text
    except Exception as e:
        return f"Error: {str(e)}"

# Function to analyze website content
def analyze_website_content(website_text, url):
    """Analyze website content to extract business information and evaluate offer"""
    if not st.session_state.openai_available:
        return {
            "industry": "",
            "product": "",
            "offer_details": "",
            "offer_score": 0,
            "recommendation": "API key required for analysis."
        }
    
    try:
        domain = urlparse(url).netloc
        prompt = f"""
        Analyze this website content from {domain} and extract the following information:
        
        Website text content:
        \"\"\"{website_text}\"\"\"
        
        1. What industry is this business in? Choose from: SaaS, Coaching, E-commerce, Services, or Other.
        2. What is their primary product or service?
        3. What is their current price point? If not explicit, estimate a range.
        4. What offer elements are currently present on their website?
        5. What key value propositions do they mention?
        6. Do they have any clear guarantees, risk reversals, or social proof?
        7. What is their dream outcome for customers?
        
        Then, rate their current offer on a scale of 1-10 based on Hormozi's & Abraham's frameworks.
        
        Format the response as valid JSON with these keys:
        "industry": string (one of the categories),
        "product": string,
        "price_range": string,
        "offer_elements": string,
        "value_propositions": string,
        "guarantees": string, 
        "dream_outcome": string,
        "offer_score": number (1-10),
        "recommendation": string (one key suggestion)
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in analyzing business websites and creating no-brainer offers based on frameworks from Jay Abraham, Alex Hormozi, and MJ DeMarco."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        
        analysis_text = response.choices[0].message.content
        
        # Try to parse the JSON response
        try:
            # Find JSON in the response (in case there's additional text)
            json_pattern = r'\{.*\}'
            json_match = re.search(json_pattern, analysis_text, re.DOTALL)
            
            if json_match:
                analysis_json = json.loads(json_match.group(0))
            else:
                analysis_json = json.loads(analysis_text)
                
            return analysis_json
        except json.JSONDecodeError:
            # If we can't parse JSON, return a simple dict with the raw response
            return {
                "industry": "Other",
                "product": "Could not determine",
                "offer_score": 0,
                "recommendation": "Analysis failed to parse.",
                "raw_response": analysis_text
            }
            
    except Exception as e:
        return {
            "industry": "Other",
            "product": "Error during analysis",
            "offer_score": 0,
            "recommendation": f"Error: {str(e)}"
        }

# Page content
if st.session_state.page == 0:
    # Website analysis page
    st.markdown("""
    ## No-Brainer Offer Builder
    
    Based on frameworks from Jay Abraham, Alex Hormozi, and MJ DeMarco, this tool will help you create an irresistible offer that converts.
    
    ### Start by analyzing your website
    
    Enter your website URL below to automatically analyze your current offer and get a starting score.
    """)
    
    url = st.text_input("Your business website URL", placeholder="https://www.yourbusiness.com")
    
    if st.button("Analyze Website"):
        if url:
            with st.spinner("Analyzing your website..."):
                # Initialize session state for website data if it doesn't exist
                if 'website_data' not in st.session_state:
                    st.session_state.website_data = {}
                
                # Validate URL
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                # Scrape website
                website_text = scrape_website(url)
                
                if website_text.startswith("Error:"):
                    st.error(f"Could not scrape website: {website_text}")
                else:
                    # Analyze content
                    analysis = analyze_website_content(website_text, url)
                    st.session_state.website_data = analysis
                    
                    # Display results
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("### Website Analysis Results")
                        st.markdown(f"**Industry:** {analysis.get('industry', 'Unknown')}")
                        st.markdown(f"**Primary Product/Service:** {analysis.get('product', 'Unknown')}")
                        st.markdown(f"**Price Range:** {analysis.get('price_range', 'Unknown')}")
                        
                        st.markdown("#### Current Offer Elements")
                        st.markdown(f"{analysis.get('offer_elements', 'No clear offer detected')}")
                        
                        st.markdown("#### Value Propositions")
                        st.markdown(f"{analysis.get('value_propositions', 'No clear value propositions detected')}")
                        
                        st.markdown("#### Guarantees & Risk Reversal")
                        st.markdown(f"{analysis.get('guarantees', 'No clear guarantees detected')}")
                        
                        st.markdown("#### Dream Outcome")
                        st.markdown(f"{analysis.get('dream_outcome', 'No clear dream outcome detected')}")
                    
                    with col2:
                        st.markdown("### Offer Score")
                        score = analysis.get('offer_score', 0)
                        st.markdown(f"<h1 style='text-align: center;'>{score}/10</h1>", unsafe_allow_html=True)
                        
                        if score >= 8:
                            st.success("Excellent offer structure!")
                        elif score >= 6:
                            st.info("Good offer with room for improvement.")
                        elif score >= 4:
                            st.warning("Basic offer that needs significant improvement.")
                        else:
                            st.error("Weak offer or no clear offer found.")
                        
                        st.markdown("#### Key Recommendation")
                        st.markdown(f"{analysis.get('recommendation', 'No recommendation available.')}")
                    
                    # Set form values based on analysis
                    if 'industry' in analysis:
                        st.session_state['form_industry'] = analysis['industry']
                    if 'product' in analysis:
                        st.session_state['form_product'] = analysis['product']
                    
                    # Show continue button
                    st.success("Website analyzed! Now let's build your no-brainer offer.")
                    if st.button("Continue to Offer Builder"):
                        next_page()
        else:
            st.warning("Please enter a website URL")
    
    # Option to skip
    st.markdown("---")
    if st.button("Skip website analysis"):
        next_page()
        
elif st.session_state.page == 1:
    # Welcome page
    st.markdown("""
    ## Build Your No-Brainer Offer
    
    Based on frameworks from Jay Abraham, Alex Hormozi, and MJ DeMarco, this tool will help you create an irresistible offer that converts.
    
    **What you'll get:**
    - Step-by-step guidance to build your offer
    - AI-powered suggestions and improvements
    - Industry-specific examples
    - Value scoring based on proven frameworks
    - Recommendations to improve your offer
    
    Click Next to begin!
    """)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Previous", on_click=prev_page)
    with col2:
        st.button("Next", on_click=next_page)

elif st.session_state.page == 2:
    # Basic business info
    st.markdown("## Step 1: Your Business Basics")
    
    industry_options = ["SaaS", "Coaching", "E-commerce", "Services", "Other"]
    st.selectbox("What industry are you in?", industry_options, key="form_industry")
    
    st.text_input("What is your primary product or service?", key="form_product")
    
    price_options = ["Under $100", "$100-$500", "$500-$2,000", "$2,000-$10,000", "Over $10,000"]
    st.selectbox("What is your current price point?", price_options, key="form_price")
    
    goal_options = ["Customer Acquisition", "Upselling Existing Customers", "Reactivating Past Customers", "Introducing New Product"]
    st.selectbox("What's the primary goal of this offer?", goal_options, key="form_goal")
    
    if st.session_state.openai_available and st.session_state.get("form_product") and st.session_state.get("form_industry"):
        # Get AI suggestions
        with st.expander("🤖 AI Suggestions", expanded=True):
            current_context = {
                "industry": st.session_state.get("form_industry", ""),
                "product": st.session_state.get("form_product", ""),
                "price": st.session_state.get("form_price", ""),
                "goal": st.session_state.get("form_goal", "")
            }
            
            if st.button("Get Offer Ideas"):
                suggestion = get_cached_suggestion(
                    current_context,
                    f"Product: {st.session_state.get('form_product', '')}, Goal: {st.session_state.get('form_goal', '')}",
                    "value_enhancement"
                )
                st.markdown(suggestion)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Next", on_click=next_page)

elif st.session_state.page == 3:
    # Dream outcome
    st.markdown("## Step 2: Dream Outcome")
    st.markdown("What result or transformation does your customer truly want?")
    
    current_context = {k[5:]: v for k, v in st.session_state.items() if k.startswith('form_')}
    
    st.text_area("Describe the exact outcome your ideal customer desires:", key="form_outcome_description")
    
    # AI assistance
    if st.session_state.openai_available and st.session_state.get("form_outcome_description"):
        with st.expander("🤖 AI Suggestions for Dream Outcome", expanded=True):
            suggestion = get_cached_suggestion(
                current_context,
                st.session_state.get("form_outcome_description", ""),
                "dream_outcome"
            )
            st.markdown(suggestion)
    
    st.markdown("### Outcome Value")
    st.markdown("How valuable is this outcome to your customer?")
    st.slider("Value Rating", 1, 10, 5, key="form_outcome_value")
    value_factors["dream_outcome"] = st.session_state.get("form_outcome_value", 5)
    
    # Industry examples
    with st.expander("See examples from your industry"):
        industry = st.session_state.get("form_industry", "SaaS")
        if industry in examples:
            for example in examples[industry]:
                st.markdown(f"- {example}")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Previous", on_click=prev_page)
    with col2:
        st.button("Next", on_click=next_page)

elif st.session_state.page == 4:
    # Perceived likelihood
    st.markdown("## Step 3: Perceived Likelihood of Achievement")
    st.markdown("How confident will customers be that your solution will work for them?")
    
    current_context = {k[5:]: v for k, v in st.session_state.items() if k.startswith('form_')}
    
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
    
    # AI assistance
    if st.session_state.openai_available and st.session_state.get("form_success_story"):
        with st.expander("🤖 AI Credibility Enhancement Suggestions", expanded=True):
            proof_elements = st.session_state.get("form_proof_elements", [])
            success_story = st.session_state.get("form_success_story", "")
            
            if st.button("Get Credibility Suggestions"):
                suggestion = get_cached_suggestion(
                    current_context,
                    f"Proof elements: {', '.join(proof_elements)}, Success story: {success_story}",
                    "value_enhancement"
                )
                st.markdown(suggestion)
    
    st.markdown("### Credibility Score")
    st.markdown("Rate how strong your proof is")
    st.slider("Credibility Rating", 1, 10, 5, key="form_credibility")
    value_factors["likelihood"] = st.session_state.get("form_credibility", 5)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Previous", on_click=prev_page)
    with col2:
        st.button("Next", on_click=next_page)

elif st.session_state.page == 5:
    # Time delay
    st.markdown("## Step 4: Time to Results")
    st.markdown("How quickly can customers expect to see results?")
    
    current_context = {k[5:]: v for k, v in st.session_state.items() if k.startswith('form_')}
    
    time_options = ["Immediate", "Days", "Weeks", "Months", "Years"]
    st.selectbox("How long does it typically take to see results?", time_options, key="form_time_to_results")
    
    st.text_area("How can you accelerate results or provide quick wins?", key="form_acceleration")
    
    # AI assistance
    if st.session_state.openai_available:
        with st.expander("🤖 AI Acceleration Suggestions", expanded=True):
            if st.button("Get Acceleration Ideas"):
                suggestion = get_cached_suggestion(
                    current_context,
                    f"Current time to results: {st.session_state.get('form_time_to_results', '')}, Acceleration ideas: {st.session_state.get('form_acceleration', '')}",
                    "value_enhancement"
                )
                st.markdown(suggestion)
    
    st.markdown("### Time Factor")
    st.markdown("Rate how quickly your solution delivers results (higher is faster)")
    st.slider("Speed Rating", 1, 10, 5, key="form_speed")
    value_factors["time_delay"] = st.session_state.get("form_speed", 5)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Previous", on_click=prev_page)
    with col2:
        st.button("Next", on_click=next_page)

elif st.session_state.page == 6:
    # Effort & sacrifice
    st.markdown("## Step 5: Effort & Sacrifice")
    st.markdown("What must the customer give up or do to get results?")
    
    current_context = {k[5:]: v for k, v in st.session_state.items() if k.startswith('form_')}
    
    st.text_area("What effort is required from the customer?", key="form_effort_required")
    
    st.text_area("How can you reduce this effort?", key="form_effort_reduction")
    
    # AI assistance
    if st.session_state.openai_available and st.session_state.get("form_effort_required"):
        with st.expander("🤖 AI Effort Reduction Suggestions", expanded=True):
            if st.button("Get Effort Reduction Ideas"):
                suggestion = get_cached_suggestion(
                    current_context,
                    f"Current effort required: {st.session_state.get('form_effort_required', '')}, Reduction ideas: {st.session_state.get('form_effort_reduction', '')}",
                    "value_enhancement"
                )
                st.markdown(suggestion)
    
    st.markdown("### Ease Factor")
    st.markdown("Rate how easy it is to use your solution (higher is easier)")
    st.slider("Ease Rating", 1, 10, 5, key="form_ease")
    value_factors["effort"] = st.session_state.get("form_ease", 5)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Previous", on_click=prev_page)
    with col2:
        st.button("Next", on_click=next_page)

elif st.session_state.page == 7:
    # Risk reversal
    st.markdown("## Step 6: Risk Reversal")
    st.markdown("How can you eliminate the risk for your customer?")
    
    current_context = {k[5:]: v for k, v in st.session_state.items() if k.startswith('form_')}
    
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
    
    # AI assistance
    if st.session_state.openai_available:
        with st.expander("🤖 AI Guarantee Suggestions", expanded=True):
            guarantees = st.session_state.get("form_guarantees", [])
            guarantee_statement = st.session_state.get("form_guarantee_statement", "")
            
            if st.button("Get Guarantee Ideas"):
                suggestion = get_cached_suggestion(
                    current_context,
                    guarantee_statement,
                    "risk_reversal"
                )
                st.markdown(suggestion)
    
    st.markdown("### Risk Reversal Strength")
    st.slider("Risk Reversal Rating", 1, 10, 5, key="form_risk_reversal")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Previous", on_click=prev_page)
    with col2:
        st.button("Next", on_click=next_page)

elif st.session_state.page == 8:
    # Value stack
    st.markdown("## Step 7: Value Stack")
    st.markdown("What additional value can you add to make your offer irresistible?")
    
    current_context = {k[5:]: v for k, v in st.session_state.items() if k.startswith('form_')}
    
    st.text_area("Core Offer - What's the main product/service?", key="form_core_offer")
    
    # AI assistance for bonuses
    if st.session_state.openai_available and st.session_state.get("form_core_offer"):
        with st.expander("🤖 AI Bonus Suggestions", expanded=True):
            # Update context with core offer
            current_context["core_offer"] = st.session_state.get("form_core_offer", "")
            
            if st.button("Generate Bonus Ideas"):
                suggestion = get_cached_suggestion(
                    current_context,
                    current_context.get("core_offer", ""),
                    "bonuses"
                )
                st.markdown(suggestion)
    
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

elif st.session_state.page == 9:
    # Results page
    st.markdown("## Your No-Brainer Offer")
    
    # Gather all form data into context
    current_context = {k[5:]: v for k, v in st.session_state.items() if k.startswith('form_')}
    st.session_state.responses = current_context
    
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
    
    # AI Analysis
    if st.session_state.openai_available:
        with st.expander("🤖 AI Offer Analysis", expanded=True):
            if st.button("Get Complete Offer Analysis"):
                with st.spinner("Analyzing your offer..."):
                    suggestion = get_cached_suggestion(
                        current_context,
                        "Complete offer analysis",
                        "offer_analysis"
                    )
                    st.markdown(suggestion)
    
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
    
    # Show examples from the same industry
    st.markdown("### Examples From Your Industry")
    industry = st.session_state.responses.get('industry', 'SaaS')
    if industry in examples:
        for example in examples[industry]:
            st.markdown(f"- {example}")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Previous", on_click=prev_page)
    with col2:
        if st.button("Start Over"):
            for key in list(st.session_state.keys()):
                if key not in ['openai_available', 'ai_suggestions']:
                    del st.session_state[key]
            st.session_state.page = 0
            st.session_state.responses = {}
            st.session_state.offer_score = 0
            st.experimental_rerun()
    
    # Export options
    st.markdown("### Export Your Offer")
    if st.button("Download Offer as PDF"):
        st.info("In a production app, this would generate a PDF with your complete offer details and analysis.")

# Footer
st.markdown("---")
st.markdown("No-Brainer Offer Builder - Based on frameworks by Jay Abraham, Alex Hormozi, and MJ DeMarco")
