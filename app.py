from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import folium

app = Flask(__name__)

# Veri dosyası yolu
DATA_FILE = 'data.csv'

# Verileri yükleme
def load_data():
    try:
        data = pd.read_csv(DATA_FILE)
        if data.empty:
            return pd.DataFrame(columns=['Name', 'X', 'Y', 'Radioactivity', 'Pollution', 'pH', 'General Pollution'])
        return data
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=['Name', 'X', 'Y', 'Radioactivity', 'Pollution', 'pH', 'General Pollution'])

# Verileri kaydetme
def save_data(data):
    data.to_csv(DATA_FILE, index=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Form verilerini al
        name = request.form['name']
        x = float(request.form['x'])  # Boylam (Longitude)
        y = float(request.form['y'])  # Enlem (Latitude)
        radioactivity = float(request.form['radioactivity'])
        pollution = float(request.form['pollution'])
        ph = float(request.form['ph'])

        # Genel kirlilik hesapla
        general_pollution = (radioactivity + pollution) / 2

        # Yeni veriyi ekle
        data = load_data()
        new_data = pd.DataFrame([{
            'Name': name,
            'X': x,
            'Y': y,
            'Radioactivity': radioactivity,
            'Pollution': pollution,
            'pH': ph,
            'General Pollution': general_pollution
        }])
        data = pd.concat([data, new_data], ignore_index=True)
        save_data(data)

        return redirect(url_for('map_view'))

    return render_template('index.html')

@app.route('/map')
def map_view():
    data = load_data()

    # Harita oluşturulurken X ve Y koordinatlarını doğru bir şekilde kullanma
    if not data.empty:
        start_lat = data['Y'].mean()  # Enlem (Latitude), yani Y
        start_lon = data['X'].mean()  # Boylam (Longitude), yani X
    else:
        start_lat, start_lon = 0, 0  # Eğer veri yoksa, başlangıç koordinatları 0,0 olarak ayarlanır.

    # Harita oluştur
    map_ = folium.Map(location=[start_lat, start_lon], zoom_start=5)

    # Verileri haritaya ekle
    for _, row in data.iterrows():
        popup_text = f"""
        Name: {row['Name']}<br>
        Radioactivity: {row['Radioactivity']}<br>
        Pollution: {row['Pollution']}<br>
        pH: {row['pH']}<br>
        General Pollution: {row['General Pollution']}
        """
        folium.Marker(
            location=[row['Y'], row['X']],  # Enlem (Y) ve Boylam (X) doğru sırada kullanılmalı
            popup=popup_text,
            icon=folium.Icon(color='red' if row['General Pollution'] > 5 else 'green')
        ).add_to(map_)

    # Haritayı kaydet
    map_.save('static/map.html')
    return render_template('map_view.html')
    
@app.route('/view-data')
def view_data():
    data = load_data()
    return render_template('view_data.html', data=data)

@app.route('/delete/<int:index>', methods=['POST'])
def delete_data(index):
    data = load_data()

    # İlgili satırı sil
    data = data.drop(index)
    save_data(data)

    return redirect(url_for('view_data'))

if __name__ == '__main__':
    app.run(debug=True)
