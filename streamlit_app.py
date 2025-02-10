import streamlit as st
import json
import os
import folium
from streamlit_folium import st_folium
import pandas as pd

JSON_FILE = "kullanicilar.json"
DURUM_FILE = "durumlar.json"

if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(DURUM_FILE):
    with open(DURUM_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(JSON_FILE, "r") as f:
        return json.load(f)

def load_durumlar():
    with open(DURUM_FILE, "r") as f:
        return json.load(f)

# 📌 Menü Butonları
st.title("📌 Menü")

col1, col2, col3, col4, col5 = st.columns(5)

if col1.button("Haritayı Göster"):
    st.session_state["sayfa"] = "Haritayı Göster"
if col2.button("Kayıt Ol"):
    st.session_state["sayfa"] = "Kayıt Ol"
if col3.button("Durum Güncelle"):
    st.session_state["sayfa"] = "Durum Güncelle"
if col4.button("Aktif Kullanıcılar"):
    st.session_state["sayfa"] = "Aktif Kullanıcılar"
if col5.button("Kullanıcı Düzenle"):
    st.session_state["sayfa"] = "Kullanıcı Düzenle"

sayfa = st.session_state.get("sayfa", "Haritayı Göster")

# **Haritayı Göster Sayfası**
if sayfa == "Haritayı Göster":
    st.title("📍 Servis Noktaları")
    kullanicilar = load_users()
    m = folium.Map(location=[40.934444429879434, 29.32820863673836], zoom_start=13)

    for k in kullanicilar:
        folium.Marker(
            location=[k["lat"], k["lon"]],
            popup=f"{k['ad']} {k['soyad']}",
            icon=folium.Icon(color="blue")
        ).add_to(m)

    st_folium(m, width=800, height=500)

# **Kayıt Ol Sayfası**
elif sayfa == "Kayıt Ol":
    st.title("📝 Kayıt Ol")
    ad = st.text_input("Adınız")
    soyad = st.text_input("Soyadınız")
    telefon = st.text_input("Telefon Numaranız")
    koordinat = st.text_input("Koordinatlar (Enlem, Boylam)", value="40.934444429879434, 29.32820863673836")

    if st.button("Kaydol"):
        try:
            lat, lon = map(float, koordinat.split(","))
            users = load_users()
            users.append({"ad": ad, "soyad": soyad, "telefon": telefon, "lat": lat, "lon": lon})
            with open(JSON_FILE, "w") as f:
                json.dump(users, f, indent=4)

            durumlar = load_durumlar()
            durumlar[ad] = False  # Varsayılan olarak pasif
            with open(DURUM_FILE, "w") as f:
                json.dump(durumlar, f, indent=4)

            st.success(f"✅ {ad} {soyad}, başarıyla kayıt oldunuz!")
        except ValueError:
            st.error("❌ Hatalı koordinat formatı!")

# **Durum Güncelleme Sayfası**
elif sayfa == "Durum Güncelle":
    st.title("🔴🟢 Kullanıcı Durumu Güncelle")
    kullanicilar = load_users()
    durumlar = load_durumlar()
    
    if not kullanicilar:
        st.warning("Henüz kayıtlı kimse yok.")
    else:
        for k in kullanicilar:
            ad = k["ad"]
            mevcut_durum = durumlar.get(ad, False)
            
            if st.button(f"{ad} - {'🟢 Aktif' if mevcut_durum else '🔴 Pasif'}", key=f"durum_{ad}"):
                durumlar[ad] = not mevcut_durum
                with open(DURUM_FILE, "w") as f:
                    json.dump(durumlar, f, indent=4)
                st.rerun()

# **Aktif Kullanıcıları Listeleme Sayfası**
elif sayfa == "Aktif Kullanıcılar":
    st.title("🟢 Aktif Kullanıcılar")
    kullanicilar = load_users()
    durumlar = load_durumlar()
    aktif_kullanicilar = [k for k in kullanicilar if durumlar.get(k["ad"], False)]
    aktif_kullanicilar = sorted(aktif_kullanicilar, key=lambda k: k['lat'])

    if not aktif_kullanicilar:
        st.warning("Henüz aktif olan kullanıcı yok.")
    else:
        df = pd.DataFrame(aktif_kullanicilar)
        st.write(df)

# **Kullanıcı Düzenleme Sayfası**
elif sayfa == "Kullanıcı Düzenle":
    st.title("📝 Kullanıcı Düzenleme")
    kullanicilar = load_users()
    
    if not kullanicilar:
        st.warning("Henüz kayıtlı kimse yok.")
    else:
        for k in kullanicilar:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{k['ad']} {k['soyad']}** - {k['telefon']}")
            with col2:
                if st.button("Düzenle", key=f"edit_{k['ad']}"):
                    st.session_state["edit_user"] = k
            with col3:
                if st.button("Sil", key=f"delete_{k['ad']}"):
                    kullanicilar = [u for u in kullanicilar if u["ad"] != k["ad"]]
                    with open(JSON_FILE, "w") as f:
                        json.dump(kullanicilar, f, indent=4)
                    st.rerun()
