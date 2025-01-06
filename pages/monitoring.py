import streamlit as st
import json
from datetime import datetime
import plotly.graph_objects as go


import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
from streamlit_utils import show_sidebar_pages
show_sidebar_pages()


# Load API logs and model metrics
def load_logs_and_metrics():
    # Load API logs
    try:
        with open("logs/api_logs.json", "r") as f:
            api_logs = json.load(f)
    except FileNotFoundError:
        api_logs = []

    # Load model metrics
    try:
        with open("models/model_metrics.json", "r") as f:
            model_metrics = json.load(f)
    except FileNotFoundError:
        model_metrics = {}

    return api_logs, model_metrics

# Parse API logs for metrics
def parse_api_logs(api_logs):
    total_calls = len(api_logs)
    if total_calls > 0:
        average_response_time = sum(log["duration"] for log in api_logs) / total_calls
        error_count = sum(1 for log in api_logs if log["status_code"] != 200)
    else:
        average_response_time = 0
        error_count = 0

    return total_calls, average_response_time, error_count

# Display API Logs tab
def display_api_logs_tab(api_logs):
    st.subheader("API Logs")
    total_calls, average_response_time, error_count = parse_api_logs(api_logs)

    st.metric("Total API Calls", total_calls)
    st.metric("Average Response Time (s)", round(average_response_time, 4))
    st.metric("Error Count", error_count)

    if api_logs:
        st.divider()
        with st.expander("View Raw Logs"):
            st.json(api_logs)


# Display Model Quality tab with dynamic and collapsible charts
def display_model_quality_tab(model_metrics):
    st.subheader("Model Quality")

    if model_metrics:
        # Get the latest model and prepare a dropdown
        sorted_models = sorted(
            model_metrics.keys(), 
            key=lambda x: model_metrics[x]["timestamp"], 
            reverse=True
        )
        default_model = sorted_models[0]
        selected_model = st.selectbox(
            "Select a Model to View Metrics:",
            sorted_models,
            index=0  # Default to the latest model
        )
        selected_metrics = model_metrics[selected_model]

        # Convert timestamp to human-readable format
        trained_on = datetime.fromisoformat(selected_metrics["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

        st.write(f"**Selected Model:** {selected_model}")
        st.write(f"**Trained on:** {trained_on}")

        # Display metrics with legend and collapsible charts
        metrics = {
            "RMSE": "Root Mean Squared Error - Measures the average magnitude of prediction errors. (Lower is better).",
            "MAPE": "Mean Absolute Percentage Error - Shows average percentage difference between predicted and true values. (Lower is better)",
            "MAE": "Mean Absolute Error - Measures the average absolute difference between predicted and true values. (Lower is better)"
        }

        for metric, legend in metrics.items():
            value = round(selected_metrics[metric], 2)
            if metric == "MAPE":
                st.metric(metric, f"{value}%", help=legend)
            else:
                st.metric(metric, value, help=legend)
            # Dynamic chart inside a collapsible expander
            with st.expander(f"{metric} History"):
                # Use chronological order for plotting
                chronological_models = sorted(
                    model_metrics.keys(),
                    key=lambda x: model_metrics[x]["timestamp"],
                    reverse=False  # Sort oldest to newest
                )

                metric_history = {
                    model: model_metrics[model][metric]
                    for model in chronological_models
                }
                timestamps = [
                    datetime.fromisoformat(model_metrics[model]["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                    for model in chronological_models
                ]
                values = list(metric_history.values())

                # Standardize x-axis distance by using a simple index
                standardized_x = list(range(len(timestamps)))

                # Plotly line chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=standardized_x, 
                    y=values, 
                    mode="lines+markers", 
                    name=metric,
                    line=dict(shape='linear', color='royalblue'),
                    marker=dict(size=8)
                ))
                fig.update_layout(
                    title=f"{metric} Over Time",
                    xaxis_title="Training Date",
                    yaxis_title=metric,
                    template="seaborn",
                    xaxis_tickangle=45,
                    showlegend=False,
                    margin=dict(l=40, r=40, t=40, b=40),
                    xaxis=dict(tickmode='array', tickvals=standardized_x, ticktext=timestamps)
                )
                st.plotly_chart(fig, use_container_width=True)

        # Optionally show all metrics for debugging or exploration
        st.divider()
        with st.expander("View All Model Metrics"):
            st.json(model_metrics)

    else:
        st.warning("No model metrics found.")



# Main function to render the page
def main():
    st.title("Monitoring Dashboard")
    api_logs, model_metrics = load_logs_and_metrics()

    # Tabs for API logs and model quality
    tab1, tab2 = st.tabs(["API Logs", "Model Quality"])

    with tab1:
        display_api_logs_tab(api_logs)

    with tab2:
        display_model_quality_tab(model_metrics)

if __name__ == "__main__":
    main()
