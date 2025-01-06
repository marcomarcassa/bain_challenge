# Property Valuation API

## Project Overview and Goals:
This project is aimed at developing a property valuation model for a real estate client in Chile, leveraging machine learning techniques to predict residential property prices based on various property features. The model is designed to deliver fast, reliable property valuations and is intended to be deployed quickly into production.

The main objectives of this project include:

- **Model Development**: Build a robust and scalable machine learning pipeline that trains and evaluates a property valuation model using the provided datasets (train.csv and test.csv).
- **API Development**: Create an API capable of receiving property information and generating fast and accurate valuation predictions. The API also includes decurity features, such as API key authentication, Usage rate limit per user and an IP Blacklist, to ensure safe and controlled access.
- **Reproducibility and Scalability**: Ensure that the model training and prediction process is reproducible and scalable, featuring abstractions and a simple database example to facilitate future integration with the client’s databases, allowing for more seamless data management in the long run.
- **Comprehensive Logging**: The project includes a rich logging strategy, enabling the user to audit, monitor, and analyse information about the usage of the model. 
- **Quality of Life Features**: To enhance user experience, the project includes a dashboard for easy exploration of model performance, API testing, and integration with CSV files and databases. The dashboard also demonstrates the reusability and reproducibility of the code, including key functionalities like API key rotation, API monitoring dashboard, demonstrating metrics such as total calls, avarage response time and errors, and model metrics history to monitor perfomance across training rounds.

**The goal** is to deliver a clean, maintainable, and well-documented codebase that can easily scale for future models and projects, with an emphasis on usability, error handling, and integration capabilities.

## Features and Capabilities

- **Prediction Endpoint**: Predicts property prices based on input features.
- **Model Metadata**: Provides metadata about the current model.
- **Model History**: Fetches the history of model metrics.
- **API Key Validation**: Ensures secure access to endpoints.
- **IP Blacklisting**: Blocks requests from blacklisted IPs.
- **Rate Limiting**: Limits the number of requests to the prediction endpoint.
- **Logging**: Logs requests and errors in .log and JSON formats.
- **Dashboard**: All the capabilities and information centralized in an easy to use UI.


## Setup Instructions

### Environment Setup

**Docker setup**:

1. **Docker Build**:

    ```sh
    docker build -t property-valuation-app .
    ```

2. **Docker run**:

    ```sh
    docker run -p 8000:8000 -p 8501:8501 property-valuation-app
    ```

**Setup without Docker**:

1. **Install python dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

2. (alternative) **Create Conda Environment**:
    ```sh
    conda env create -f config/conda_env_bain_challenge.yml
    conda activate bain_challenge
    ```

### Database Setup (simple Postgres database to demonstrate Database integration for production)

1. **Pull Postgres image**
    ```sh
    docker pull marcomarcassa/postgres-db:latest
    ```
2. **Run Postgres Container**:
    ```sh
    docker run --name postgres-db -p 5432:5432 -e POSTGRES_PASSWORD=password -d postgres
    ```

3. **Insert Data**:
    ```sh
    python config/import_data.py
    ```

## Running the Demo

### Running the API

1. **Start the API**:
    ```sh
    uvicorn app_api:app --reload
    ```

### Running the Dashboard

1. **Start Streamlit Dashboard**:
    ```sh
    streamlit run dashboard.py
    ```

## Usage Instructions

### Prediction Endpoint

- **URL**: `/predict`
- **Method**: `POST`
- **Headers**: `Authorization: <API_KEY>`
- **Body**:
    ```json
    {
        "type": "departamento",
        "sector": "vitacura",
        "net_usable_area": 140.0,
        "net_area": 170.0,
        "n_rooms": 4.0,
        "n_bathroom": 4.0,
        "latitude": -33.40123,
        "longitude": -70.58056
    }
    ```

### Model Metadata

- **URL**: `/model_metadata`
- **Method**: `GET`

### Model History

- **URL**: `/model_history`
- **Method**: `GET`

## Additional Information

- **API Key Management**: Use the `regenerate_api_key.py` page to regenerate API keys.
- **Model Retraining**: Use the `retrain_model.py` page to retrain models.
- **Monitoring**: Use the `monitoring.py` page to monitor model performance and API logs.

For more detailed instructions, refer to the individual scripts and notebooks in the project as there may be more functionality than listed in this file.


## Suggestions and Improvements to original code:

- Identified issues with data processing and model training, relying too much on raw input data.
- Focused on improving data validation and implementing best practices, including:
  - Random data splits
  - Handling invalid data and missing target values
- The notebook lacked clarity on environment specifications.
- Compatibility issues between scikit-learn and category_encoders library during initialization.


## Issues and Next Steps

### Next Steps:
- Integrate and/or deploy to a cloud provider, such as AWS or azure.
- Implement role-based access control for the dashboard and endpoints, with an admin profile for retraining and metrics.

### Known Issues:
- When installing the demo via Docker, the two containers (postgres and project) cannot communicate with each other. This issue has not been debugged yet. However, installing it via Conda (as described in the setup instructions) ensures proper functionality.