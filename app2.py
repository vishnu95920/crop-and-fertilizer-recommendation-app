import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Streamlit App Setup
st.set_page_config(page_title="Crop & Fertilizer Recommendation", page_icon="🌾", layout="wide")

# CSS Theme
st.markdown("""
    <style>
    /* Main background */
    [data-testid="stAppViewContainer"] > div:first-child {
        background: linear-gradient(to bottom right, #E8F5E9, #F5F6E1) !important;
    }
    .stApp {
        background: linear-gradient(to bottom right, #E8F5E9, #F5F6E1) !important;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #43A047;
        color: #FFFFFF;
        border-right: 2px solid #2E7D32;
    }
    /* Header styling */
    h1 {
        color: #1B5E20;
        font-family: 'Georgia', serif;
        text-shadow: 1px 1px 2px #A5D6A7;
    }
    h2 {
        color: #388E3C;
        font-family: 'Arial', sans-serif;
    }
    /* Input labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #5D4037;
        font-weight: bold;
        font-family: 'Verdana', sans-serif;
    }
    /* Button styling */
    .stButton>button {
        background-color: #66BB6A;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #4CAF50;
        box-shadow: 4px 4px 8px rgba(0, 0, 0, 0.3);
    }
    /* Success/Error message */
    div[data-testid="stMarkdownContainer"] > .stSuccess {
        background-color: #DCEDC8;
        color: #1B5E20;
        border: 2px dashed #81C784;
        border-radius: 8px;
        padding: 10px;
    }
    div[data-testid="stMarkdownContainer"] > .stError {
        background-color: #FFCDD2;
        color: #B71C1C;
        border: 2px dashed #EF5350;
        border-radius: 8px;
        padding: 10px;
    }
    /* Input boxes */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFDE7;
        border: 1px solid #AED581;
        border-radius: 5px;
    }
    /* Ensure content area is transparent */
    [data-testid="stVerticalBlock"] {
        background: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# Session State for Login
if 'users' not in st.session_state:
    st.session_state.users = {"admin": "123"}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Sidebar Navigation
st.sidebar.header("Navigation")
if not st.session_state.logged_in:
    page = st.sidebar.radio("Go to", ["Login", "Sign Up"])
else:
    page = st.sidebar.radio("Go to", ["Home", "Logout"])

# Login Page
if page == "Login" and not st.session_state.logged_in:
    st.title("🌾 Login to Your Account")
    st.markdown("Enter your credentials below to access the recommendation system.", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.success("Login successful! Welcome, {}".format(username))
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password!")
    
    st.markdown("New user? Switch to **Sign Up** from the sidebar.", unsafe_allow_html=True)

# Sign Up Page
elif page == "Sign Up" and not st.session_state.logged_in:
    st.title("🌾 Sign Up for an Account")
    st.markdown("Create a new account to start using the recommendation system.", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Sign Up"):
            if new_username in st.session_state.users:
                st.error("Username already exists! Try a different one.")
            elif new_password != confirm_password:
                st.error("Passwords do not match!")
            elif not new_username or not new_password:
                st.error("Please fill in all fields!")
            else:
                st.session_state.users[new_username] = new_password
                st.success("Sign up successful! Please go to Login page.")
    
    st.markdown("Already have an account? Switch to **Login** from the sidebar.", unsafe_allow_html=True)

# Logout
elif page == "Logout" and st.session_state.logged_in:
    st.session_state.logged_in = False
    st.success("Logged out successfully!")
    st.rerun()

# Main App
elif page == "Home" and st.session_state.logged_in:
    # Load pre-trained models, scalers, and encoders
    try:
        crop_model = joblib.load('crop_recommendation_model.pkl')
        fert_model = joblib.load('fertilizer_recommendation_model.pkl')
        scaler_crop = joblib.load('scaler_crop.pkl')
        scaler_fert = joblib.load('fertilizer_scaler.pkl')
        soil_encoder = joblib.load('soil_encoder.pkl')
        crop_encoder = joblib.load('crop_encoder.pkl')
        label_encoder = joblib.load('label_encoder_fert.pkl')
    except FileNotFoundError as e:
        st.error(f"Error: Missing file {str(e)}. Ensure all .pkl files are in the same directory.")
        st.stop()

    # Crop Recommendation Function
    def recommend_crop(N, P, K, temperature, humidity, ph, rainfall):
        try:
            # Validate inputs (based on Crop_recommendation.csv ranges)
            if not (0 <= N <= 140):
                return f'Error: Nitrogen must be between 0 and 140.'
            if not (5 <= P <= 145):
                return f'Error: Phosphorus must be between 5 and 145.'
            if not (5 <= K <= 205):
                return f'Error: Potassium must be between 5 and 205.'
            if not (8 <= temperature <= 44):
                return f'Error: Temperature must be between 8 and 44 °C.'
            if not (14 <= humidity <= 100):
                return f'Error: Humidity must be between 14 and 100 %.'
            if not (3.5 <= ph <= 10):
                return f'Error: pH must be between 3.5 and 10.'
            if not (20 <= rainfall <= 300):
                return f'Error: Rainfall must be between 20 and 300 mm.'

            # Prepare input
            inputs = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
            inputs_df = pd.DataFrame(inputs, columns=columns)
            
            # Verify scaler feature names
            if not np.array_equal(scaler_crop.feature_names_in_, columns):
                return f"Error: Scaler feature names {scaler_crop.feature_names_in_} do not match input columns {columns}"

            # Scale input
            inputs_scaled = scaler_crop.transform(inputs_df)
            
            # Predict
            prediction = crop_model.predict(inputs_scaled)[0]
            
            # # Debug: Print prediction and model classes
            # st.write(f"Debug: Model prediction = {prediction}")
            # st.write(f"Debug: Model classes = {crop_model.classes_}")

            # Validate prediction
            if prediction not in crop_model.classes_:
                return f"Error: Predicted crop '{prediction}' not in valid classes {crop_model.classes_}"
            
            # Return prediction directly (since model outputs strings)
            return prediction
        except Exception as e:
            return f'Error: {str(e)}'

    # Fertilizer Recommendation Function
    def recommend_fertilizer(Temperature, Humidity, Moisture, Soil_Type, Crop_Type, Nitrogen, Potassium, Phosphorous):
        try:
            # Validate numerical inputs (based on document PAGE3)
            if not (0 <= Temperature <= 42):
                return {'name': 'Error', 'full_name': 'Error', 'npk': 'N/A', 'explanation': 'Temperature must be between 0 and 42.'}
            if not (25 <= Humidity <= 38):
                return {'name': 'Error', 'full_name': 'Error', 'npk': 'N/A', 'explanation': 'Humidity must be between 25 and 38.'}
            if not (50 <= Moisture <= 72):
                return {'name': 'Error', 'full_name': 'Error', 'npk': 'N/A', 'explanation': 'Moisture must be between 50 and 72.'}
            if not (4 <= Nitrogen <= 65):
                return {'name': 'Error', 'full_name': 'Error', 'npk': 'N/A', 'explanation': 'Nitrogen must be between 4 and 65.'}
            if not (0 <= Potassium <= 42):
                return {'name': 'Error', 'full_name': 'Error', 'npk': 'N/A', 'explanation': 'Potassium must be between 0 and 42.'}
            if not (0 <= Phosphorous <= 19):
                return {'name': 'Error', 'full_name': 'Error', 'npk': 'N/A', 'explanation': 'Phosphorous must be between 0 and 19.'}

            # Encode categorical inputs
            if Soil_Type not in soil_encoder.classes_:
                return {'name': 'Error', 'full_name': 'Error', 'npk': 'N/A', 'explanation': f'Invalid Soil Type. Choose from {list(soil_encoder.classes_)}.'}
            if Crop_Type not in crop_encoder.classes_:
                return {'name': 'Error', 'full_name': 'Error', 'npk': 'N/A', 'explanation': f'Invalid Crop Type. Choose from {list(crop_encoder.classes_)}.'}
            
            soil_encoded = soil_encoder.transform([Soil_Type])[0]
            crop_encoded = crop_encoder.transform([Crop_Type])[0]

            # Prepare input array (8 features)
            features = np.array([[Temperature, Humidity, Moisture, soil_encoded, crop_encoded, Nitrogen, Potassium, Phosphorous]])
            columns = ['Temparature', 'Humidity ', 'Moisture', 'Soil Type', 'Crop Type', 'Nitrogen', 'Potassium', 'Phosphorous']
            input_df = pd.DataFrame(features, columns=columns)

            # Scale features
            transformed_features = scaler_fert.transform(input_df)

            # Predict
            prediction = fert_model.predict(transformed_features)[0]
            fertilizer = label_encoder.inverse_transform([prediction])[0]

            # Fertilizer details
            fertilizer_details = {
                'urea': {'full_name': 'Urea (Carbamide)', 'npk': '46-0-0', 'explanation': 'High-nitrogen fertilizer (46% Nitrogen). Used for crops needing nitrogen boost, like Paddy, Wheat, and Cotton. Promotes leaf and stem growth.'},
                'dap': {'full_name': 'Diammonium Phosphate', 'npk': '18-46-0', 'explanation': 'Rich in Phosphorus (46%) and Nitrogen (18%). Ideal for root development and early growth. Suits crops like Sugarcane, Ground Nuts, and Pulses.'},
                '14-35-14': {'full_name': 'NPK 14-35-14', 'npk': '14-35-14', 'explanation': 'Balanced fertilizer with Nitrogen (14%), Phosphorus (35%), and Potassium (14%). Supports flowering and fruiting. Great for Cotton, Sugarcane, and Oil seeds.'},
                '28-28': {'full_name': 'NPK 28-28-0', 'npk': '28-28-0', 'explanation': 'Equal Nitrogen and Phosphorus (28% each), no Potassium. Boosts vegetative growth and root strength. Common for Paddy, Maize, and Ground Nuts.'},
                '17-17-17': {'full_name': 'NPK 17-17-17', 'npk': '17-17-17', 'explanation': 'Fully balanced fertilizer (17% each of N, P, K). Versatile for all growth stages. Used for Sugarcane, Cotton, and Barley.'},
                '20-20': {'full_name': 'NPK 20-20-0', 'npk': '20-20-0', 'explanation': 'Balanced Nitrogen and Phosphorus (20% each). Supports early growth and root development. Ideal for Millets, Pulses, and Oil seeds.'},
                '10-26-26': {'full_name': 'NPK 10-26-26', 'npk': '10-26-26', 'explanation': 'Balanced fertilizer with low Nitrogen (10%), high Phosphorus (26%), and Potassium (26%). Supports flowering and fruiting. Common for Pulses and Barley.'}
            }

            details = fertilizer_details.get(fertilizer, {
                'full_name': fertilizer,
                'npk': 'Unknown',
                'explanation': 'No details available.'
            })

            return {
                'name': fertilizer,
                'full_name': details['full_name'],
                'npk': details['npk'],
                'explanation': details['explanation']
            }
        except Exception as e:
            return {
                'name': 'Error',
                'full_name': 'Error',
                'npk': 'N/A',
                'explanation': f'Error in prediction: {str(e)}'
            }

    # Title and Header
    st.title("🌾 Crop & Fertilizer Recommendation System")
    st.markdown("Get personalized crop and fertilizer recommendations based on your soil and environmental conditions!", unsafe_allow_html=True)

    # Sidebar for Navigation within Main App
    app_mode = st.sidebar.selectbox("Choose Recommendation Type", ["Crop Recommendation", "Fertilizer Recommendation"])

    # Crop Recommendation Section
    if app_mode == "Crop Recommendation":
        st.header("Crop Recommendation")
        st.write("Enter the soil and environmental details below to get the best crop suggestion. **Ensure inputs are within the specified ranges to avoid errors.**")

        col1, col2 = st.columns(2)
        with col1:
            N = st.number_input("Nitrogen (N)", min_value=0.0, max_value=140.0, value=50.0, step=0.1, help="Enter value between 0 and 140 for Nitrogen content in soil.")
            P = st.number_input("Phosphorus (P)", min_value=5.0, max_value=145.0, value=50.0, step=0.1, help="Enter value between 5 and 145 for Phosphorus content in soil.")
            K = st.number_input("Potassium (K)", min_value=5.0, max_value=205.0, value=50.0, step=0.1, help="Enter value between 5 and 205 for Potassium content in soil.")
            temperature = st.number_input("Temperature (°C)", min_value=8.0, max_value=44.0, value=25.0, step=0.1, help="Enter value between 8 and 44 for Temperature in Celsius.")
        with col2:
            humidity = st.number_input("Humidity (%)", min_value=14.0, max_value=100.0, value=50.0, step=0.1, help="Enter value between 14 and 100 for Humidity percentage.")
            ph = st.number_input("pH Value", min_value=3.5, max_value=12.0, value=6.5, step=0.1, help="Enter value between 3.5 and 10 for soil pH.")
            rainfall = st.number_input("Rainfall (mm)", min_value=20.0, max_value=300.0, value=100.0, step=0.1, help="Enter value between 20 and 300 for Rainfall in millimeters.")

        if st.button("Recommend Crop"):
            crop = recommend_crop(N, P, K, temperature, humidity, ph, rainfall)
            if crop.startswith('Error'):
                st.error(crop)
            else:
                st.success(f"The recommended crop is: **{crop.capitalize()}**")

    # Fertilizer Recommendation Section
    elif app_mode == "Fertilizer Recommendation":
        st.header("Fertilizer Recommendation")
        st.write("Enter the details below to get the best fertilizer suggestion. **Ensure inputs are within the specified ranges to avoid errors.**")

        col1, col2 = st.columns(2)
        with col1:
            Temperature = st.number_input("Temperature (°C)", min_value=0.0, max_value=42.0, value=25.0, step=0.1, help="Enter value between 0 and 42 for Temperature in Celsius.")
            Humidity = st.number_input("Humidity (%)", min_value=25.0, max_value=38.0, value=30.0, step=0.1, help="Enter value between 25 and 38 for Humidity percentage.")
            Moisture = st.number_input("Moisture (%)", min_value=50.0, max_value=72.0, value=60.0, step=0.1, help="Enter value between 50 and 72 for Moisture percentage.")
            Soil_Type = st.selectbox("Soil Type", soil_encoder.classes_, help=f"Choose from valid soil types: {', '.join(soil_encoder.classes_)}")
        with col2:
            Crop_Type = st.selectbox("Crop Type", crop_encoder.classes_, help=f"Choose from valid crop types: {', '.join(crop_encoder.classes_)}")
            Nitrogen = st.number_input("Nitrogen", min_value=4.0, max_value=65.0, value=37.0, step=0.1, help="Enter value between 4 and 65 for Nitrogen content in soil.")
            Potassium = st.number_input("Potassium", min_value=0.0, max_value=42.0, value=0.0, step=0.1, help="Enter value between 0 and 42 for Potassium content in soil.")
            Phosphorous = st.number_input("Phosphorus", min_value=0.0, max_value=19.0, value=0.0, step=0.1, help="Enter value between 0 and 19 for Phosphorus content in soil.")

        if st.button("Recommend Fertilizer"):
            result = recommend_fertilizer(Temperature, Humidity, Moisture, Soil_Type, Crop_Type, Nitrogen, Potassium, Phosphorous)
            
            if result['name'] == 'Error':
                st.error(result['explanation'])
            else:
                st.success(f"Recommended Fertilizer: **{result['name'].capitalize()}**")
                st.info(f"**Full Name**: {result['full_name']}")
                st.info(f"**NPK Ratio**: {result['npk']}")
                st.write(f"**Details**: {result['explanation']}")

# Footer
st.markdown("---")
st.markdown(" ", unsafe_allow_html=True)