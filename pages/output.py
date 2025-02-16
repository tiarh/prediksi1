import streamlit as st
import pandas as pd
import requests
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import plotly.graph_objects as go

# Title
st.title("Hasil Prediksi")
st.write("Halaman ini menampilkan hasil prediksi 7 hari ke depan.")

# Check if data is available in session state
if "updated_data" in st.session_state:
    data = st.session_state["updated_data"]
else:
    st.error("⚠️ Data tidak tersedia. Silakan kembali ke halaman input untuk menyimpan data.")
    st.stop()

# Display the data
st.subheader("📊 Data Saat Ini (Termasuk Input Terbaru)")
st.dataframe(data)

# Check if data is sufficient for prediction (90 timesteps)
if len(data) < 90:
    st.warning("⚠️ Data tidak cukup untuk prediksi (dibutuhkan minimal 90 hari).")
else:
    # Prepare input for prediction
    recent_data = data.iloc[-90:][["Price", "t2m", "mean_dewpoint_temperature", "tp", "mean_surface_pressure_hPa"]]

    # Normalisasi data
    scaler = MinMaxScaler()
    normalized_data = scaler.fit_transform(recent_data)  # Normalisasi data 90 hari terakhir

    # Reshape untuk input model
    input_data = normalized_data.reshape(1, 90 * 5)  # Reshape menjadi (1, 450)

    # Load the model
    url = 'https://github.com/tiarh/prediksi-beras/raw/refs/heads/baru/model-skenario3%20(2).h5'
    response = requests.get(url)
    with open('model-skenario3.h5', 'wb') as f:
        f.write(response.content)

    model = load_model('model-skenario3.h5')

    # Predict for the next 7 days
    predicted_normalized = model.predict(input_data).flatten()  # Prediksi (hasil masih dalam skala normalisasi)

    # Denormalisasi hasil prediksi
    predicted = scaler.inverse_transform(
        np.hstack((predicted_normalized.reshape(-1, 1), np.zeros((7, 4))))  # Tambahkan kolom dummy untuk denormalisasi
    )[:, 0]  # Ambil hanya kolom "Price"

    # Debugging: Tampilkan output prediksi
    st.write(f"Predicted values: {predicted}")

    # Generate dates for the next 7 days
    future_dates = pd.date_range(start=pd.to_datetime(data["Date"].iloc[-1]), periods=8, freq="D")[1:]

    # Create DataFrame for predicted data
    predicted_df = pd.DataFrame({
        "Date": future_dates,
        "Price": predicted
    })
    predicted_df["Type"] = "Prediction"  # Tambahkan tipe prediksi

    # Append predicted data to the dataset
    data["Type"] = "Actual"  # Tandai data asli sebagai actual
    combined_data = pd.concat([data, predicted_df], ignore_index=True)

    # Plot the data using Plotly
    st.subheader("📈 Grafik Prediksi (Interaktif)")
    fig = go.Figure()

    # Plot actual data
    actual_data = combined_data[combined_data["Type"] == "Actual"]
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(actual_data["Date"]),
        y=actual_data["Price"],
        mode='lines',
        name='Harga Aktual (HB)',
        line=dict(color='blue')
    ))

    # Plot predicted data
    predicted_data = combined_data[combined_data["Type"] == "Prediction"]
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(predicted_data["Date"]),
        y=predicted_data["Price"],
        mode='lines',
        name='Prediksi Harga (HB)',
        line=dict(color='orange', dash='dash')
    ))

    # Update layout with range slider
    fig.update_layout(
        title="Prediksi Harga 7 Hari ke Depan",
        xaxis_title="Tanggal",
        yaxis_title="Harga (HB)",
        xaxis=dict(rangeslider=dict(visible=True)),  # Aktifkan range slider
        template="plotly_white"
    )

    # Tampilkan grafik interaktif
    st.plotly_chart(fig, use_container_width=True)

    # Display predicted data
    st.subheader("📋 Data Prediksi 7 Hari ke Depan")
    st.dataframe(predicted_df)
