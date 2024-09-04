import tkinter as tk
from tkinter import messagebox
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
import webbrowser

TURKIYE_TZ = pytz.timezone('Europe/Istanbul')


def get_flight_info(icao24):
    url = f"https://opensky-network.org/api/states/all"
    response = requests.get(url)
    if response.status_code == 200:
        flights = response.json().get('states', [])
        for flight in flights:
            if flight[0] == icao24:
                return {
                    'icao24': flight[0],
                    'callsign': flight[1].strip(),
                    'origin_country': flight[2],
                    'longitude': flight[5],
                    'latitude': flight[6],
                    'altitude': flight[13],
                    'velocity': flight[9],
                    'last_contact': flight[4],
                    'on_ground': flight[8]
                }
    return None


def show_flight_info():
    global flight_info
    icao24 = flight_entry.get().strip().lower()
    if icao24:
        flight_info = get_flight_info(icao24)
        if flight_info:
            route_label.config(text=f"Çağrı Kodu: {flight_info['callsign']}")
            origin_label.config(text=f"Kaynak Ülke: {flight_info['origin_country']}")
            position_label.config(text=f"Konum: ({flight_info['latitude']}, {flight_info['longitude']})")
            altitude_label.config(text=f"Yükseklik: {flight_info['altitude']} metre")
            velocity_label.config(text=f"İvme: {flight_info['velocity']} m/s")

            last_contact_time_utc = datetime.utcfromtimestamp(flight_info['last_contact'])
            last_contact_time = last_contact_time_utc.replace(tzinfo=pytz.utc)
            current_time = datetime.utcnow().replace(tzinfo=pytz.utc)
            flight_duration = current_time - last_contact_time

            if flight_info['on_ground']:
                flight_status_label.config(text="Uçuş Durumu: Yerde")
                landing_time_label.config(text="İniş Saati: Uçakta değil")
            else:
                flight_status_label.config(text="Uçuş Durumu: Havada")
                landing_time_label.config(
                    text=f"Son Veri Zamanı: {last_contact_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
                duration_label.config(text=f"Uçuş Süresi: {str(flight_duration).split('.')[0]}")

                estimated_flight_duration = timedelta(hours=1.5)
                estimated_takeoff_time = last_contact_time - flight_duration
                estimated_landing_time = estimated_takeoff_time + estimated_flight_duration
                estimated_landing_time_tr = estimated_landing_time.astimezone(TURKIYE_TZ)

                estimated_landing_label.config(
                    text=f"Tahmini İniş Saati (TR): {estimated_landing_time_tr.strftime('%Y-%m-%d %H:%M:%S')}")

            plt.figure(figsize=(8, 6))
            world_img = plt.imread(
                "https://upload.wikimedia.org/wikipedia/commons/8/80/World_map_blank_without_borders.png")
            plt.imshow(world_img, extent=[-180, 180, -90, 90])

            if flight_info['longitude'] and flight_info['latitude']:
                plt.plot(flight_info['longitude'], flight_info['latitude'], 'ro', markersize=8)

            plt.title(f"Uçuş: {flight_info['callsign']}")
            plt.xlabel("Boylam")
            plt.ylabel("Enlem")
            plt.show()
        else:
            messagebox.showerror("Hata", "Uçuş bulunamadı.")
    else:
        messagebox.showerror("Hata", "Lütfen bir ICAO24 tanımlayıcısı girin.")


def watch_flight():
    if flight_info:
        callsign = flight_info['callsign']
        if callsign:
            flightradar24_url = f"https://www.flightradar24.com/{callsign.lower()}"
            try:
                webbrowser.open(flightradar24_url)
            except Exception as e:
                print(f"Tarayıcı açma hatası: {e}")
        else:
            messagebox.showerror("Hata", "Çağrı kodu bulunamadı.")
    else:
        messagebox.showerror("Hata", "Önce uçuş bilgilerini aramalısınız.")


root = tk.Tk()
root.title("Uçuş Takip")

tk.Label(root, text="ICAO24 Tanımlayıcısı Girin:").grid(row=0, column=0, padx=10, pady=10)
flight_entry = tk.Entry(root)
flight_entry.grid(row=0, column=1, padx=10, pady=10)

search_button = tk.Button(root, text="Uçuş Ara", command=show_flight_info)
search_button.grid(row=0, column=2, padx=10, pady=10)

watch_button = tk.Button(root, text="Uçuşu İzle", command=watch_flight)
watch_button.grid(row=0, column=3, padx=10, pady=10)

route_label = tk.Label(root, text="")
route_label.grid(row=1, column=0, columnspan=4, padx=10, pady=5)

origin_label = tk.Label(root, text="")
origin_label.grid(row=2, column=0, columnspan=4, padx=10, pady=5)

position_label = tk.Label(root, text="")
position_label.grid(row=3, column=0, columnspan=4, padx=10, pady=5)

altitude_label = tk.Label(root, text="")
altitude_label.grid(row=4, column=0, columnspan=4, padx=10, pady=5)

velocity_label = tk.Label(root, text="")
velocity_label.grid(row=5, column=0, columnspan=4, padx=10, pady=5)

flight_status_label = tk.Label(root, text="")
flight_status_label.grid(row=6, column=0, columnspan=4, padx=10, pady=5)

landing_time_label = tk.Label(root, text="")
landing_time_label.grid(row=7, column=0, columnspan=4, padx=10, pady=5)

duration_label = tk.Label(root, text="")
duration_label.grid(row=8, column=0, columnspan=4, padx=10, pady=5)

estimated_landing_label = tk.Label(root, text="")
estimated_landing_label.grid(row=9, column=0, columnspan=4, padx=10, pady=5)

root.mainloop()
