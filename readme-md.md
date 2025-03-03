# No-Brainer Offer Builder

An AI-powered tool to help you create irresistible offers based on frameworks from Jay Abraham, Alex Hormozi, and MJ DeMarco.

## Features

- Step-by-step guidance to build your offer
- AI-powered suggestions at each step
- Industry-specific examples
- Value scoring based on proven frameworks
- Comprehensive offer analysis

## Quick Setup

### Running Locally

1. Clone this repository
2. Install the requirements:
   ```
   pip install -r requirements.txt
   ```
3. Set up your API key:
   - Create a `.streamlit` folder in the project root
   - Create a `secrets.toml` file inside this folder
   - Add your OpenAI API key:
     ```
     [openai]
     api_key = "your-openai-api-key-here"
     ```
   - Or, set the OPENAI_API_KEY environment variable:
     ```
     export OPENAI_API_KEY="your-openai-api-key-here"
     ```
4. Run the app:
   ```
   streamlit run app.py
   ```

### Deploying to Streamlit Cloud

1. Push your code to GitHub
2. Connect your GitHub repository to Streamlit Cloud
3. Add your OpenAI API key in the Streamlit Cloud secrets management:
   - Go to your app settings
   - Under "Secrets", add the following:
     ```
     [openai]
     api_key = "your-openai-api-key-here"
     ```
4. Deploy your app

## Using the Tool

1. Enter your business information
2. Follow the step-by-step process
3. Get AI-powered suggestions at each step
4. Receive a complete analysis of your offer
5. Review improvement suggestions

## Security Note

This app requires an OpenAI API key to provide AI-powered suggestions. The key is securely handled through Streamlit's secrets management system and is not exposed to users or stored in the code.
