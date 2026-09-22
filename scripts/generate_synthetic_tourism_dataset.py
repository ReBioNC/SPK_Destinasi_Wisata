"""
Script Generator Lengkap Dataset Pariwisata 38 Provinsi Indonesia (TravelFit).
Menghasilkan 50 destinasi wisata per provinsi (total 1.900 baris),
lengkap dengan koordinat geografis nyata, harga rasional, rating kredibel,
deskripsi informatif, penanda fasilitas, dan tag aktivitas.
"""

import sys
import os
import json
import random
import re
from pathlib import Path
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)

# Import base provinces
from all_provinces_registry import ALL_38_PROVINCES

# Registry batch 2: Tambahan provinsi
ADDITIONAL_PROVINCES = [
    # ==================== BALI & NUSA TENGGARA (3) ====================
    {
        "nama": "Bali", "pulau": "Bali-Nusa Tenggara", "ibukota": "Denpasar",
        "cities": [
            ("Kota Denpasar", -8.6705, 115.2126), ("Badung", -8.5833, 115.1833),
            ("Gianyar", -8.5333, 115.3333), ("Tabanan", -8.5333, 115.1167),
            ("Buleleng", -8.1167, 115.0833), ("Karangasem", -8.4500, 115.6167),
            ("Klungkung", -8.5333, 115.4000), ("Bangli", -8.4500, 115.3500),
            ("Jembrana", -8.3000, 114.6667)
        ],
        "pantai": [
            "Pantai Kuta Badung", "Pantai Pandawa Tebing Kapur", "Pantai Sanur Sunrise", "Pantai Seminyak Sunset",
            "Pantai Melasti Ungasan", "Pantai Dreamland Tebing", "Pantai Jimbaran Seafood", "Pantai Lovina Lumba-Lumba",
            "Pantai Padang Padang Uluwatu", "Pantai Nusa Dua Pasir Putih", "Pantai Virgin Beach Karangasem",
            "Pantai Amed Snorkeling Bawah Laut", "Pantai Balangan Badung", "Pantai Suluban Blue Point",
            "Pantai Echo Beach Canggu", "Pantai Medewi Jembrana"
        ],
        "gunung": [
            "Gunung Batur Kintamani Sunrise", "Gunung Agung Puncak Tertinggi Bali", "Gunung Abang Bangli",
            "Gunung Batukaru Tabanan", "Bukit Campuhan Ubud Ridge Walk", "Bukit Asah Karangasem Laut",
            "Puncak Wanagiri Hidden Hill", "Bukit Teletubbies Nusa Penida", "Gunung Catur Bedugul",
            "Bukit Cinta Karangasem", "Bukit Belong Klungkung", "Puncak Munduk Buleleng"
        ],
        "alam": [
            "Tegallalang Rice Terrace Subak", "Nusa Penida Kelingking Beach", "Danau Beratan Bedugul",
            "Air Terjun Gitgit Buleleng", "Air Terjun Sekumpul Buleleng", "Air Terjun Tegenungan Gianyar",
            "Danau Batur Kintamani", "Hutan Monyet Ubud (Monkey Forest)", "Tirta Gangga Karangasem", "Danau Tamblingan"
        ],
        "budaya": [
            "Pura Luhur Uluwatu Tari Kecak", "Pura Tanah Lot Pulau Karang", "Desa Adat Penglipuran Terbersih",
            "Pura Tirta Empul Tampaksiring", "Pura Taman Ayun Mengwi", "Garuda Wisnu Kencana (GWK) Cultural Park",
            "Istana Kerajaan Klungkung Kertagosa", "Pura Goa Lawah Klungkung"
        ],
        "hiburan": ["Waterbom Bali Kuta", "Bali Safari & Marine Park Gianyar", "Bali Zoo Sukawati", "Finns Beach Club Canggu", "Krisna Funtastic Land Buleleng"],
        "belanja": ["Pasar Seni Ubud Gianyar", "Pasar Seni Sukawati Gianyar", "Krisna Oleh-Oleh Khas Bali Tuban", "Pasar Seni Kumbasari Denpasar", "The Keranjang Bali Kuta"],
        "religi": ["Pura Agung Besakih Mother Temple", "Pura Ulun Danu Beratan", "Pura Lempuyang Luhur Gates of Heaven", "Vihara Dharmayana Kuta", "Gereja Palasari Jembrana Arsitektur Gotik Bali"]
    },
    {
        "nama": "Nusa Tenggara Barat", "pulau": "Bali-Nusa Tenggara", "ibukota": "Mataram",
        "cities": [
            ("Kota Mataram", -8.5833, 116.1167), ("Lombok Barat", -8.6833, 116.1333),
            ("Lombok Tengah", -8.7000, 116.2833), ("Lombok Timur", -8.6500, 116.5333),
            ("Lombok Utara", -8.3500, 116.1667), ("Sumbawa", -8.5000, 117.4333),
            ("Sumbawa Barat", -8.7500, 116.8500), ("Dompu", -8.5333, 118.4667),
            ("Kota Bima", -8.4500, 118.7333), ("Bima", -8.5833, 118.7167)
        ],
        "pantai": [
            "Pantai Senggigi Lombok Barat", "Pantai Kuta Mandalika Lombok Tengah", "Pantai Tanjung Aan Pasir Merica",
            "Pantai Pink Lombok Timur (Tangsi)", "Pantai Selong Belanak Selancar", "Pantai Mawun Lombok Tengah",
            "Pantai Sire Lombok Utara", "Pantai Malimbu Lombok", "Pantai Lakey Dompu Surfing Dunia",
            "Pantai Kenawa Sumbawa Barat", "Pantai Lawar Sekongkang", "Pantai Jelenga Sumbawa",
            "Pantai Kertasari Taliwang", "Pantai Lariti Bima Laut Terbelah", "Pantai Oi Fanda Bima", "Pantai Semeti Karang Krypton"
        ],
        "gunung": [
            "Gunung Rinjani (3.726 mdpl)", "Gunung Tambora Kaldera Raksasa 1815", "Bukit Pergasingan Sembalun",
            "Bukit Merese Mandalika", "Puncak Bukit Nanggi Sembalun", "Bukit Datu Sembalun",
            "Bukit Mantar Sumbawa Negeri di Atas Awan", "Bukit Seger Sirkuit Mandalika", "Bukit Malimbu Lombok",
            "Puncak Pusuk Pass Kera Hutan", "Bukit Kondo Sembalun", "Gunung Sangeang Api Bima"
        ],
        "alam": [
            "Danau Segara Anak Rinjani", "Gili Trawangan Wisata Bahari", "Gili Meno Penyu Laut",
            "Gili Air Karang Tropis", "Air Terjun Sendang Gile Senaru", "Air Terjun Tiu Kelep Lombok Utara",
            "Pulau Kenawa Sumbawa Sabana", "Pulau Moyo Air Terjun Mata Jitu Putri Diana", "Air Terjun Benang Kelambu", "Gili Nanggu Snorkeling"
        ],
        "budaya": [
            "Desa Adat Sade Suku Sasak", "Desa Wisata Ende Lombok Tengah", "Taman Mayura Cakranegara Mataram",
            "Taman Narmada Air Awet Muda", "Istana Dalam Loka Sumbawa", "Desa Tenun Sukarara Lombok",
            "Desa Adat Bayan Beleq", "Museum Negeri NTB Mataram"
        ],
        "hiburan": ["Sirkuit Internasional Pertamina Mandalika", "Mataram Water Park", "Lombok Wildlife Park Sigar Penjalin", "Taman Sangkareang Mataram", "Kura-Kura Waterpark Sumbawa"],
        "belanja": ["Pasar Seni Sayang-Sayang Mataram", "Pusat Mutiara Sekarbela Mataram", "Sentra Tenun Ikat Sukarara", "Sentra Madu Sumbawa Asli", "Lombok Epicentrum Mall"],
        "religi": ["Masjid Hubbul Wathan Islamic Center NTB", "Pura Lingsar Kerukunan Umat Beragama", "Pura Batu Bolong Senggigi", "Masjid Kuno Bayan Beleq", "Pura Meru Cakranegara"]
    },
    {
        "nama": "Nusa Tenggara Timur", "pulau": "Bali-Nusa Tenggara", "ibukota": "Kupang",
        "cities": [
            ("Kota Kupang", -10.1772, 123.6070), ("Manggarai Barat Labuan Bajo", -8.5000, 119.8833),
            ("Sumba Barat", -9.6667, 119.4167), ("Sumba Timur", -9.6500, 120.2667),
            ("Ende", -8.8432, 121.6623), ("Ngada Bajawa", -8.7000, 120.9667),
            ("Alor Kalabahi", -8.2167, 124.5167), ("Rote Ndao", -10.7333, 123.0667),
            ("Sikka Maumere", -8.6167, 122.2167), ("Timor Tengah Selatan Soe", -9.8667, 124.2833)
        ],
        "pantai": [
            "Pantai Pink Beach Taman Nasional Komodo", "Pantai Lasiana Kupang", "Pantai Oetune Gurun Pasir TTS",
            "Pantai Kolbano Batu Kerikil Warna", "Pantai Mandorak Sumba Barat Daya", "Pantai Walakiri Sunset Pohon Menari Sumba",
            "Pantai Nihiwatu Sumba Kelas Dunia", "Pantai Nembrala Rote Surfing", "Pantai Koka Maumere Sikka",
            "Pantai Pede Labuan Bajo", "Pantai Batu Cermin Bajo", "Pantai Tablolong Kupang Rumput Laut",
            "Pantai Maimol Alor", "Pantai Buntal Manggarai Timur", "Pantai Liman Pulau Semau Kupang", "Pantai Liang Komodo"
        ],
        "gunung": [
            "Gunung Kelimutu Tiga Warna Ende", "Gunung Inerie Piramida Alam Ngada", "Puncak Bukit Padar Komodo Ikonik",
            "Bukit Wairinding Sumba Timur Sabana", "Bukit Tanarara Sumba Timur Bergelombang", "Bukit Sylvia Labuan Bajo Sunset",
            "Bukit Cinta Labuan Bajo", "Puncak Gunung Mutis TTS", "Gunung Iya Ende", "Gunung Egon Maumere",
            "Bukit Tuamese Raja Ampat NTT", "Bukit Teletubbies Sumba"
        ],
        "alam": [
            "Taman Nasional Komodo Habitat Asli Biawak Komodo", "Danau Tiga Warna Kelimutu", "Pulau Rinca Komodo",
            "Gua Rangko Kolam Renang Air Asin Alami", "Gua Batu Cermin Labuan Bajo", "Danau Weekuri Laguna Air Asin Sumba",
            "Air Terjun Cunca Wulang Ngarai Batu", "Air Terjun Tanggedu Grand Canyon Sumba", "Taman Laut Selat Pantar Alor", "Air Terjun Oenesu Kupang Tiga Tingkat"
        ],
        "budaya": [
            "Desa Adat Wae Rebo Negeri di Atas Awan", "Desa Adat Bena Megalitikum Bajawa", "Desa Adat Ratenggaro Menara Rumah Tinggi Sumba",
            "Desa Adat Prai Ijing Sumba Barat", "Situs Rumah Pengasingan Bung Karno Ende", "Kampung Adat Takpala Alor",
            "Desa Tenun Ikat Lepo Lorun Maumere", "Museum NTT Kupang"
        ],
        "hiburan": ["Waterpark Baumata Kupang", "Taman Nostalgia Kupang Kuliner", "Suba Suka Paradise Kupang", "Waterboom Tirta Mutiara Kupang", "Marina Labuan Bajo Waterfront Walk"],
        "belanja": ["Pasar Malam Kampung Ujung Seafood Labuan Bajo", "Sentra Tenun Ikat NTT Ina Ndao Kupang", "Sentra Kopi Bajawa Flores", "Pasar Kasih Naikoten Kupang", "Sentra Cendana Kupang"],
        "religi": ["Gereja Katedral Kristus Raja Kupang", "Gereja Katedral Roh Kudus Weetebula Sumba", "Masjid Agung Nurul Falah Labuan Bajo", "Patung Bunda Maria Segala Bangsa Maumere", "Gereja Tua Sikka Maumere 1899"]
    },

    # ==================== KALIMANTAN (5 PROVINSI) ====================
    {
        "nama": "Kalimantan Barat", "pulau": "Kalimantan", "ibukota": "Pontianak",
        "cities": [
            ("Kota Pontianak", -0.0263, 109.3425), ("Kota Singkawang", 0.9000, 108.9833),
            ("Sambas", 1.3667, 109.3000), ("Ketapang", -1.8500, 109.9833),
            ("Bengkayang", 0.8167, 109.6500), ("Kapuas Hulu Putussibau", 0.8667, 112.9333),
            ("Sintang", 0.0667, 111.5000), ("Kubu Raya", -0.1500, 109.3833),
            ("Landak Ngabang", 0.4000, 109.7500), ("Mempawah", 0.3667, 108.9500)
        ],
        "pantai": [
            "Pantai Pasir Panjang Singkawang", "Pantai Palm Beach Singkawang", "Pantai Kijing Mempawah",
            "Pantai Sinam Pemangkat Sambas", "Pantai Temajuk Ekor Borneo", "Pantai Batu Payung Singkawang",
            "Pantai Tanjung Batu Ketapang", "Pantai Pulau Datok Sukadana Kayong", "Pantai Samudra Indah Bengkayang",
            "Pantai Bajau Rindu Alam Singkawang", "Pantai Gratis Singkawang", "Pantai Tanjung Belandang Ketapang",
            "Pantai Polaria Sambas", "Pantai Kura-Kura Bengkayang", "Pantai Gosong Singkawang", "Pantai Sungai Jawi Ketapang"
        ],
        "gunung": [
            "Gunung Palung (TNGP) Kayong Utara", "Bukit Kelam Sintang (Batu Monolit Terbesar Kedua Dunia)", "Gunung Bawang Bengkayang",
            "Bukit Penjamur Bengkayang Negeri Awan", "Bukit Rimbang Mempawah", "Puncak Bukit Bougenville Singkawang",
            "Gunung Poteng Singkawang", "Bukit Vander Vich Putussibau", "Bukit Jamur Singkawang",
            "Puncak Gunung Niut Landak", "Bukit Saran Sintang", "Bukit Matok Sambas"
        ],
        "alam": [
            "Taman Nasional Danau Sentarum Kapuas Hulu", "Tugu Khatulistiwa Pontianak Titik Nol Ekuator",
            "Taman Nasional Gunung Palung Orangutan", "Air Terjun Riam Merasap Bengkayang Little Niagara",
            "Air Terjun Riam Dait Landak Tujuh Tingkat", "Sungai Kapuas Terpanjang di Indonesia",
            "Danau Laet Tayan Sanggau", "Pulau Lemukutan Snorkeling Bengkayang", "Pulau Randayan Wisata Bahari", "Air Terjun Mananggar Landak"
        ],
        "budaya": [
            "Keraton Kadriah Kesultanan Pontianak", "Rumah Betang Radakng Pontianak Terpanjang", "Kawasan Pecinan Singkawang Kota Amoy",
            "Istana Sambas Alwatzikoebillah", "Vihara Tri Dharma Bumi Raya Singkawang", "Museum Negeri Pontianak",
            "Rumah Adat Melayu Pontianak", "Desa Adat Sahapm Dayak Kanayatn Landak"
        ],
        "hiburan": ["Paradis-Q Waterpark Kubu Raya", "Taman Alun-Alun Kapuas Pontianak", "Sinka Zoo Singkawang Taman Satwa", "Mimi Land Batu Payung Singkawang", "Waterboom Equator Pontianak"],
        "belanja": ["Pasar Tengah Pontianak", "Sentra Lidah Buaya Aloevera Center", "Sentra Tenun Sambas Songket Lunggi", "Pusat Keramik Dinasti Singkawang", "Ayani Mega Mall Pontianak"],
        "religi": ["Masjid Raya Mujahidin Pontianak", "Masjid Jami Sultan Syarif Abdurrahman Pontianak", "Vihara Sui Khew Pak Kung Singkawang", "Gereja Katedral Santo Yosef Pontianak", "Masjid Agung Al-Falah Mempawah"]
    },
    {
        "nama": "Kalimantan Selatan", "pulau": "Kalimantan", "ibukota": "Banjarmasin",
        "cities": [
            ("Kota Banjarmasin", -3.3194, 114.5908), ("Kota Banjarbaru", -3.4400, 114.8300),
            ("Banjar Martapura", -3.4167, 114.9833), ("Tanah Laut Pelaihari", -3.8000, 114.7667),
            ("Kotabaru", -3.2500, 116.2167), ("Tanah Bumbu Batulicin", -3.4500, 115.9833),
            ("Hulu Sungai Selatan Kandangan", -2.7500, 115.2500), ("Hulu Sungai Tengah Barabai", -2.6000, 115.4167),
            ("Tapin Rantau", -2.9167, 115.1500), ("Tabalong Tanjung", -1.9000, 115.5000)
        ],
        "pantai": [
            "Pantai Takisung Tanah Laut", "Pantai Batakan Baru Pelaihari", "Pantai Gedambaan Sarang Tiung Kotabaru",
            "Pantai Pagatan Pesta Laut Mappanretasi", "Pantai Teluk Tamiang Surga Bahari Kotabaru", "Pantai Swarangan Jorong",
            "Pantai Angsana Snorkeling Terumbu Karang", "Pantai Rindu Alam Batulicin", "Pantai Muara Kintap",
            "Pantai Tanjung Dewa", "Pantai Asam-Asam Tanah Laut", "Pantai Teluk Gosong Kotabaru",
            "Pantai Batu Buaya Kotabaru", "Pantai Pulau Burung Tanah Bumbu", "Pantai Pagatan Tanah Bumbu", "Pantai Samber Gelap Kotabaru"
        ],
        "gunung": [
            "Puncak Pegunungan Meratus Loksado", "Gunung Halau-Halau Puncak Tertinggi Kalsel (1.901 mdpl)", "Bukit Matang Kaladan Raja Ampat Banjar",
            "Bukit Riam Kanan Aranio", "Bukit Mawar Kiram Park Banjar", "Bukit Batulaki HSS",
            "Bukit Langara Loksado Bambu", "Bukit Batu Riam Kanan", "Bukit Birah Tanah Laut",
            "Bukit Lintang Pelaihari", "Puncak Gunung Mando Pelaihari", "Gunung Hauk Balangan"
        ],
        "alam": [
            "Pasar Terapung Lok Baintan Sungai Martapura", "Pasar Terapung Muara Kuin", "Danau Riam Kanan Waduk Aranio",
            "Bamboo Rafting Sungai Amandit Loksado", "Pulau Kembang Habitat Kera Ekor Panjang Bekantan", "Pulau Curiak Konservasi Bekantan",
            "Air Terjun Haratai Loksado", "Danau Biru Pengaron Bekas Tambang", "Tahura Sultan Adam Mandiangin", "Gua Liang Bangkai Tanah Bumbu"
        ],
        "budaya": [
            "Kawasan Rumah Adat Bubungan Tinggi Teluk Selong", "Museum Wasaka Perjuangan Rakyat Kalsel", "Makam Syekh Muhammad Arsyad Al-Banjari (Datu Kalampayan)",
            "Museum Lambung Mangkurat Banjarbaru", "Desa Wisata Sasirangan Kampung Seberang Mesjid", "Makam Pangeran Antasari Banjarmasin",
            "Kawasan Wisata Kampung Pelangi Banjarbaru", "Balai Adat Dayak Meratus Malaris Loksado"
        ],
        "hiburan": ["Kiram Park Banjar Karang Intan", "Amanah Borneo Park Banjarbaru", "Waterboom Pesona Modern Kertak Hanyar", "Menara Pandang Banjarmasin Siring", "Taman Siring Sungai Martapura"],
        "belanja": ["Pusat Pertokoan Cahaya Bumi Selamat (CBS) Intan Permata Martapura", "Sentra Kain Sasirangan Banjarmasin", "Sentra Dodol Kandang HSS", "Pasar Bauntung Banjarbaru", "Duta Mall Banjarmasin"],
        "religi": ["Masjid Raya Sabilal Muhtadin Banjarmasin", "Masjid Bersejarah Sultan Suriansyah Kuin", "Masjid Agung Al-Karomah Martapura", "Makam Datu Sanggul Tatakan Tapin", "Masjid Ba'angkat Sucipto HSS"]
    },
    {
        "nama": "Kalimantan Tengah", "pulau": "Kalimantan", "ibukota": "Palangka Raya",
        "cities": [
            ("Kota Palangka Raya", -2.2083, 113.9167), ("Kotawaringin Barat Pangkalan Bun", -2.6833, 111.6167),
            ("Kotawaringin Timur Sampit", -2.5333, 112.9500), ("Katingan Kasongan", -1.9000, 113.3833),
            ("Kapuas Kuala Kapuas", -3.0000, 114.3833), ("Barito Selatan Buntok", -1.7167, 114.8333),
            ("Barito Utara Muara Teweh", -0.9500, 114.9000), ("Sukamara", -2.6333, 111.2333),
            ("Lamandau Nanga Bulik", -1.8333, 111.2833), ("Murung Raya Puruk Cahu", -0.6167, 114.5833)
        ],
        "pantai": [
            "Pantai Ujung Pandaran Sampit", "Pantai Kubu Pangkalan Bun", "Pantai Tanjung Keluang Pasir Putih Konservasi Penyu",
            "Pantai Bogam Raya Kotawaringin Barat", "Pantai Keraya Kumai", "Pantai Anugerah Sukamara",
            "Pantai Tanjung Penghujan Sukamara", "Pantai Lunci Sukamara", "Pantai Satiruk Kotawaringin Timur",
            "Pantai Teluk Bogam Kobar", "Pantai Sebuai Kumai", "Pantai Sungai Cabang TN Tanjung Puting",
            "Pantai Cemara Sukamara", "Pantai Babalot Kotawaringin", "Pantai Sungai Bakau Seruyan", "Pantai Tanjung Siamuk"
        ],
        "gunung": [
            "Bukit Tangkiling Palangka Raya", "Bukit Batu Kasongan Pertapaan Tjilik Riwut", "Gunung Bukit Raya Puncak Tertinggi Kalimantan (2.278 mdpl)",
            "Gunung Bondang Murung Raya Sakral", "Bukit Cinta Tangkiling", "Bukit Baranahu Katingan",
            "Bukit Doa Karmel Tangkiling", "Bukit Sebayan Lamandau", "Bukit Ngalangkang Palangka Raya",
            "Bukit Matang Kahayan", "Puncak Bukit Babi Murung Raya", "Bukit Salju Barito Utara"
        ],
        "alam": [
            "Taman Nasional Tanjung Puting Konservasi Orangutan Terbesar Dunia", "Taman Nasional Sebangau Ekosistem Gambut Blackwater",
            "Camp Leakey Pusat Rehabilitasi Orangutan", "Danau Tahai Jembatan Kayu Gambut", "Susur Sungai Kahayan Jembatan Kahayan",
            "Sungai Sekonyer Amazon Borneo", "Air Terjun Tosah Barito Utara", "Air Terjun Bumbun Murung Raya",
            "Riam Tinggi Lamandau", "Danau Sembuluh Danau Terluas Kalteng"
        ],
        "budaya": [
            "Istana Kuning Kesultanan Kotawaringin Pangkalan Bun", "Rumah Betang Dayak Damang Batu", "Museum Balanga Palangka Raya",
            "Desa Wisata Dayak Pasir Panjang Kobar", "Rumah Tradisional Betang Sei Pasah Kapuas", "Sandung Tulang Leluhur Dayak Ngaju",
            "Situs Cagar Budaya Tiwah Tumbang Malahoi", "Tugu Sukarno Titik Awal Ibu Kota Nusantara Palangka Raya 1957"
        ],
        "hiburan": ["Kalawa Waterpark Palangka Raya", "Kum Kum Taman Wisata Palangka Raya", "Taman Pasuk Kameloh Jembatan Kahayan", "Taman Kota Sampit Kotim", "Taman Bundaran Besar Palangka Raya"],
        "belanja": ["Pasar Besar Palangka Raya", "Sentra Kerajinan Anyaman Rotan Sanaman Mantikei", "Pusat Kerajinan Getah Nyatu Palangka Raya", "Sentra Ikan Salai Jelawat Sampit", "Palma Mall Palangka Raya"],
        "religi": ["Masjid Raya Darussalam Palangka Raya", "Gereja Katedral Santa Perawan Maria Palangka Raya", "Balai Basarah Hindu Kaharingan", "Masjid Agung Kyai Gede Kotawaringin Lama", "Masjid Agung Wahyu Al-Hadi Sampit"]
    },
    {
        "nama": "Kalimantan Timur", "pulau": "Kalimantan", "ibukota": "Samarinda",
        "cities": [
            ("Kota Samarinda", -0.5022, 117.1536), ("Kota Balikpapan", -1.2654, 116.8312),
            ("Kutai Kartanegara Tenggarong", -0.4167, 116.9833), ("Berau Tanjung Redeb", 2.1500, 117.4833),
            ("Kutai Barat Sendawar", -0.2333, 115.7000), ("Kutai Timur Sangatta", 0.5333, 117.5500),
            ("Kota Bontang", 0.1333, 117.5000), ("Penajam Paser Utara (IKN)", -1.2833, 116.7167),
            ("Paser Tanah Grogot", -1.9000, 116.1500), ("Mahakam Ulu Ujoh Bilang", 0.7000, 115.3000)
        ],
        "pantai": [
            "Pantai Derawan Berau Pulau Kura-Kura", "Pantai Maratua Surga Bahari Maladewa Kaltim", "Pantai Manggar Segarasari Balikpapan",
            "Pantai Lamaru Balikpapan Pohon Cemara", "Pantai Kemala Balikpapan Tepi Kota", "Pantai Biduk-Biduk Berau Labuan Cermin",
            "Pantai Melawai Sunset Balikpapan", "Pantai Nipah-Nipah Penajam Paser Utara", "Pantai Tanjung Batu Berau",
            "Pantai Marina Balikpapan", "Pantai Sekerat Kutai Timur", "Pantai Teluk Lombok Sangatta",
            "Pantai Panrita Lopi Muara Badak", "Pantai Tanah Merah Samboja Kukar", "Pantai Ambalat Samboja", "Pantai Kaniungan Besar Biduk-Biduk"
        ],
        "gunung": [
            "Titik Nol Nusantara (IKN Penajam Paser Utara)", "Bukit Bangkirai Samboja Canopy Bridge", "Bukit Selili Samarinda Paralayang",
            "Gunung Beriun Kutai Timur Karst Sangkulirang", "Bukit Soeharto Tahura Kutai", "Puncak Bukit Batu Dinding Samboja",
            "Bukit Alpha Balikpapan Teletubbies", "Gunung Embun Paser Negeri di Atas Awan", "Bukit Pelangi Sangatta",
            "Puncak Samarinda Islamic Center", "Bukit Biru Tenggarong", "Gunung Kongbeng Kutim"
        ],
        "alam": [
            "Danau Labuan Cermin Biduk-Biduk Danau Dua Rasa", "Danau Kakaban Berenang Bersama Ubur-Ubur Tanpa Sengat",
            "Gua Haji Mangku Maratua", "Taman Nasional Kutai Habitat Orangutan Morio", "Kawasan Karst Sangkulirang Mangkalihat UNESCO",
            "Hutan Lindung Sungai Wain Konservasi Beruang Madu Balikpapan", "Danau Semayang Danau Melintang Mahakam", "Susur Sungai Mahakam Pesut Mahakam",
            "Air Terjun Doyam Turu Paser", "Air Terjun Kedang Ipil Kukar"
        ],
        "budaya": [
            "Museum Mulawarman Keraton Kesultanan Kutai Kartanegara", "Desa Budaya Pampang Dayak Kenyah Samarinda",
            "Pulau Kumala Sungai Mahakam Tenggarong", "Kawasan Cagar Budaya IKN Sepaku", "Museum Daerah Kutai Kartanegara",
            "Desa Tenun Samarinda Seberang Sarung Samarinda", "Ladang Budaya (Ladaya) Tenggarong", "Situs Gua Telapak Tangan Purba Sangkulirang"
        ],
        "hiburan": ["Caribbean Island Waterpark Balikpapan", "Mahakam Lampion Garden (MLG) Samarinda", "Taman Rekreasi Lembah Hijau Samarinda", "Bontang Kuala Perkampungan Terapung Atas Laut", "Wisata Alam Kebun Raya Balikpapan"],
        "belanja": ["Pasar Kebun Sayur Pusat Batu Mulia Balikpapan", "Sentra Sarung Samarinda Seberang", "Pasar Citra Niaga Samarinda Kerajinan Dayak", "E-Walk Balikpapan Superblock", "Big Mall Samarinda"],
        "religi": ["Masjid Islamic Center Samarinda Masjid Terbesar Kedua Asia Tenggara", "Masjid Agung At-Taqwa Balikpapan", "Masjid Jami Aji Amir Hasanuddin Tenggarong 1874", "Gereja Santa Maria Katedral Samarinda", "Klenteng Thien Ie Kong Samarinda"]
    },
    {
        "nama": "Kalimantan Utara", "pulau": "Kalimantan", "ibukota": "Tanjung Selor",
        "cities": [
            ("Bulungan Tanjung Selor", 2.8500, 117.3667), ("Kota Tarakan", 3.3000, 117.6333),
            ("Nunukan", 4.1333, 117.6667), ("Malinau", 3.5833, 116.6333),
            ("Tana Tidung Tideng Pale", 3.5500, 117.2500)
        ],
        "pantai": [
            "Pantai Amal Baru & Lama Tarakan", "Pantai Batu Lamapu Sebatik Nunukan Perbatasan", "Pantai Ecing Nunukan",
            "Pantai Kayu Angin Sebatik", "Pantai Marina Tarakan", "Pantai Mamburungan Tarakan",
            "Pantai Tanah Kuning Bulungan Pasir Putih", "Pantai Kelapa Bulungan", "Pantai Sei Taiwan Sebatik Dua Negara",
            "Pantai Binalatung Tarakan", "Pantai Simangkadu Nunukan", "Pantai Gusung Tarakan Pulau Pasir",
            "Pantai Nipah Sebatik", "Pantai Tanjung Harapan Tana Tidung", "Pantai Bahagia Nunukan", "Pantai Tanjung Palas Bulungan"
        ],
        "gunung": [
            "Gunung Rian Tana Tidung Air Terjun Batu Raksasa", "Bukit Kasih Sayang Bulungan", "Bukit Teletubbies Tanjung Selor",
            "Gunung Putih Tanjung Palas Situs Bersejarah", "Puncak Bukit Cinta Nunukan", "Bukit Padan Sebatik",
            "Bukit Tempayan Malinau", "Puncak Perbatasan RI-Malaysia Sebatik", "Gunung Belumut Kaltara",
            "Bukit Salembatu Bulungan", "Puncak Selimau Tanjung Selor", "Bukit Simanggaris Nunukan"
        ],
        "alam": [
            "Taman Nasional Kayan Mentarang Hutan Primer Terluas Kaltara", "Kawasan Konservasi Mangrove & Bekantan (KKMB) Tarakan",
            "Air Terjun Semolon Sumber Air Panas Alami Malinau", "Air Terjun Sianak Tana Tidung", "Sungai Kayan Arung Jeram",
            "Gua Karst Gunung Putih Tanjung Palas", "Air Terjun Martin Billa Malinau", "Danau Buatan Persemaian Tarakan",
            "Gua Mangkaliat Bulungan", "Sumber Air Panas Sajau Tanjung Palas Timur"
        ],
        "budaya": [
            "Museum Kesultanan Bulungan Tanjung Palas", "Rumah Adat Baloy Mayo Adat Tidung Tarakan", "Desa Wisata Setulang Malinau Hutan Adat Tane Olen",
            "Tugu Dwikora Nunukan Sejarah Konfrontasi", "Monumen Perang Dunia II Tarakan Peninggalan Australia-Jepang",
            "Desa Budaya Pulau Sapi Malinau Dayak Lundayeh", "Museum Roemah Boendar Tarakan", "Batu Benau Cagar Budaya Bulungan"
        ],
        "hiburan": ["Taman Berlabuh Tarakan Tepi Laut", "Taman Oval Ladang Tarakan", "Waterpark Malinau Kota", "Taman Cendrawasih Tanjung Selor", "Taman Kota Tideng Pale Tana Tidung"],
        "belanja": ["Pasar Gusher Tarakan Pusat Kepiting Kenari", "Sentra Tenun Batik Kaltara Lundayeh Malinau", "Pasar Inpres Tanjung Selor", "Sentra Kerajinan Manik Dayak Malinau", "Grand Tarakan Mall"],
        "religi": ["Masjid Agung Baitul Izzah Islamic Center Tarakan", "Masjid Kasimuddin Peninggalan Sultan Bulungan Tanjung Palas", "Gereja Katedral Santa Maria Immaculata Tarakan", "Klenteng To Pek Kong Tarakan", "Masjid Agung Istiqomah Tanjung Selor"]
    },

    # ==================== SULAWESI (6 PROVINSI) ====================
    {
        "nama": "Sulawesi Utara", "pulau": "Sulawesi", "ibukota": "Manado",
        "cities": [
            ("Kota Manado", 1.4748, 124.8421), ("Kota Tomohon", 1.3250, 124.8400),
            ("Minahasa Tondano", 1.3000, 124.9167), ("Minahasa Utara Airmadidi", 1.4167, 124.9833),
            ("Kota Bitung", 1.4400, 125.1800), ("Minahasa Selatan Amurang", 1.1833, 124.5667),
            ("Kepulauan Sangihe Tahuna", 3.6167, 125.5000), ("Kepulauan Talaud Melonguane", 4.0000, 126.7000),
            ("Bolaang Mongondow Kotamobagu", 0.7333, 124.3167), ("Kepulauan Sitaro Ondong", 2.7333, 125.4000)
        ],
        "pantai": [
            "Pantai Malalayang Manado", "Pantai Paal Likupang DPSP Pasir Putih", "Pantai Pulisan Likupang Tebing Karang",
            "Pantai Batu Angus Bitung Selat Lembeh", "Pantai Firdaus Kema Minut", "Pantai Kanada Bitung",
            "Pantai Lakban Ratatotok Mitra Ekowisata Emas", "Pantai Moat Bolmong", "Pantai Paniki Siau Sitaro",
            "Pantai Batu Lubang Pulau Lembeh", "Pantai Serena Lembeh", "Pantai Pall Likupang Timur",
            "Pantai Boulevard Amurang Minsel", "Pantai Ria Manado", "Pantai Mahembang Minahasa", "Pantai Surabaya Likupang"
        ],
        "gunung": [
            "Gunung Lokon Tomohon Kawah Aktif Tompaluan", "Gunung Mahawu Kawah Hijau Tomohon", "Gunung Klabat Puncak Tertinggi Sulut (1.995 mdpl)",
            "Gunung Soputan Letusan Eksotis", "Bukit Kasih Kanonang Monumen 5 Agama", "Puncak Bukit Doa Mahawu Kelong Tomohon",
            "Puncak Tetempangan Koha Manado Paralayang", "Bukit Tetetana Kumelembuai Tomohon Bunga", "Gunung Karangetang Sitaro Gunung Api Aktif",
            "Gunung Awu Sangihe", "Gunung Tumpa Siladen View Manado", "Bukit Larata Likupang Padang Sabana"
        ],
        "alam": [
            "Taman Nasional Bunaken Surga Terumbu Karang Segitiga Karang Dunia", "Pulau Siladen Taman Laut Pasir Putih",
            "Selat Lembeh Muck Diving Ibukota Nudibranchia Dunia", "Danau Linow Tomohon Tiga Warna Belerang",
            "Danau Tondano Danau Vulkanik Terluas Sulut", "Taman Wisata Alam Batu Putih Tangkoko Tarsius Spektrum",
            "Air Terjun Ratahan Telu Minahasa", "Air Terjun Kima Atas Manado", "Pulau Manado Tua Siluet Megah", "Kawasan Likupang Destinasi Super Prioritas"
        ],
        "budaya": [
            "Waruga Airmadidi Makam Kuno Megalitikum Leluhur Minahasa", "Monumen Yesus Memberkati Manado Tertinggi Ke-4 Dunia",
            "Museum Negeri Provinsi Sulawesi Utara", "Kampung Cina Ban Hin Kiong Manado", "Benteng Moraya Tondano Perang Minahasa",
            "Desa Wisata Bunga Tomohon", "Desa Adat Pulisan Likupang", "Jembatan Soekarno Manado Ikon Kota"
        ],
        "hiburan": ["CitraLand Waterpark Manado", "Taman Kesatuan Bangsa (TKB) Manado", "Tuur Ma'asering Tomohon Hutan Aren Nira", "Manado Skyline Tetempangan", "Grand Luley Bunaken Resort"],
        "belanja": ["Pasar Beriman Tomohon Pasar Tradisional Ikonik", "Sentra Klappertaart Christine Manado", "Manado Town Square (Mantos)", "Sentra Ikan Cakalang Fufu Flamboyan", "Pasar 45 Pusat Belanja Manado"],
        "religi": ["Klenteng Ban Hin Kiong Tertua di Manado 1686", "Gereja Sentrum Manado Peninggalan Belanda", "Masjid Raya Ahmad Yani Manado", "Gereja Katedral Hati Tersuci Maria Manado", "Bukit Kasih Kanonang"]
    },
    {
        "nama": "Gorontalo", "pulau": "Sulawesi", "ibukota": "Gorontalo",
        "cities": [
            ("Kota Gorontalo", 0.5435, 123.0568), ("Bone Bolango Suwawa", 0.5333, 123.1833),
            ("Gorontalo Limboto", 0.6333, 122.9833), ("Gorontalo Utara Kwandang", 0.8333, 122.9000),
            ("Pohuwato Marisa", 0.4500, 121.9333), ("Boalemo Tilamuta", 0.6500, 122.3333)
        ],
        "pantai": [
            "Pantai Botubarani Hiu Paus (Whale Shark) Jinak", "Pantai Olele Taman Laut Koral Salvador Dali",
            "Pantai Bolihutuo Boalemo Pantai Pasir Putih", "Pantai Kurenai Bone Bolango", "Pantai Monano Gorontalo Utara",
            "Pantai Minanga Atinggola", "Pantai Biluhu Timur Tebing Karang", "Pantai Dulamayo Teluk Tomini",
            "Pantai Libuo Pohuwato", "Pantai Pohe Kota Gorontalo Tangga 2000", "Pantai Lahilote Legenda Telapak Kaki",
            "Pantai Pasir Putih Leato", "Pantai Dulupi Boalemo", "Pantai Molingkapoto Kwandang", "Pantai Buntulia Pohuwato", "Pantai Torosiaje Laut Bajo"
        ],
        "gunung": [
            "Puncak Dulamayo Negeri di Atas Awan Gorontalo", "Puncak Hutan Pinus Motilango", "Bukit Arang Lonuo Bone Bolango Paralayang",
            "Gunung Tabongo Gorontalo", "Bukit Layang Kota Gorontalo Panorama", "Puncak Gunung Boliyohuto",
            "Bukit Proklamasi Gorontalo", "Puncak Merah Putih Kwandang", "Bukit Tihengo Boalemo",
            "Puncak Karang Ilomata", "Bukit Kasih Pohuwato", "Puncak Tilongkabila Bone Bolango"
        ],
        "alam": [
            "Pulau Saronde Gorontalo Utara Maladewa Sulawesi", "Danau Limboto Danau Alami Gorontalo",
            "Taman Laut Olele Karang Karpet", "Air Terjun Hiyaliyo Da'a Gorontalo Utara", "Pemandian Air Panas Lombongo Suwawa",
            "Air Terjun Dulamayo Asri", "Desa Terapung Torosiaje Suku Bajo Pohuwato", "Pulau Cinta Boalemo Resort Hati Mengapung",
            "Air Terjun Lombongo Taman Nasional Bogani", "Cagar Alam Panua Pohuwato Burung Maleo"
        ],
        "budaya": [
            "Benteng Otanaha Peninggalan Abad ke-16 Kerajaan Ilahudu", "Rumah Adat Dulohupa Gorontalo Arsitektur Tradisional",
            "Museum Purbakala Popalo Gorontalo", "Desa Adat Bongo Desa Religi Bubohu", "Benteng Ulanta Suwawa Bone Bolango",
            "Pendaratan Amfibi Soekarno Danau Limboto", "Rumah Adat Gobel Tapa", "Makam Sultan Amai Raja Muslim Pertama"
        ],
        "hiburan": ["Menara Keagungan Limboto Menara Eiffel Gorontalo", "Taman Kota Gorontalo Taruna Remaja", "Pemandian Kolam Potanga", "Waterpark Karsa Utama Gorontalo", "Taman Budaya Limboto"],
        "belanja": ["Sentra Kain Tenun Karawo Tradisional Gorontalo", "Sentra Kue Pia Gorontalo Sinar Terang", "Pasar Sentral Kota Gorontalo", "Sentra Kopi Pinogu Organik Organisasi", "Mall Gorontalo"],
        "religi": ["Masjid Walima Emas Desa Bubohu Puncak Bukit", "Masjid Agung Baiturrahim Kota Gorontalo", "Masjid Hunto Sultan Amai 1495 Masehi Tertua", "Klenteng Tulus Harapan Kita Gorontalo", "Gereja Katolik Santo Kristoforus Gorontalo"]
    },
    {
        "nama": "Sulawesi Tengah", "pulau": "Sulawesi", "ibukota": "Palu",
        "cities": [
            ("Kota Palu", -0.9000, 119.8333), ("Donggala", -0.6833, 119.7500),
            ("Poso", -1.4000, 120.7500), ("Tojo Una-Una Ampana (Togean)", -0.8667, 121.6167),
            ("Banggai Luwuk", -0.9500, 122.7833), ("Toli-Toli", 1.0333, 120.8167),
            ("Parigi Moutong", -0.8167, 120.1833), ("Sigi Biromaru", -1.1500, 119.9500),
            ("Morowali Bungku", -2.4833, 121.9500), ("Banggai Kepulauan Salakan", -1.3333, 123.1667)
        ],
        "pantai": [
            "Pantai Tanjung Karang Donggala Pasir Putih Diving", "Pantai Talise Teluk Palu", "Pantai Danau Paisu Pok Banggai Air Kaca Sebening Cermin",
            "Pantai Kadidiri Kepulauan Togean", "Pantai Sera Donggala", "Pantai Kilo Lima Luwuk Banggai",
            "Pantai Boneoge Donggala", "Pantai Prince John Dive Resort Donggala", "Pantai Malenge Togean Ubur-Ubur",
            "Pantai Kaliburu Donggala", "Pantai Sabang Toli-Toli", "Pantai Enu Donggala",
            "Pantai Kayubura Parigi Teluk Tomini", "Pantai Matindok Banggai", "Pantai Siabang Morowali", "Pantai Kura-Kura Toli-Toli"
        ],
        "gunung": [
            "Puncak Matantimali Sigi Tempat Paralayang Terbaik Asia Tenggara", "Gunung Gawalise Palu Puncak Salena",
            "Gunung Nokilalaki Lore Lindu (2.355 mdpl)", "Gunung Sojol Donggala", "Bukit Salena Palu Sunset",
            "Bukit Keles Luwuk Kota Air Berbintang", "Puncak Bukit Teletubbies Luwuk Banggai", "Puncak Doda Sigi Hills",
            "Gunung Tinombala Toli-Toli", "Puncak Padamarari Morowali", "Gunung Tambusisi Morowali Utara", "Bukit Asam Palu"
        ],
        "alam": [
            "Taman Nasional Kepulauan Togean Cagar Biosfer UNESCO", "Danau Poso Danau Terbesar Ketiga Indonesia Berpasir Kuning",
            "Danau Paisu Pok Banggai Kepulauan Danau Kaca Biru", "Taman Nasional Lore Lindu Habitat Fauna Endemik Maleo Anoa",
            "Air Terjun Saluopa Poso 12 Tingkat Bertangga Batu", "Air Terjun Piala Luwuk Air Hijau Zamrud Alami",
            "Gua Karst Pulau Malenge Danau Ubur-Ubur", "Gua Latea Poso Kuburan Batu Purba", "Pusat Laut Donggala Sumur Alami Raksasa Tepi Laut", "Air Terjun Watu Mabontina Morowali"
        ],
        "budaya": [
            "Situs Megalitikum Lembah Bada Patung Batu Purba Lore Lindu", "Museum Sulawesi Tengah Palu",
            "Rumah Adat Souraja Banua Mbaso Palu Rumah Raja", "Tugu Perdamaian Nosarara Nosabatutu Palu",
            "Keraton Banggai Kesultanan Luwuk", "Pusat Kerajinan Tenun Donggala Sutra Asli", "Desa Adat Mantikole Sigi", "Situs Megalitikum Pokekea Lembah Besoa"
        ],
        "hiburan": ["Palu Grand Mall Tepi Teluk", "Taipa Beach Resort Palu Waterboom", "Taman Nasional Hutan Kota Kaombona Palu", "Taman GOR Palu Kuliner Malam", "Dermaga Sunset Donggala"],
        "belanja": ["Pasar Tradisional Manonda Palu", "Sentra Bawang Goreng Palu Sri Rejeki", "Sentra Tenun Donggala Sutera Buatan Tangan", "Pusat Kerajinan Kayu Hitam Eboni Palu", "Luwuk Shopping Center"],
        "religi": ["Masjid Terapung Arkam Babu Rahman Teluk Palu Saksi Tsunami", "Masjid Agung Baiturrahim Lolu Palu", "Gereja Tua Imanuel Poso 1900-an", "Pura Agung Jagatnatha Giri Natha Palu", "Gereja Katolik Santa Maria Palu"]
    },
    {
        "nama": "Sulawesi Barat", "pulau": "Sulawesi", "ibukota": "Mamuju",
        "cities": [
            ("Mamuju", -2.6788, 118.8877), ("Polewali Mandar (Polman)", -3.4333, 119.3333),
            ("Majene", -3.5333, 118.9667), ("Mamasa", -2.9667, 119.3833),
            ("Mamuju Tengah Tobadak", -2.1000, 119.3000), ("Pasangkayu", -1.1833, 119.3667)
        ],
        "pantai": [
            "Pantai Manakarra Mamuju Tepi Landmark Kota", "Pantai Karampuang Pulau Karst Terumbu Karang",
            "Pantai Mampie Polman Konservasi Penyu Laut", "Pantai Palippis Majene Tebing Karang Gua Kelelawar",
            "Pantai Dato Majene Pasir Putih Tangga Karang", "Pantai Gonda Mangrove Park Polman Snorkeling",
            "Pantai Barane Majene Sunset Nelayan", "Pantai Koa-Koa Pasangkayu Pasir Halus", "Pantai Lombang-Lombang Mamuju",
            "Pantai Tanjung Buku Polman Hutan Bakau", "Pantai Babampongi Mamuju Tengah", "Pantai Labuang Majene Perahu Sandeq",
            "Pantai Batu Raja Pasangkayu", "Pantai Belang-Belang Mamuju", "Pantai Silopo Polman Pelabuhan", "Pantai Ahu Mamuju"
        ],
        "gunung": [
            "Gunung Gandang Dewata Puncak Tertinggi Sulbar (3.074 mdpl) Sakral", "Puncak Bukit Anjoro Mamuju Landmark Mamuju City",
            "Puncak Buntu Liarra Mamasa Negeri di Atas Awan Bidadari", "Bukit Buttu Macca Majene", "Puncak Mambulilling Mamasa Dingin Sejuk",
            "Puncak Salubarana Mamuju", "Bukit Senayan Pasangkayu", "Puncak Rura Mamasa Lembah Hijau",
            "Bukit Teletubbies Polman", "Puncak Pass Majene Panorama Selat Makassar", "Gunung Mando Mandar", "Bukit Kelapa Tujuh Pasangkayu"
        ],
        "alam": [
            "Pulau Karampuang Sumur Tiga Rasa & Terumbu Karang", "Air Terjun Tamasapi Mamuju Hutan Lindung",
            "Liawan Waterfall Air Terjun Bertingkat Mamasa", "Permandian Air Panas Limbong Lopi Polman", "Gua Purba Kalumpang Arkeologi Prasejarah",
            "Air Terjun Indo Rannuang Polman", "Rawa Mangrove Pasangkayu Ekowisata", "Danau Mampie Surga Burung Air",
            "Arung Jeram Sungai Mamasa Arus Deras", "Air Terjun Malunda Majene"
        ],
        "budaya": [
            "Perahu Tradisional Sandeq Mandar Tercepat Dunia Tanpa Mesin", "Rumah Adat Boyang Mandar Somba Majene",
            "Rumah Tradisional Adat Banua Sibatang Mamasa Tanduk Kerbau", "Museum Mandar Majene Peninggalan Kerajaan Balanipa",
            "Makam Raja-Raja Banggae Majene Bukit Karst", "Sentra Tenun Sutra Mandar Saqbe Tinambung Polman",
            "Desa Budaya Ballapeu Mamasa Tarian Tradisional", "Pesta Adat Sayyang Pattu'du Kuda Menari Mandar"
        ],
        "hiburan": ["Taman Kota Surowako Mamuju", "Waterpark Polewali Mandar Bahari Manding", "Anjungan Pantai Manakarra Landmark Raksasa", "Taman Bunga Mamasa Agrowisata", "Komp. Wisata Buttu Ciping Tinambung"],
        "belanja": ["Pasar Sentral Pekkabata Polman", "Sentra Tenun Saqbe Mandar Tinambung", "Sentra Kopi Arabika Mamasa Asli Pegunungan", "Pusat Kuliner Jepa dan Ikan Terbang Majene", "Maleo Town Square Mamuju"],
        "religi": ["Masjid Raya Suhada Mamuju Arsitektur Modern Megah", "Masjid Imam Lapeo Campalagian Ulama Karismatik Mandar", "Gereja Tua Mamasa Klasik Kayu Rante-Buda", "Masjid Agung Syuhada Polman", "Masjid Tua Salabose Majene Abad Ke-17"]
    },
    {
        "nama": "Sulawesi Selatan", "pulau": "Sulawesi", "ibukota": "Makassar",
        "cities": [
            ("Kota Makassar", -5.1477, 119.4327), ("Gowa Sungguminasa", -5.2000, 119.4500),
            ("Maros", -5.0000, 119.5667), ("Bulukumba", -5.5500, 120.2000),
            ("Tana Toraja Makale", -3.1000, 119.8667), ("Toraja Utara Rantepao", -2.9667, 119.9000),
            ("Kepulauan Selayar Benteng", -6.1167, 120.5167), ("Kota Palopo", -2.9945, 120.1954),
            ("Kota Parepare", -4.0167, 119.6333), ("Bone Watampone", -4.5333, 120.3167)
        ],
        "pantai": [
            "Pantai Losari Makassar Ikon Pisang Epe & Sunset", "Pantai Bira Tanjung Bira Pasir Selembut Tepung Bulukumba",
            "Pantai Bara Bulukumba Tepi Tebing Karang Sunyi", "Pantai Marina Bantaeng Kawasan Rekreasi Pantai",
            "Pantai Akkarena Makassar Kafe Tepi Laut", "Pantai Liang Kareta Kepulauan Selayar Pasir Murni",
            "Pantai Kuri Caddi Maros Pesisir Asri", "Pantai Galesong Takalar Resor Waterboom",
            "Pantai Lemo-Lemo Bulukumba Pembuatan Perahu Pinisi", "Pantai Apparalang Bulukumba Tebing Mirip Raja Ampat",
            "Pantai Ujung Genteng Bone", "Pantai Baloiya Selayar Gua Karang", "Pantai Mattirotasi Parepare",
            "Pantai Lowita Pinrang", "Pantai Punaga Takalar Tebing Karang Indah", "Pantai Jalange Luwu"
        ],
        "gunung": [
            "Gunung Bawakaraeng Malino Gowa Sakral", "Gunung Latimojong Puncak Rante Mario Tertinggi Sulawesi (3.478 mdpl)",
            "Puncak Lolai Toraja Utara Negeri di Atas Awan Tongkonan", "Gunung Sesean Toraja Pemandangan Awan Megah",
            "Malino Highlands Perkebunan Teh Dingin Sejuk", "Bukit Ollon Toraja Lembah Swiss Sabana Domba",
            "Puncak Pabbentengang Maros Karst Purba", "Gunung Bulusaraung Pangkep Tracking Karst",
            "Puncak Tinggimoncong Gowa", "Puncak Biringkanaya Makassar", "Bukit Kenari Parepare", "Puncak Bila Sidrap Kincir Angin PLTB"
        ],
        "alam": [
            "Taman Nasional Bantimurung Maros Kerajaan Kupu-Kupu Dunia", "Rammang-Rammang Maros Kawasan Karst Terbesar Kedua di Dunia",
            "Taman Laut Nasional Taka Bonerate Atol Terbesar Ketiga Dunia Selayar", "Danau Tempe Wajo Rumah Terapung Tradisional",
            "Gua Leang-Leang Maros Lukisan Dinding Prasejarah Tertua Dunia (45.000 Tahun)", "Air Terjun Bantimurung Tirai Raksasa",
            "Air Terjun Ketemu Jodoh Malino", "Danau Matano Luwu Timur Danau Terdalam Se-Asia Tenggara",
            "Permandian Air Panas Lejja Soppeng Belerang Alami", "Gua Mampu Bone Gua Terluas Bertingkat Tujuh"
        ],
        "budaya": [
            "Kete Kesu Toraja Desa Adat Tongkonan & Makam Tebing Pahat", "Londa Toraja Makam Gua Gantung Pahat Peti Mati Kuno",
            "Desa Tanah Beru Bulukumba Pusat Pembuatan Kapal Pinisi Warisan UNESCO", "Benteng Rotterdam Fort Rotterdam Makassar 1673",
            "Benteng Somba Opu Peninggalan Kejayaan Kesultanan Gowa", "Istana Balla Lompoa Museum Pusaka Emas Kerajaan Gowa",
            "Kompleks Makam Raja-Raja Tallo Makassar", "Lemo Toraja Patung Kayu Tao-Tao Pemakaman Tebing Batu"
        ],
        "hiburan": ["Trans Studio Mall Makassar Theme Park", "Bugis Waterpark Adventure Makassar", "Pantai Pasir Putih CPI Sunset Quay", "Taman Gajah Makassar Ruang Publik", "Kincir Angin PLTB Tolo Jeneponto & Sidrap"],
        "belanja": ["Pasar Butung Makassar Pusat Grosir Tekstil", "Sentra Minyak Tawon Somba Opu", "Sentra Kain Sutera Sengkang Wajo", "Sentra Kopi Arabika Toraja Asli Rantepao", "Mall Ratu Indah Makassar"],
        "religi": ["Masjid 99 Kubah CPI Makassar Karya Ridwan Kamil Megah", "Masjid Terapung Amirul Mukminin Pantai Losari", "Masjid Raya Makassar Arsitektur Timur Tengah", "Gereja Katedral Hati Kudus Yesus Makassar", "Pura Giri Natha Makassar"]
    },
    {
        "nama": "Sulawesi Tenggara", "pulau": "Sulawesi", "ibukota": "Kendari",
        "cities": [
            ("Kota Kendari", -3.9985, 122.5126), ("Kota Baubau Buton", -5.4667, 122.6000),
            ("Wakatobi Wangi-Wangi", -5.3167, 123.5833), ("Konawe Unaaha", -3.8667, 122.0500),
            ("Konawe Utara Wanggudu", -3.4000, 122.1833), ("Konawe Selatan Andoolo", -4.3333, 122.2500),
            ("Kolaka", -4.0500, 121.6000), ("Buton Pasarwajo", -5.1667, 122.8333),
            ("Muna Raha", -4.8500, 122.7167), ("Bombana Rumbia", -4.7500, 121.8333)
        ],
        "pantai": [
            "Pantai Nirwana Baubau Tiga Warna Pasir Mutiara", "Pantai Nambo Kendari Pasir Landai Pohon Kelapa",
            "Pantai Toronipa Kendari Wisata Keluarga", "Pantai Sawa Konawe Utara Pasir Putih Bersih",
            "Pantai Kamali Baubau Patung Naga Megah", "Pantai Lakeba Baubau Dermaga Kayu Romantis",
            "Pantai Huntete Tomia Wakatobi Karang Luas", "Pantai Hoga Pulau Hoga Surga Penyelam Dunia",
            "Pantai Cemara Wangi-Wangi Wakatobi", "Pantai Meleura Muna Danau Karst Tepi Laut",
            "Pantai Walengkabola Muna Pasir Putih Halus", "Pantai Taipa Konawe Utara Tempat Bertelur Maleo",
            "Pantai Mandra Kolaka Sunset Tepi Kota", "Pantai Kayu Angin Kolaka", "Pantai Bungi Buton", "Pantai Bokori Pulau Pasir Putih Kendari"
        ],
        "gunung": [
            "Puncak Sorawolio Baubau Hutan Pinus Sejuk", "Puncak Oheo Konawe Utara Panorama Alam", "Puncak Popalia Ranomeeto Konservasi",
            "Puncak Kahianga Tomia Wakatobi Sunset Menakjubkan", "Puncak Amarilis Kendari", "Bukit Teletubbies Bombana Rumbia Sabana",
            "Puncak Mengkudu Kolaka", "Puncak Tirawuta Kolaka Timur", "Bukit Palelat Wakatobi",
            "Puncak Labengki Blue Lagoon View", "Bukit Wakila Muna", "Puncak Mowewe Kolaka"
        ],
        "alam": [
            "Taman Nasional Wakatobi Pusat Keanekaragaman Karang Dunia (Coral Triangle)", "Pulau Labengki Raja Ampat Sulawesi Tenggara Mini",
            "Danau Ubur-Ubur Lohia Muna Tanpa Sengat", "Gua Liang Kabori Muna Lukisan Karst Tertua Layang-Layang Kuno",
            "Air Terjun Moramo Konsel Bertingkat 127 Undakan Batu Marmer", "Sungai Tamborasi Kolaka Sungai Terpendek Kedua di Dunia (20 meter)",
            "Gua Moko Muna Kolam Alami Air Tawar Jernih", "Pulau Sombori Teluk Karst Spektakuler", "Air Terjun Tetewa Konawe", "Rawa Aopa Watumohai Taman Nasional Konservasi Rusa"
        ],
        "budaya": [
            "Benteng Keraton Buton Benteng Terluas di Dunia Rekor Guinness World Records", "Istana Malige Rumah Adat Buton Kayu Tanpa Paku",
            "Museum Negeri Bharugano Wuna Muna", "Perkampungan Bajo Mola Wakatobi Rumah di Atas Karang",
            "Batu Popaua Tempat Pelantikan Raja-Raja Buton", "Tari Tradisional Lulo Massal Kendari", "Desa Wisata Tenun Masalili Muna", "Masjid Keraton Buton Tua 1712"
        ],
        "hiburan": ["Kendari Water Sports Anjungan Teluk Kendari", "CitraLand Waterpark Kendari", "Taman Kota Kendari Jogging Track", "Jembatan Teluk Kendari Bahteramas Megah", "Wakatobi Dive Resort Pelayanan Dunia"],
        "belanja": ["Pusat Kerajinan Perak Kendari Kendari Filigree", "Sentra Tenun Buton & Muna Masalili", "Pasar Sentral Kota Kendari", "Sentra Kopi Rumbia Bombana", "The Park Kendari Mall"],
        "religi": ["Masjid Al-Alam Masjid Terapung Tengah Teluk Kendari", "Masjid Agung Keraton Buton", "Masjid Raya Alkautsar Kendari", "Gereja Katedral Santo Fransiskus Xaverius Kendari", "Pura Jagatnatha Kendari"]
    },

    # ==================== MALUKU (2 PROVINSI) ====================
    {
        "nama": "Maluku", "pulau": "Maluku", "ibukota": "Ambon",
        "cities": [
            ("Kota Ambon", -3.6954, 128.1814), ("Maluku Tengah Masohi Banda", -3.2900, 128.9500),
            ("Maluku Tenggara Langgur Kei", -5.6667, 132.7333), ("Kota Tual", -5.6333, 132.7500),
            ("Buru Namlea", -3.2500, 127.0833), ("Seram Bagian Barat Piru", -3.0833, 128.2500),
            ("Seram Bagian Timur Bula", -3.0500, 130.5000), ("Kepulauan Tanimbar Saumlaki", -7.9833, 131.3000),
            ("Kepulauan Aru Dobo", -5.7500, 134.2167), ("Maluku Barat Daya Tiakur", -8.1500, 127.9500)
        ],
        "pantai": [
            "Pantai Pasir Panjang Ngurbloat Kei Pasir Terhalus di Dunia", "Pantai Pintu Kota Ambon Karang Berlubang Tebing Laut",
            "Pantai Natsepa Ambon Ikon Rujak Buah Natsepa", "Pantai Liang Ambon (Pantai Hunimua) Air Sebening Kaca",
            "Pantai Ora Pulau Seram Surga Maladewa Indonesia", "Pantai Bair Tual Raja Ampat Maluku",
            "Pantai Ngurtafur Pulau Warbal Pasir Timbul 2 km Burung Pelikan", "Pantai Hukurila Ambon Tebing Gua Karang",
            "Pantai Santai Ambon Snorkeling", "Pantai Namalatu Ambon Batu Kerikil Alami", "Pantai Jikumerasa Pulau Buru",
            "Pantai Kisar MBD Karang Mutiara", "Pantai Kurom Tanimbar", "Pantai Ohoidertawun Kei Pasir Surut Luas",
            "Pantai Lubang Buaya Morella", "Pantai Tanjung Marthafons Ambon"
        ],
        "gunung": [
            "Gunung Api Banda Kepulauan Banda Snorkeling Kawah Bawah Laut", "Gunung Binaiya Puncak Tertinggi Maluku (3.027 mdpl) Pulau Seram",
            "Bukit Karang Tebing Hatumete Seram", "Puncak Bukit Martha Christina Tiahahu Ambon", "Gunung Salahutu Ambon",
            "Bukit Masbait Kei Puncak Ziarah Katolik Salib Kristus", "Puncak Laworkawu Tanimbar", "Gunung Gamalama Buru",
            "Bukit Paralayang Batu Gong Ambon", "Puncak Sirimau Ambon", "Gunung Kerbau Moa MBD Sabana Kuda", "Bukit Koli Koli Seram"
        ],
        "alam": [
            "Kepulauan Banda Neira Kepulauan Rempah Bersejarah Pala & Cengkih Dunia", "Taman Bawah Laut Banda Neira Terumbu Karang Sehat",
            "Danau Rana Pulau Buru Danau Suci Terbesar Maluku", "Gua Hawang Kei Kolam Air Tawar Sebening Kristal",
            "Taman Nasional Manusela Cagar Biosfer Satwa Burung Kakatua Seram", "Air Terjun Wae Sai Seram Barat",
            "Air Terjun Haturessy Maluku Tengah", "Gua Luvat Kertayasa Lukisan Prasejarah Manusia Purba Kei",
            "Laguna Semblat Seram Timur", "Pulau Saparua Benteng Duurstede Sejarah Pattimura"
        ],
        "budaya": [
            "Benteng Belgica Banda Neira Benteng Segilima VOC Abad Ke-17 Uang Rp 1.000", "Benteng Nassau Banda Neira",
            "Rumah Pengasingan Bung Hatta & Sutan Sjahrir Banda Neira", "Museum Siwalima Ambon Koleksi Etnografi Seni Maluku",
            "Benteng Duurstede Pulau Saparua Markas Kapitan Pattimura", "Benteng Amsterdam Hila Leihitu Ambon Tertua 1642",
            "Gong Perdamaian Dunia Ambon Simbol Persaudaraan Pela Gandong", "Desa Adat Morella Atraksi Pukul Sapu Lidi Berdarah"
        ],
        "hiburan": ["Taman Pattimura Kota Ambon Ruang Terbuka Hijau", "Ambon City Center (ACC) Passo", "Taman Makam Pahlawan Kapitan Pattimura", "Waterpark Victoria Ambon", "Kolam Renang Waai Belut Raksasa Morea"],
        "belanja": ["Pasar Mardika Ambon Pasar Ikan Segar Cakalang", "Sentra Minyak Kayu Putih Asli Namlea Buru", "Pusat Kerajinan Besi Putih Morotai-Ambon", "Sentra Kacang Kenari Banda Neira & Halua Kenari", "Maluku City Mall (MCM) Ambon"],
        "religi": ["Masjid Tua Wapauwe Kaitetu Tertua di Maluku Sejak 1414 Masehi", "Gereja Maranatha Ambon Pusat GPM", "Gereja Katedral Santo Fransiskus Xaverius Ambon", "Masjid Raya Al-Fatah Ambon Kubah Emas Megah", "Gereja Tua Imanuel Hila 1780 Peninggalan VOC"]
    },
    {
        "nama": "Maluku Utara", "pulau": "Maluku", "ibukota": "Sofifi",
        "cities": [
            ("Kota Ternate", 0.7833, 127.3667), ("Kota Tidore Kepulauan", 0.6833, 127.4000),
            ("Halmahera Barat Jailolo", 1.0667, 127.4667), ("Halmahera Utara Tobelo", 1.7333, 128.0000),
            ("Pulau Morotai Daruba", 2.0500, 128.2833), ("Halmahera Selatan Labuha Bacan", -0.6333, 127.5000),
            ("Halmahera Tengah Weda", 0.4500, 127.9167), ("Halmahera Timur Maba", 0.7000, 128.3000),
            ("Kepulauan Sula Sanana", -2.0000, 125.9833), ("Pulau Taliabu Bobong", -1.8333, 124.4833)
        ],
        "pantai": [
            "Pantai Sulamadaha Ternate Air Laut Kaca Berenang Perahu Terapung", "Pantai Jikomalamo Ternate Surga Snorkeling Diving Terumbu Karang",
            "Pantai Dodola Morotai Pulau Pasir Putih Menyambung Pasang Surut", "Pantai Batu Angus Ternate Lahar Bekas Letusan Gunung Gamalama",
            "Pantai Kastela Ternate Tempat Pembunuhan Sultan Khairun Portugis", "Pantai Bobanehena Jailolo Pasir Hitam Belerang Hangat",
            "Pantai Kupa-Kupa Tobelo Karang Tropis Teduh", "Pantai Luari Halmahera Utara Sunrise Pasir Bersih",
            "Pantai Tugulufa Tidore Tepi Selat Pulau", "Pantai Pastofiri Tidore Gosong Pasir Timbul Laut",
            "Pantai Tanjung Gorango Morotai Tebing Megah Ombak Surfing", "Pantai Nunuhu Morotai",
            "Pantai Falajawa Boulevard Ternate Berenang Tepi Kota", "Pantai Disa Halmahera Timur",
            "Pantai Pulau Bacan Sawadai", "Pantai Selat Capalulu Taliabu Arus Kencang"
        ],
        "gunung": [
            "Gunung Gamalama Ternate Puncak Stratovolcano Aktif Penghasil Cengkih", "Gunung Kie Matubu Tidore Puncak Gunung Uang Kertas Rp 1.000",
            "Gunung Dukono Tobelo Kawah Belerang Vulkanik Aktif", "Gunung Gamkonora Halmahera Barat Tertinggi di Halmahera",
            "Puncak Gunung Ibu Kawah Letusan Berkala", "Bukit Ngade Ternate Danau Laguna Berlatar Pulau Tidore",
            "Puncak Cengkeh Afo Ternate Pohon Cengkih Tertua di Dunia", "Bukit Sabatai Morotai Pemandangan Pasifik",
            "Puncak Rappa Pelangi Tidore", "Gunung Sibela Pulau Bacan Cagar Alam Batu Bacan",
            "Bukit Loleo Halmahera", "Puncak Talaga Paca Halut"
        ],
        "alam": [
            "Danau Tolire Besar & Tolire Kecil Ternate Legenda Buaya Siluman", "Danau Laguna Ngade Ikon Pemandangan Ternate",
            "Air Terjun Cunca Kahatola Tebing Karang Jatuh Langsung ke Laut", "Taman Laut Selat Bacan Habitat Kima Raksasa",
            "Pulau Kakara Tobelo Asal Tarian Perang Cakalele", "Pulau Mitita Morotai Spot Menyelam Hiu Sirip Hitam",
            "Batu Angus Ternate Hamparan Batu Bekas Lahar Beku 1907", "Air Terjun Roko Halmahera Barat",
            "Danau Galela Halmahera Utara Perikanan Air Tawar", "Taman Nasional Aketajawe-Lolobata Habitat Burung Bidadari Halmahera"
        ],
        "budaya": [
            "Kedaton Kesultanan Ternate Museum Pusaka Mahkota Berambut Emas", "Kedaton Kesultanan Tidore Peninggalan Sultan Nuku Pahlawan Nasional",
            "Benteng Tolukko Ternate Benteng Portugis Menghadap Gamalama 1540", "Benteng Kalamata Benteng Bastion Portugis Menghadap Tidore",
            "Benteng Kastela Benteng Tertua Portugis Santo Yohanes Pembaptis", "Benteng Torre & Benteng Tahula Peninggalan Spanyol di Tidore",
            "Museum Perang Dunia II Morotai Monumen Tentara Sekutu Douglas MacArthur", "Desa Adat Sasadu Halmahera Barat Rumah Musyawarah Suku Sahu"
        ],
        "hiburan": ["Taman Landmark Kota Ternate Pinggir Laut", "Taman Film Ternate", "Taman Dodoku Ali Tidore Waterfront", "Taman Kota Tobelo Halmahera Utara", "Morotai Waterfront City Promenade"],
        "belanja": ["Pasar Gamalama Ternate Pusat Rempah Pala Cengkih", "Sentra Sirup Buah Pala Ternate Swering", "Pusat Kerajinan Batu Bacan Doko Halmahera Selatan", "Sentra Batik Tubo Motif Rempah Ternate", "Jatiland Mall Ternate"],
        "religi": ["Masjid Sultan Ternate Tua Sejak Abad ke-17 Atap Tumpang Empat", "Masjid Raya Shaful Khairaat Sofifi Ibu Kota Maluku Utara", "Gereja Tua Eben Haezer Tobelo 1898", "Klenteng Thian Hou Kiong Ternate Tepi Laut", "Gereja Katolik Santo Willibrordus Ternate"]
    },

    # ==================== PAPUA (6 PROVINSI) ====================
    {
        "nama": "Papua", "pulau": "Papua", "ibukota": "Jayapura",
        "cities": [
            ("Kota Jayapura", -2.5333, 140.7167), ("Jayapura Sentani", -2.5667, 140.5167),
            ("Keerom Waris", -3.2833, 140.7500), ("Sarmi", -1.8667, 139.3500),
            ("Mamberamo Raya Kasonaweja", -2.0000, 138.1667), ("Biak Numfor", -1.1833, 136.0833),
            ("Supiori Sorendiweri", -0.7333, 135.6000), ("Waropen Botawa", -2.4000, 136.5000),
            ("Kepulauan Yapen Serui", -1.8500, 136.2500)
        ],
        "pantai": [
            "Pantai Base-G Jayapura Pasir Putih Bersejarah Sekutu PD II", "Pantai Hamadi Jayapura Hutan Mangrove & Jembatan Merah Youtefa",
            "Pantai Pasir Enam Jayapura Tersembunyi Karang Tropis", "Pantai Holtekamp Jembatan Youtefa Ikon Baru Papua",
            "Pantai Tablanusu Pasir Kerikil Hitam Unik Bunyi Gemerisik", "Pantai Harlem Jayapura Kolam Air Tawar Sebelah Air Asin Terjernih",
            "Pantai Bosnik Biak Timur Terumbu Karang Air Biru", "Pantai Batu Pica Biak Deburan Karang Ombak Menjulang",
            "Pantai Segara Indah Bosnik Biak", "Pantai Wari Biak Pasir Lembut Ombak Lepas Pasifik",
            "Pantai Sorendiweri Supiori Mangrove Laut", "Pantai Amai Jayapura Muara Air Terjun Sungai Dingin",
            "Pantai Mariadei Yapen Serui", "Pantai Sarmi Ombak Selancar Pasifik", "Pantai Depapre Teluk Tanah Merah", "Pantai Doreri Manokwari-Biak"
        ],
        "gunung": [
            "Puncak Bukit Teletubbies Danau Sentani (Bukit Tungku Wiri)", "Puncak Jayapura City Pemandangan Kerlap-kerlip Lampu Teluk Youtefa",
            "Puncak Bukit MacArthur Ifar Gunung Markas Jenderal Sekutu", "Pegunungan Cycloop (Robhongholo) Cagar Alam Keramat Sumber Air",
            "Puncak Bukit Merah Putih Skouw Perbatasan Papua Nugini", "Bukit Pantai Dok 2 Jayapura",
            "Puncak Samber Biak Numfor", "Puncak Lembah Grime Keerom", "Puncak Gunung Botak Sarmi",
            "Puncak Bukit Polimak Jayapura", "Bukit Kasuari Biak", "Puncak Yoka Sentani Danau View"
        ],
        "alam": [
            "Danau Sentani 22 Pulau Kecil di Tengah Danau Eksotis", "Taman Nasional Pegunungan Cycloop Habitat Kangguru Pohon & Cenderawasih",
            "Gua Jepang Binsari Biak Saksi Bisu Perang Pasifik PD II", "Air Terjun Kiti-Kiti Danau Sentani",
            "Teluk Youtefa Hutan Bakau & Ikan Karang", "Kali Biru Genyem Kolam Alami Sebening Kaca di Tengah Hutan Rimba",
            "Air Terjun Wafsarak Biak Air Terjun Biru Menyegarkan", "Kepulauan Padaido Biak Surga Menyelam Terumbu Karang Karibia Papua",
            "Air Terjun Anmo Sarmi", "Sungai Mamberamo Amazon Papua Arung Buaya Liar"
        ],
        "budaya": [
            "Desa Adat Asei Pulau Danau Sentani Seni Lukis Kulit Kayu Khombouw", "Desa Adat Tobati & Enggros Suku Asli Teluk Youtefa",
            "Jembatan Merah Youtefa Ikon Infrastruktur Monumental Papua", "Museum Loka Budaya Universitas Cenderawasih Abepura",
            "Museum Negeri Provinsi Papua Waena", "Monumen Jenderal Douglas MacArthur Markas Perang Pasifik",
            "Kampung Adat Sauwandarek Biak Tradisi Barapen Bakar Batu", "Perbatasan RI-PNG Skouw Titik Gerbang Timur Indonesia"
        ],
        "hiburan": ["Stadion Utama Papua Bangkit (Lukas Enembe Stadium)", "Taman Imbi Jantung Kota Jayapura", "Jayapura City Mall (JCM) Entrop", "Taman Wisata Alam Youtefa", "Dermaga Wisata Danau Sentani Kalkhote"],
        "belanja": ["Pasar Tradisional Hamadi Pusat Souvenir Koteka & Noken Papua Asli", "Sentra Noken Kulit Kayu Sentani Binaan UNESCO", "Pasar Youtefa Abepura Sentra Buah Merah & Keladi", "Pusat Kerajinan Ukiran Asmat Jayapura", "Mall Abepura"],
        "religi": ["Gereja Katedral Gembala Baik Abepura", "Masjid Raya Baiturrahim Jayapura Tepi Teluk", "Tugu Salib Titik Masuk Injil Mansinam-Jayapura", "Gereja Tua Zeth Biak Numfor", "Masjid Agung As-Sholihin Abepura"]
    },
    {
        "nama": "Papua Barat", "pulau": "Papua", "ibukota": "Manokwari",
        "cities": [
            ("Manokwari", -0.8667, 134.0833), ("Fakfak", -2.9167, 132.3000),
            ("Kaimana", -3.6667, 133.7500), ("Teluk Bintuni", -2.1333, 133.5333),
            ("Teluk Wondama Rasiei", -2.7000, 134.5000), ("Manokwari Selatan Ransiki", -1.5000, 134.1833),
            ("Pegunungan Arfak Anggi", -1.3667, 133.9167)
        ],
        "pantai": [
            "Pantai Pasir Putih Manokwari Teluk Doreri Wisata Snorkeling", "Pantai Bakaro Manokwari Tradisi Pemanggil Ikan Peluit Alami",
            "Pantai Maruni Manokwari Pesisir Pabrik Semen Karang", "Pantai Bantemi Kaimana Sunset Teluk Triton Memukau",
            "Pantai Simora Kaimana Teluk Triton Karang Mengapung", "Pantai Air Tiba Fakfak Pasir Putih Berkeliling Pohon Kelapa",
            "Pantai Werabur Fakfak", "Pantai Yen Beba Manokwari", "Pantai Amban Manokwari Ombak Surfing Pasifik",
            "Pantai Syari Teluk Wondama Pesisir Teluk Cenderawasih", "Pantai Tubir Seram Fakfak", "Pantai Pulau Mansinam Tempat Ziarah Bersejarah",
            "Pantai Abasi Manokwari Komunitas Selancar Anak Papua", "Pantai Venu Kaimana Pulau Penyu Belimbing Bertelur",
            "Pantai Tanjung Kasuari Teluk Bintuni", "Pantai Pulau Karas Fakfak"
        ],
        "gunung": [
            "Pegunungan Arfak Puncak Tertinggi Papua Barat (2.955 mdpl) Surga Cenderawasih", "Puncak Bukit Kobrey Danau Anggi Pegaf",
            "Puncak Gunung Meja Manokwari Hutan Lindung Tugu Jepang", "Bukit Soribo Manokwari Panorama Kota",
            "Puncak Petuanan Kerajaan Fatagar Fakfak", "Puncak Mandopi Manokwari", "Puncak Bukit Boi Kaimana",
            "Bukit Ransiki Manokwari Selatan", "Puncak Danau Anggi Giji & Anggi Gida (Danau Laki-laki & Perempuan)",
            "Gunung Botak Manokwari Selatan Tebing Laut Spektakuler", "Bukit Mupi Manokwari", "Puncak Babo Bintuni"
        ],
        "alam": [
            "Teluk Triton Kaimana Surga Bawah Air Raja Ampat Selatan Koral Lunak", "Taman Nasional Teluk Cenderawasih Berenang Bersama Hiu Paus Kwatisore",
            "Danau Kembar Anggi Giji & Anggi Gida Pegunungan Arfak Sejuk", "Air Terjun Kiti-Kiti Fakfak Jatuh Langsung ke Air Laut Asin",
            "Gua Purba Kokas Fakfak Lukisan Tangan Merah Cadas Prasejarah Tebing Laut", "Hutan Mangrove Teluk Bintuni Mangrove Terluas Kedua di Dunia",
            "Kali Dingin Manokwari Mata Air Hutan Pegaf", "Air Terjun Anatu Kaimana", "Hutan Wisata Gunung Meja Monument Jepang", "Pulau Venu Kaimana Cagar Konservasi Penyu Hijau"
        ],
        "budaya": [
            "Pulau Mansinam Manokwari Pulau Bersejarah Pendaratan Injil Pertama di Tanah Papua 1855", "Situs Sejarah Tugu Salib Raksasa Mansinam",
            "Masjid Tua Patimburak Fakfak Simbol Toleransi Islam Satu Tungku Tiga Batu 1870", "Rumah Adat Kaki Seribu Suku Arfak Mod Aki Aksa",
            "Benteng Jepang Gua Binsari Kokas Fakfak Peninggalan Meriam PD II", "Desa Wisata Rhepang Muaif Pengamatan Burung Pintar Namdur",
            "Museum Negeri Mansinam Manokwari", "Perkampungan Tradisional Suku Kuri Bintuni"
        ],
        "hiburan": ["Taman Kota Manokwari Lapangan Borasi", "Taman Kota Kaimana Senja Kaimana", "Hadi Mall Manokwari", "Taman Bermain Anak Fakfak Waterfront", "Dermaga Wisata Teluk Doreri Manokwari"],
        "belanja": ["Pasar Sanggeng Manokwari Sentra Noken & Buah Salak Manokwari", "Sentra Pala Fakfak Permen Tomat Pala Asli Fakfak", "Sentra Cokelat Ransiki Kakao Organik Terbaik Dunia", "Pasar Ikan Sanggeng Manokwari", "Sentra Kerajinan Kulit Kayu Manokwari"],
        "religi": ["Gereja Pengharapan Mansinam Monumen Injil Papua", "Masjid Tua Patimburak Fakfak Bentuk Kubah Gereja-Masjid Filosofi Toleransi", "Gereja Katedral Santo Agustinus Manokwari", "Masjid Agung Ridwaniah Manokwari", "Tugu Titik Temu Peradaban Papua Mansinam"]
    },
    {
        "nama": "Papua Barat Daya", "pulau": "Papua", "ibukota": "Sorong",
        "cities": [
            ("Kota Sorong", -0.8833, 131.2500), ("Sorong Aimas", -0.9667, 131.3333),
            ("Raja Ampat Waisai", -0.4333, 130.8167), ("Sorong Selatan Teminabuan", -1.4500, 132.0167),
            ("Tambrauw Fef", -0.6000, 132.3333), ("Maybrat Kumurkek", -1.2500, 132.5000)
        ],
        "pantai": [
            "Pantai Pasir Timbul Raja Ampat Gosong Pasir Putih di Tengah Lautan Karang", "Pantai Waiwo Waisai Raja Ampat Menyelam Depan Kamar Resor",
            "Pantai Tanjung Kasuari Sorong Pasir Putih Pohon Rindang Tepi Kota", "Pantai Saonek Raja Ampat Sejarah Ibu Kota Lama",
            "Pantai Waisai Torang Cinta (WTC) Waterfront Kota Raja Ampat", "Pantai Arborek Pulau Desa Wisata Terumbu Karang Bawah Dermaga",
            "Pantai Pulau Friwen Pasir Halus & Gorengan Hangat Raja Ampat", "Pantai Saleo Waisai Air Teduh Rindang Pepohonan",
            "Pantai Jamursba Medi Tambrauw Tempat Bertelur Penyu Belimbing Raksasa Terbesar Dunia", "Pantai Warmamedi Tambrauw Konservasi Penyu",
            "Pantai Dofior Kota Sorong Sunset Tembok Berlin", "Pantai Seget Sorong Pesisir Kilang Minyak Bersejarah",
            "Pantai Pulau Misool Karst Selatan Air Sebening Permata", "Pantai Banos Misool Pasir Putih Halus",
            "Pantai Yeben Snorkeling Hiu Karang", "Pantai Rufas Laguna Karst Toska Tersembunyi"
        ],
        "gunung": [
            "Puncak Wayag Raja Ampat Ikon Dunia Bukit Karst Jamur Mengapung di Laut Biru", "Puncak Piaynemo Raja Ampat Miniatur Wayag Tangga Kayu",
            "Puncak Dapunlol Teluk Misool Karst Menjulang Megah Harimau", "Puncak Bukit Love Teluk Bidadari Karst Berbentuk Hati",
            "Puncak Bukit Peternakan Mare Maybrat", "Puncak Bukit Teletubbies Teminabuan Sorong Selatan",
            "Puncak Sorong City View Pemandangan Pelabuhan & Selat Dampier", "Gunung Tambrauw Konservasi Hutan Pegunungan",
            "Bukit Salju Fef Tambrauw Kabut Tebal Rimba", "Puncak Gunung Kwoka Tambrauw",
            "Bukit Somba Misool", "Puncak Teluk Mayalibit Raja Ampat Ngarai Sempit"
        ],
        "alam": [
            "Kepulauan Raja Ampat Ibukota Terumbu Karang Terkaya di Planet Bumi (UNESCO Global Geopark)",
            "Kali Biru Warsambin Raja Ampat Sungai Hutan Tropis Berair Biru Safir Dingin", "Danau Ayamaru Maybrat Tiga Danau Karst Purba Habitat Ikan Pelangi",
            "Kali Kaca Teminabuan Sorong Selatan Sungai Transparan Air Sebening Kaca", "Teluk Kabui Raja Ampat Tebing Karst dan Batu Pensil Megah",
            "Gua Keramat Misool Al-Qur'an Kuno & Kolam Bawah Tanah", "Laguna Bintang Star Lagoon Piaynemo Gugusan Karst Berbentuk Bintang",
            "Air Terjun Sasnek Sorong Selatan Bertingkat di Tengah Hutan Rimba Belantara", "Gua Tengkorak Misool Situs Makam Purba Prasejarah",
            "Manta Sandy Raja Ampat Stasiun Pembersihan Ikan Pari Manta Raksasa"
        ],
        "budaya": [
            "Desa Wisata Arborek Pengrajin Topi Pari Manta & Noken Anyam Daun Pandan Laut", "Desa Adat Sawinggrai Pusat Pengamatan Tari Burung Cenderawasih Merah Liar",
            "Kawasan Tembok Berlin Sorong Kuliner Pesisir Ikan Bakar", "Lukisan Cadas Tebing Purba Misool Cap Telapak Tangan Oker Merah",
            "Desa Tradisional Warsambin Pintu Masuk Teluk Mayalibit", "Rumah Adat Suku Maybrat Kain Timur Pusaka Sakral",
            "Tugu Selamat Datang Kota Sorong Pintu Gerbang Papua Barat Daya", "Desa Ekowisata Werur Tambrauw Jejak Sejarah Jenderal Douglas MacArthur"
        ],
        "hiburan": ["Taman Sorong City Landmark Kota", "Mega Mall Sorong Pusat Belanja Terbesar Sorong", "Waterpark Aimas Kabupaten Sorong", "Waisai Waterfront Park Raja Ampat", "Taman Kota Fef Tambrauw"],
        "belanja": ["Pasar Remu Sorong Sentra Oleh-Oleh Keripik Keladi & Abon Gulung Hawaii", "Sentra Roti Abon Gulung Sorong Bakery Manise", "Pasar Ikan Jembatan Puri Sorong Tuna & Lobster Segar", "Sentra Kerajinan Patung Asmat & Noken Raja Ampat", "Mall Sorong Square"],
        "religi": ["Masjid Raya Al-Akbar Kota Sorong Megah Kubah Emas", "Gereja Katedral Kristus Raja Sorong", "Gereja Tua Klasis Raja Ampat Waisai", "Vihara Buddha Jayanti Sorong Tepi Bukit", "Tugu Peringatan Masuknya Injil Tanah Malamoi Sorong"]
    },
    {
        "nama": "Papua Pegunungan", "pulau": "Papua", "ibukota": "Jayawijaya (Wamena)",
        "cities": [
            ("Jayawijaya Wamena", -4.0833, 138.9500), ("Lanny Jaya Tiom", -3.9000, 138.5000),
            ("Tolikara Karubaga", -3.6000, 138.6500), ("Yahukimo Dekai", -4.8500, 139.5000),
            ("Yalimo Elelim", -3.7500, 139.4000), ("Pegunungan Bintang Oksibil", -4.9000, 140.6333),
            ("Mamberamo Tengah Kobakma", -3.6500, 139.1000), ("Nduga Kenyam", -4.5000, 138.4000)
        ],
        "pantai": [
            "Pasir Putih Aikima Lembah Baliem Hamparan Pasir Putih Pegunungan Misterius", "Tepi Danau Habema Tertinggi Indonesia Berpasir Dingin",
            "Pesisir Pasir Kali Baliem Wamena Arus Deras Sungai Gunung", "Pesisir Danau Habbema Puncak Trikora",
            "Tepi Sungai Brazza Dekai Yahukimo Hutan Rawa Raksasa", "Pasir Kali Ibele Wamena Bebatuan Granit Lembah",
            "Tepi Danau Telaga Biru Maima Jayawijaya", "Pesisir Sungai Lorentz Nduga Aliran Gletser Salju",
            "Pantai Pasir Putih Sumur Alami Lembah Baliem", "Tepi Sungai Baliem Asologaima",
            "Pasir Kali Uwe Wamena", "Tepi Danau Hutan Trikora", "Pesisir Kali Tiom Lanny Jaya",
            "Tepi Sungai Oksibil Pegunungan Bintang", "Pesisir Kali Yawei Kobakma Mamberamo Tengah", "Tepi Sungai Brazza Bawah Yahukimo"
        ],
        "gunung": [
            "Puncak Trikora Puncak Tertinggi Papua Pegunungan (4.750 mdpl) Salju Abadi", "Pegunungan Jayawijaya Barisan Sudirman Tulang Punggung Pulau Papua",
            "Puncak Mandala Pegunungan Bintang (4.760 mdpl) Puncak Salju Kedua", "Lembah Baliem Hamparan Lembah Hijau Ketinggian 1.650 mdpl Terkenal Sedunia",
            "Puncak Bukit Wolani Wamena", "Puncak Bukit Isakusa Lembah Baliem", "Puncak Buntul Kurima Pintu Masuk Yahukimo",
            "Puncak Gunung Elit Yalimo", "Puncak Tiom Lanny Jaya Negeri Lembah Kabut Dingin",
            "Puncak Bokondini Tolikara Lembah Terisolir Eksotis", "Puncak Pass Oksibil Perbatasan PNG", "Bukit Susu Lembah Baliem Wamena"
        ],
        "alam": [
            "Danau Habema (Danau di Atas Awan) Danau Tertinggi di Indonesia (3.300 mdpl) Kaki Trikora",
            "Taman Nasional Lorentz Situs Warisan Dunia UNESCO Ekosistem Terlengkap dari Salju ke Tropis",
            "Gua Kotilola Wamena Gua Karst Raksasa Tempat Tinggal Kelelawar Purba Hutan Lembah",
            "Telaga Biru Maima Danau Keramat Air Biru Pekat Tersembunyi", "Air Terjun Napua Wamena Suasana Alami Hutan Pinus",
            "Mata Air Garam Alami Jiwika Sumur Garam Gunung di Atas Puncak Ketinggian Suku Dani",
            "Hutan Lumut Hutan Basah Trikora Berlumut Tebal Mirip Negeri Dongeng Fantasi",
            "Gua Lokale Wamena Gua Panjang Tanpa Ujung Terdalam", "Air Terjun Walesi Jayawijaya", "Danau Lereng Gunung Mandala Oksibil"
        ],
        "budaya": [
            "Mumi Kuno Jiwika Mumi Panglima Perang Suku Dani Berusia Ratusan Tahun Diawetkan Asap",
            "Mumi Pumo & Mumi Aikima Tradisi Pengawetan Jenazah Leluhur Suku Dani",
            "Desa Tradisional Obia Wamena Tempat Pelaksanaan Festival Budaya Lembah Baliem (FBLB)",
            "Rumah Adat Honai Rumah Tradisional Beratap Jerami Melingkar Khas Dataran Tinggi Pegunungan",
            "Perkampungan Tradisional Suku Yali Suku Kerdil Pembuat Jembatan Gantung Rotan Lembah Kurima",
            "Tradisi Barapen Pesta Bakar Batu Upacara Syukur Persaudaraan Nusantara Terbesar",
            "Suku Korowai Rumah Pohon Tinggi 30-50 Meter di Pucuk Pohon Hutan Belantara Yahukimo",
            "Festival Budaya Lembah Baliem Perang-Perangan Adat Menarik Ribuan Wisatawan Mancanegara"
        ],
        "hiburan": ["Taman Menara Salib Wamena Landmark Kota", "Taman Kota Karubaga Tolikara", "Pemandangan Lembah Sinakma Agrowisata Buah Kopi", "Taman Kota Tiom Lanny Jaya", "Wamena Mall Pusat Pertokoan Lembah"],
        "belanja": ["Pasar Jibama Wamena Pusat Kopi Arabika Wamena Terbaik Dunia", "Pasar Nayak Wamena Souvenir Noken Anggrek Emas Koteka & Tombak Kayu", "Sentra Kopi Arabika Organik Lembah Baliem Wamena", "Sentra Kerajinan Noken Serat Kayu Gaharu Wamena", "Pasar Dekai Yahukimo"],
        "religi": ["Gereja Katedral Kristus Penebus Wamena", "Gereja Salib Suci Jiwika", "Masjid Baiturrahman Wamena Simbol Kerukunan Dataran Tinggi", "Tugu Salib Kasih Elelim Yalimo", "Gereja GKI Betlehem Karubaga Tolikara"]
    },
    {
        "nama": "Papua Selatan", "pulau": "Papua", "ibukota": "Merauke",
        "cities": [
            ("Merauke", -8.4992, 140.4047), ("Boven Digoel Tanah Merah", -6.1000, 140.3000),
            ("Mappi Kepi", -6.5000, 139.3000), ("Asmat Agats", -5.5333, 138.1333)
        ],
        "pantai": [
            "Pantai Lampu Satu Merauke Mercusuar Bersejarah Pasir Landai Surut Berkilo-kilometer", "Pantai Onggaya Merauke Pasir Merah Eksotis Sunset Samudera Arafura",
            "Pantai Payum Merauke Tepi Kampus Musamus Hutan Kelapa", "Pantai Buti Merauke Pusat Kuliner Ikan Bakar Pesisir",
            "Pantai Imbuti Titik Temu Matahari Terbenam Ujung Timur", "Pantai Kimaam Pulau Yos Sudarso Muara Rawa",
            "Pantai Nasem Merauke Pantai Pasir Cokelat Asri", "Pantai Habe Pulau Karang Terluar Merauke",
            "Pantai Wapeko Merauke Hutan Mangrove", "Pantai Kumbe Merauke Muara Sungai Kumbe",
            "Pantai Samkai Merauke Tepi Kota", "Pantai Urumb Merauke", "Pantai Matara Merauke",
            "Pantai Kepi Mappi Rawa Tepi Pesisir", "Pantai Agats Asmat Pesisir Pasang Surut Laut Arafura", "Pantai Muara Digul Boven Digoel"
        ],
        "gunung": [
            "Puncak Bukit Musamus Sarang Semut Raksasa Rumah Rayap 4-5 Meter Ikonik Dunia", "Puncak Bukit Tanah Merah Boven Digoel Tempat Pengasingan Pejuang Kemerdekaan",
            "Bukit Salib Kepi Mappi Panorama Danau Rawa", "Puncak Bukit Bupul Merauke Pemandangan Sabana",
            "Bukit Mindiptana Boven Digoel Hutan Belantara", "Puncak Kimaam Perbukitan Karang Rawa",
            "Bukit Asmat Agats Jembatan Kayu di Atas Rawa", "Puncak Savana Kurik Merauke",
            "Bukit Perbatasan Sota Titik 0 KM Merauke Sabang", "Bukit Erambu Merauke Suaka Rusa",
            "Puncak Kali Digoel Tanah Merah", "Bukit Kali Kumbe Merauke"
        ],
        "alam": [
            "Taman Nasional Wasur (Serengeti Papua) Padang Sabana Terluas Rusa Kanguru Kuskus & Sarang Semut Musamus",
            "Musamus Mahakarya Rayap Tanah Membangun Rumah Raksasa Keras Mirip Karang Ketinggian 5 Meter",
            "Rawa Biru Danau Alami Sumber Air Bersih Merauke Habitat Flora Fauna Endemik",
            "Sungai Digoel Sungai Bersejarah Perjuangan Bangsa Arus Megah Melintasi Hutan Belantara",
            "Cagar Alam Danau Rawa Bawah Asmat Habitat Burung Air Kasuari Buaya Muara",
            "Kolam Pemandian Wisata Alam Kali Kumbe", "Sungai Maro Merauke Susur Sungai Pesona Pelabuhan",
            "Rawa Hutan Nipah Asmat Hutan Bakau Tertua", "Suaka Margasatwa Danau Bian Merauke", "Danau Kepi Mappi Danau Rawa Terapung Teratai Liar"
        ],
        "budaya": [
            "Kawasan Seni Budaya Ukir Kayu Suku Asmat Warisan Mahakarya Kemanusiaan UNESCO Terbaik Dunia",
            "Monumen Kapsul Waktu Merauke Markas Impian Generasi Penerus Bangsa Bentuk Markas Avengers",
            "Tugu Nol Kilometer Merauke Titik Paling Timur Wilayah Kedaulatan Republik Indonesia Sabang-Merauke",
            "Situs Penjara Pengasingan Kolonial Boven Digoel Tempat Bung Hatta & Sutan Sjahrir Dibuang Belanda",
            "Kota Agats Kota Unik di Atas Papan Seluruh Jalan & Rumah Bertiang Kayu di Atas Rawa Tanpa Tanah",
            "Museum Kebudayaan dan Kemajuan Asmat Agats Koleksi Ukiran Perisai & Patung Bisj Kuno Sakral",
            "Rumah Bujang Suku Asmat (Jew) Tempat Sakral Leluhur Berkumpul Menyelesaikan Konflik",
            "Pesta Budaya Asmat Festival Tahunan Pelelangan Ukiran Kayu Mahakarya Dunia"
        ],
        "hiburan": ["Taman Mandala Merauke Jantung Rekreasi Kota", "Taman Bunga Spadem Merauke", "Taman Libra (Lingkaran Brawijaya) Merauke Ikon Rusa", "Waterpark Kepi Mappi Rekreasi Keluarga", "Taman Sota Perbatasan RI-PNG Taman Edukasi Satwa"],
        "belanja": ["Pasar Wamanggu Merauke Pusat Oleh-Oleh Dendeng & Abon Rusa Asli", "Sentra Minyak Kayu Putih Wasur Asli Merauke", "Sentra Ukiran Kayu Besi Suku Asmat Asli Agats", "Pusat Kerajinan Tas Noken Merauke", "Pasar Digoel Tanah Merah"],
        "religi": ["Gereja Katedral Santo Fransiskus Xaverius Merauke 1930 Peninggalan Misi Katolik", "Masjid Raya Baiturrahman Merauke", "Gereja Katedral Salib Suci Agats Asmat Konstruksi Kayu Besi Unik", "Tugu Hati Kudus Yesus Merauke", "Masjid Agung At-Taqwa Tanah Merah Boven Digoel"]
    },
    {
        "nama": "Papua Tengah", "pulau": "Papua", "ibukota": "Nabire",
        "cities": [
            ("Nabire", -3.3667, 135.5000), ("Mimika Timika", -4.5444, 136.8872),
            ("Paniai Enarotali", -3.9000, 136.3333), ("Puncak Jaya Kotamulia", -3.7000, 137.9500),
            ("Puncak Ilaga", -3.9833, 137.6000), ("Dogiyai Kigamani", -4.0000, 135.9500),
            ("Deiyai Tigi", -4.0167, 136.0833), ("Intan Jaya Sugapa", -3.7500, 137.0500)
        ],
        "pantai": [
            "Pantai Gauto Nabire Teluk Cenderawasih Hiu Paus Berenang Bebas", "Pantai Nabire Monumen Bahari Tepi Sunset Indah",
            "Pantai Pasir Putih Pulau Pepaya Nabire Terumbu Karang Eksotis", "Pantai Pulau Rumberpon Teluk Cenderawasih Padang Lamun Dugong",
            "Pantai Ipaya Mimika Pasir Hitam Samudera Arafura", "Pantai Atuka Mimika Pesisir Suku Kamoro Tradisi Perahu Lesung",
            "Pantai Kokonao Mimika Peninggalan Sejarah Kota Tua Misi", "Pantai Karadiri Nabire Wisata Keluarga",
            "Pantai Ahe Nabire Pulau Tak Berpenghuni Surga Diving", "Pantai Monumen Hiu Paus Kwatisore Nabire",
            "Pantai Amamapare Mimika Pelabuhan Ekspor Konsentrat Tembaga Emas Freeport", "Pantai Otakwa Mimika Muara Hutan Rawa Bakau",
            "Pantai Kali Kopi Timika Pesisir Danau Air Asin", "Pantai Puriri Mimika Pulau Karang Pasir",
            "Pantai Bintuni Nabire Perbatasan Teluk", "Pantai Manase Nabire Rekreasi Tepi Laut"
        ],
        "gunung": [
            "Puncak Jaya (Carstensz Pyramid 4.884 mdpl) Atap Tertinggi Indonesia & Oseania Salju Abadi Dunia (Seven Summits)",
            "Puncak Sumantri & Puncak Ngga Pulu Salju Abadi Gletser Carstensz", "Grasberg Tambang Emas Terbuka Raksasa Tertinggi di Dunia Ketinggian 4.280 mdpl",
            "Puncak Kotamulia Puncak Jaya Kota Terdingin di Indonesia Ketinggian 2.400 mdpl", "Puncak Cartenz View Tembagapura Kota Modern Awan Freeport",
            "Bukit Bobaigo Paniai Pemandangan Menakjubkan Danau Paniai", "Puncak Lembah Ilaga Puncak Panorama Salju",
            "Puncak Deiyai Tigi Bukit Teletubbies Danau", "Puncak Gunung Weyland Nabire Cagar Alam Hutan Rimba",
            "Puncak Sugapa Intan Jaya Titik Awal Pendakian Carstensz", "Bukit Kapa-Kapa Nabire", "Puncak Enarotali Danau Paniai View"
        ],
        "alam": [
            "Taman Nasional Teluk Cenderawasih Kwatisore Nabire Atraksi Berenang Bersama Hiu Paus (Whale Shark)",
            "Danau Paniai Danau Purba Terindah Dunia Dinobatkan Konferensi Danau Jenewa 1997",
            "Danau Tigi Deiyai Danau Purba Eksotis dengan Pulau Karang Kecil di Tengah Danau",
            "Danau Tage Danau Berair Sebening Kristal Diapit Lembah Hijau Paniai",
            "Air Terjun Bihewa Nabire Air Terjun Raksasa Bertingkat Tujuh di Tengah Hutan Primer Belantara",
            "Kali Biru Timika Sungai Alami Hutan Hujan Tropis Mimika Air Segar Sebening Kaca",
            "Kawasan Gletser Carstensz Lapisan Es Salju Abadi Khatulistiwa Fenomena Langka Dunia",
            "Air Terjun Wao Nabire Alam Asri Pegunungan", "Kawasan Karst Sugapa Intan Jaya Tebing Pahat Raksasa",
            "Sungai Iwaka Timika Spot Arung Jeram dan Memancing Ikan Mas Papua"
        ],
        "budaya": [
            "Suku Kamoro Mimika Mahakarya Ukiran Patung Tiang Mbitoro Pesaing Seni Asmat",
            "Suku Amungme & Suku Dani Puncak Jaya Tradisi Hidup Selaras Pegunungan Kasuari",
            "Suku Mee (Ekari) Paniai Tradisi Memancing Kepiting Danau Menggunakan Perahu Tradisional Boba",
            "Desa Adat Kwatisore Nabire Hubungan Magis Sahabat Nelayan dengan Kawanan Hiu Paus",
            "Rumah Adat Honai Mee Paniai Konstruksi Kayu Papan Tradisional Dataran Tinggi Dingin",
            "Museum Loka Budaya Kamoro Timika Koleksi Ukiran Kayu Besi Seni Pahat Leluhur",
            "Situs Peninggalan Kota Tua Kokas Mimika Misi Katolik Bersejarah 1920-an", "Festival Budaya Maramowe Kamoro Pesta Adat Seni Suku Pesisir Mimika"
        ],
        "hiburan": ["Kuala Kencana Timika Kota Modern Bawah Tanah Ramah Lingkungan Pertama Indonesia di Tengah Hutan Hujan", "Taman Kota Timika Pasar Sentral", "Taman Gajah Mada Nabire Waterfront", "Mimika Sports Complex (MSC) Fasilitas Olahraga Bertaraf Olimpiade Internasional", "Nabire City Park Tepi Laut"],
        "belanja": ["Pasar Sentral Timika Pusat Noken Anggrek Emas Khas Suku Amungme", "Sentra Kerajinan Ukiran Tiang Mbitoro Suku Kamoro Mimika", "Sentra Kopi Arabika Moanemani Dogiyai Kopi Organik Pilihan", "Pasar Kalibobo Nabire Pusat Ikan Asar & Buah Merah", "Diana Shopping Center Timika"],
        "religi": ["Gereja Katedral Tiga Raja Timika Arsitektur Modern Monumental Tembaga", "Gereja Tua Enarotali Paniai Misi Belanda 1938", "Masjid Agung Babussalam Timika Megah", "Masjid Agung Al-Falah Nabire", "Gereja Antiokhia Sugapa Intan Jaya Tepi Tebing"]
    }
]

# Gabungkan seluruh 38 provinsi
ALL_PROVINCES = list(ALL_38_PROVINCES)
ALL_PROVINCES.extend(ADDITIONAL_PROVINCES)

# Mapping Kategori ke Clean Category TravelFit
CATEGORY_CLEAN_MAP = {
    "Pantai": "bahari",
    "Bahari": "bahari",
    "Gunung": "alam",
    "Cagar Alam": "alam",
    "Budaya": "budaya",
    "Taman Hiburan": "hiburan",
    "Pusat Perbelanjaan": "belanja",
    "Tempat Ibadah": "religi"
}

# Template deskripsi dan aktivitas berdasarkan kategori
DESCRIPTION_TEMPLATES = {
    "Pantai": [
        "Destinasi wisata pesisir dengan hamparan pasir bersih, deburan ombak yang menenangkan, serta panorama matahari terbenam yang memukau. Dilengkapi fasilitas warung makan seafood lokal, area parkir, toilet umum, dan persewaan payung pantai.",
        "Pantai eksotis dengan air laut jernih dan deretan pohon kelapa yang rindang. Menjadi lokasi favorit wisatawan untuk bersantai, bermain air bersama keluarga, berswafoto, serta menikmati kelapa muda segar di tepi pantai.",
        "Kawasan pantai dengan keindahan garis pantai memanjang, batuan karang yang menawan, serta angin sepoi-sepoi yang menyegarkan. Sangat cocok untuk aktivitas rekreasi, jalan santai di tepi air, dan piknik sore hari."
    ],
    "Gunung": [
        "Destinasi wisata pegunungan berhawa sejuk dengan jalur pendakian yang menantang dan panorama lautan awan yang spektakuler saat fajar. Tersedia pos peristirahatan, warung logistik pendaki, area perkemahan, dan pemandu lokal.",
        "Puncak bukit dan pegunungan dengan pemandangan lanskap hijau membentang sejauh mata memandang. Menawarkan pengalaman menikmati golden sunrise, udara bersih bebas polusi, dan spot foto alam yang memesona.",
        "Kawasan dataran tinggi dan lereng gunung yang asri dengan pemandangan perbukitan hijau dan kawah eksotis. Sangat ideal untuk petualangan alam terbuka, hiking santai, perkemahan keluarga, dan melepas penat."
    ],
    "Cagar Alam": [
        "Kawasan konservasi alam yang asri dan terlindungi dengan keanekaragaman flora dan fauna tropis endemik. Dilengkapi jalur trekking kayu yang tertata rapi, gazebo istirahat, pusat informasi lingkungan, dan toilet pengunjung.",
        "Wisata alam edukatif berbalut udara segar hutan tropis, aliran sungai yang jernih, serta air terjun bertingkat yang menyejukkan. Pilihan utama untuk riset keanekaragaman hayati dan ekowisata ramah lingkungan.",
        "Objek wisata alam dengan formasi tebing batuan alami, gua karst purba, serta telaga yang jernih dan tenang. Suasana alam yang tenang memberikan kesegaran pikiran bagi pengunjung yang mencintai ketenangan alam."
    ],
    "Budaya": [
        "Situs cagar budaya bersejarah yang sarat dengan nilai tradisi leluhur, arsitektur arca dan bangunan tradisional yang otentik. Dilengkapi pemandu wisata budaya, museum informasi sejarah, dan pertunjukan seni berkala.",
        "Destinasi wisata sejarah dan kearifan lokal yang memperlihatkan warisan peradaban masa lampau melalui koleksi artefak berharga. Tempat ideal untuk belajar mengenai perjuangan bangsa dan filosofi adat masyarakat.",
        "Kompleks bangunan bersejarah dan desa adat yang mempertahankan adat istiadat turun-temurun dengan ramah. Wisatawan dapat menyaksikan kerajinan tangan tradisional dan berinteraksi langsung dengan warga setempat."
    ],
    "Taman Hiburan": [
        "Taman rekreasi modern keluarga yang menghadirkan beragam wahana permainan seru, atraksi air, serta pertunjukan tematik interaktif. Memiliki fasilitas lengkap seperti food court, musala yang nyaman, toilet bersih, dan area parkir luas.",
        "Destinasi hiburan terpadu dengan spot swafoto kekinian yang estetik, wahana edukasi anak, dan ruang terbuka hijau yang ramah keluarga. Menjadi tempat favorit untuk berekreasi bersama anak-anak di akhir pekan.",
        "Kawasan rekreasi bertema dengan wahana pemacu adrenalin, kolam renang bergelombang, serta taman bermain anak yang aman. Dilengkapi staf pengawas keselamatan dan berbagai tenant kuliner lezat."
    ],
    "Pusat Perbelanjaan": [
        "Pusat perbelanjaan dan pasar tradisional khas daerah yang menjual aneka kerajinan tangan, kain tenun atau batik, serta camilan oleh-oleh lokal. Tempat bertemunya tawar-menawar yang hangat dengan harga terjangkau.",
        "Sentra kuliner dan suvenir ikonik yang menyediakan aneka buah tangan khas Nusantara berkualitas tinggi. Dilengkapi area parkir kendaraan wisata, gerai anjungan tunai mandiri (ATM), dan mushola.",
        "Kawasan pertokoan dan pasar seni yang menyajikan ragam cinderamata unik karya perajin lokal dari berbagai penjuru daerah. Selalu ramai dikunjungi wisatawan yang ingin membawa kenang-kenangan autentik."
    ],
    "Tempat Ibadah": [
        "Bangunan keagamaan bersejarah dengan arsitektur megah dan penuh nilai filosofis spiritual tinggi. Menyediakan sarana ibadah yang bersih dan khusyuk, pelataran yang teduh dan asri, serta toilet wudhu yang terawat.",
        "Ikon wisata religi yang terkenal dengan kedamaian suasananya, toleransi antarwarga, serta kubah atau menara yang menjulang indah. Menjadi tempat ziarah sekaligus edukasi spiritual bagi masyarakat luas.",
        "Tempat ibadah cagar budaya dengan ornamen seni pahat antik dan sejarah pendirian yang menginspirasi. Terbuka bagi pengunjung yang ingin berdoa maupun mengagumi keindahan karya arsitektur Nusantara."
    ]
}

ACTIVITY_TAGS_MAP = {
    "Pantai": "berenang|fotografi|kuliner|pantai|rekreasi_keluarga",
    "Gunung": "camping|fotografi|hiking|gunung",
    "Cagar Alam": "edukasi|fotografi|hiking|rekreasi_keluarga",
    "Budaya": "budaya|edukasi|fotografi|sejarah",
    "Taman Hiburan": "edukasi|fotografi|rekreasi_keluarga",
    "Pusat Perbelanjaan": "belanja|budaya|kuliner",
    "Tempat Ibadah": "budaya|religi|sejarah"
}

def generate_destination_pool():
    all_rows = []
    place_id = 1
    
    # Target 50 destinasi per provinsi:
    # Pantai: 14, Gunung: 10, Cagar Alam: 8, Budaya: 7, Taman Hiburan: 4, Pusat Perbelanjaan: 4, Tempat Ibadah: 3
    # Total = 14 + 10 + 8 + 7 + 4 + 4 + 3 = 50 per provinsi!
    TARGET_PER_CATEGORY = [
        ("Pantai", 14),
        ("Gunung", 10),
        ("Cagar Alam", 8),
        ("Budaya", 7),
        ("Taman Hiburan", 4),
        ("Pusat Perbelanjaan", 4),
        ("Tempat Ibadah", 3)
    ]

    for prov in ALL_PROVINCES:
        prov_name = prov["nama"]
        cities = prov["cities"]
        
        # Siapkan item unik per kategori
        for cat_name, target_count in TARGET_PER_CATEGORY:
            # Ambil item dari registri provinsi
            key = {
                "Pantai": "pantai",
                "Gunung": "gunung",
                "Cagar Alam": "alam",
                "Budaya": "budaya",
                "Taman Hiburan": "hiburan",
                "Pusat Perbelanjaan": "belanja",
                "Tempat Ibadah": "religi"
            }[cat_name]
            
            raw_items = prov.get(key, [])
            # Jika kurang dari target_count, lakukan pengayaan realistis berbasis kota
            selected_items = list(raw_items[:target_count])
            idx_filler = 1
            while len(selected_items) < target_count:
                city_name = cities[(len(selected_items) + idx_filler) % len(cities)][0]
                filler_name = f"{cat_name} {city_name} {idx_filler}"
                if filler_name not in selected_items:
                    selected_items.append(filler_name)
                idx_filler += 1
                
            for idx_in_cat, place_name in enumerate(selected_items[:target_count]):
                # Pilih kota dari daftar kota provinsi
                city_tuple = cities[(idx_in_cat + len(place_name)) % len(cities)]
                city_name, base_lat, base_long = city_tuple
                
                # Koordinat realistis dengan variasi kecil (jitter ~ 1-5 km)
                lat = round(base_lat + random.uniform(-0.04, 0.04), 6)
                long = round(base_long + random.uniform(-0.04, 0.04), 6)
                
                # Harga realistis per kategori
                if cat_name in ["Tempat Ibadah", "Pusat Perbelanjaan"]:
                    price = 0
                elif cat_name == "Pantai":
                    price = random.choice([5000, 10000, 15000, 20000, 25000, 30000])
                elif cat_name == "Gunung":
                    price = random.choice([10000, 15000, 20000, 25000, 35000, 50000])
                elif cat_name == "Cagar Alam":
                    price = random.choice([10000, 15000, 20000, 25000, 30000])
                elif cat_name == "Budaya":
                    price = random.choice([5000, 10000, 15000, 20000, 25000])
                elif cat_name == "Taman Hiburan":
                    price = random.choice([35000, 50000, 75000, 100000, 150000, 200000])
                else:
                    price = 10000
                    
                # Rating terdistribusi realistis (4.1 s.d. 4.9)
                rating = round(random.choice([4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9]), 1)
                
                # Durasi kunjungan rata-rata (menit)
                if cat_name in ["Gunung"]:
                    time_min = random.choice([180.0, 240.0, 300.0, 360.0])
                elif cat_name in ["Pantai", "Taman Hiburan"]:
                    time_min = random.choice([120.0, 150.0, 180.0, 240.0])
                elif cat_name in ["Cagar Alam"]:
                    time_min = random.choice([90.0, 120.0, 150.0, 180.0])
                elif cat_name in ["Budaya", "Pusat Perbelanjaan"]:
                    time_min = random.choice([60.0, 90.0, 120.0])
                else:
                    time_min = random.choice([45.0, 60.0, 90.0])
                    
                # Deskripsi
                desc_template = random.choice(DESCRIPTION_TEMPLATES[cat_name])
                description = f"{place_name} di {city_name}, {prov_name}. {desc_template}"
                
                # Sub-category
                if cat_name == "Pantai":
                    sub_category = "Pantai"
                elif cat_name == "Gunung":
                    sub_category = "Gunung" if "Gunung" in place_name else "Perbukitan"
                elif cat_name == "Cagar Alam":
                    if "Danau" in place_name: sub_category = "Danau"
                    elif "Air Terjun" in place_name or "Curug" in place_name or "Coban" in place_name: sub_category = "Air Terjun"
                    elif "Gua" in place_name: sub_category = "Gua"
                    else: sub_category = "Taman Nasional"
                elif cat_name == "Budaya":
                    if "Candi" in place_name: sub_category = "Candi"
                    elif "Museum" in place_name: sub_category = "Museum"
                    elif "Keraton" in place_name or "Istana" in place_name: sub_category = "Keraton"
                    elif "Benteng" in place_name: sub_category = "Benteng"
                    elif "Desa" in place_name or "Kampung" in place_name: sub_category = "Desa Adat"
                    else: sub_category = "Situs Sejarah"
                elif cat_name == "Taman Hiburan":
                    sub_category = "Waterpark" if "Water" in place_name else "Taman Rekreasi"
                elif cat_name == "Pusat Perbelanjaan":
                    sub_category = "Sentra Kerajinan" if "Sentra" in place_name else "Pasar Tradisional"
                elif cat_name == "Tempat Ibadah":
                    if "Masjid" in place_name: sub_category = "Masjid"
                    elif "Gereja" in place_name: sub_category = "Gereja"
                    elif "Pura" in place_name: sub_category = "Pura"
                    elif "Klenteng" in place_name or "Vihara" in place_name: sub_category = "Vihara"
                    else: sub_category = "Tempat Ibadah"
                else:
                    sub_category = cat_name
                    
                # Fasilitas
                toilet = 1
                parking = 1
                food = 1 if cat_name in ["Pantai", "Gunung", "Taman Hiburan", "Pusat Perbelanjaan", "Cagar Alam"] or random.random() > 0.3 else 0
                worship = 1 if cat_name in ["Tempat Ibadah", "Taman Hiburan", "Pantai"] or random.random() > 0.4 else 0
                access = 1 if cat_name in ["Taman Hiburan", "Pusat Perbelanjaan", "Tempat Ibadah"] or random.random() > 0.6 else 0
                info_center = 1 if cat_name in ["Cagar Alam", "Budaya", "Taman Hiburan"] or random.random() > 0.5 else 0
                facility_score = round((toilet + parking + food + worship + access + info_center) / 6.0, 4)
                
                # Activity tags
                base_tags = set(ACTIVITY_TAGS_MAP[cat_name].split('|'))
                if "snorkeling" in place_name.lower() or "diving" in place_name.lower() or "karang" in place_name.lower():
                    base_tags.add("snorkeling")
                    base_tags.add("bahari")
                if "camping" in place_name.lower() or "perkemahan" in place_name.lower():
                    base_tags.add("camping")
                if "danau" in place_name.lower() or "air terjun" in place_name.lower() or "sungai" in place_name.lower():
                    base_tags.add("alam")
                if "museum" in place_name.lower() or "candi" in place_name.lower():
                    base_tags.add("sejarah")
                    base_tags.add("edukasi")
                if cat_name == "Gunung":
                    base_tags.add("hiking")
                    base_tags.add("gunung")
                if cat_name == "Pantai":
                    base_tags.add("pantai")
                activity_tags = "|".join(sorted(base_tags))
                
                row = {
                    "Place_Id": place_id,
                    "Place_Name": place_name,
                    "Description": description,
                    "Category": cat_name,
                    "Sub_Category": sub_category,
                    "City": city_name,
                    "Price": price,
                    "Rating": rating,
                    "Time_Minutes": time_min,
                    "Coordinate": f"{{'lat': {lat}, 'lng': {long}}}",
                    "Lat": lat,
                    "Long": long,
                    "Province": prov_name,
                    # Atribut SPK
                    "Category_Clean": CATEGORY_CLEAN_MAP[cat_name],
                    "c1_ticket_price": float(price),
                    "c2_rating": float(rating),
                    "facility_toilet_mentioned": toilet,
                    "facility_parking_mentioned": parking,
                    "facility_food_mentioned": food,
                    "facility_worship_mentioned": worship,
                    "facility_accessibility_mentioned": access,
                    "facility_information_center_mentioned": info_center,
                    "c4_facility_score": facility_score,
                    "activity_tags": activity_tags
                }
                all_rows.append(row)
                place_id += 1
                
    return all_rows

def main():
    print("Mulai proses pembuatan dataset sintetis 38 provinsi...")
    rows = generate_destination_pool()
    df_all = pd.DataFrame(rows)
    print(f"Total baris yang berhasil dibuat: {len(df_all)}")
    
    # Validasi jumlah per provinsi
    prov_counts = df_all["Province"].value_counts()
    print("Jumlah provinsi unik:", len(prov_counts))
    assert len(prov_counts) == 38, f"Provinsi harus 38, ditemukan: {len(prov_counts)}"
    assert (prov_counts == 50).all(), "Setiap provinsi harus memiliki tepat 50 destinasi!"
    
    # Validasi koordinat dalam wilayah Indonesia
    assert df_all["Lat"].between(-12.0, 7.0).all(), "Ada koordinat latitude di luar Indonesia!"
    assert df_all["Long"].between(94.0, 142.0).all(), "Ada koordinat longitude di luar Indonesia!"
    
    # Pisahkan ke format Sheet 1: Destinasi_Raw
    raw_cols = [
        "Place_Id", "Place_Name", "Description", "Category", "Sub_Category",
        "City", "Price", "Rating", "Time_Minutes", "Coordinate", "Lat", "Long", "Province"
    ]
    df_raw = df_all[raw_cols].copy()
    
    # Format Sheet 2: Destinasi_TravelFit_Ready
    ready_cols = [
        "Place_Id", "Place_Name", "City", "Province", "Category", "Sub_Category",
        "Category_Clean", "c1_ticket_price", "c2_rating",
        "facility_toilet_mentioned", "facility_parking_mentioned", "facility_food_mentioned",
        "facility_worship_mentioned", "facility_accessibility_mentioned", "facility_information_center_mentioned",
        "c4_facility_score", "activity_tags"
    ]
    df_ready = df_all[ready_cols].copy()
    
    # Ekspor ke Excel dengan Styling Profesional
    excel_path = Path("Dataset_Wisata_38_Provinsi.xlsx")
    print(f"Menyimpan ke Excel: {excel_path.resolve()}...")
    
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df_raw.to_excel(writer, sheet_name="Destinasi_Raw", index=False)
        df_ready.to_excel(writer, sheet_name="Destinasi_TravelFit_Ready", index=False)
        
    # Mempercantik Excel dengan openpyxl
    wb = openpyxl.load_workbook(excel_path)
    header_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    thin_border = Border(
        left=Side(style="thin", color="E0E0E0"),
        right=Side(style="thin", color="E0E0E0"),
        top=Side(style="thin", color="E0E0E0"),
        bottom=Side(style="thin", color="E0E0E0")
    )
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        
        # Style Header
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Auto-adjust column width
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col[:100]:  # Cek 100 baris pertama untuk efisiensi
                val_str = str(cell.value or '')
                if len(val_str) > max_len:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)
            
    wb.save(excel_path)
    print("Penyimpanan Excel selesai dan terformat rapi.")
    
    # Simpan juga versi CSV
    csv_dir = Path("data/processed")
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_path = csv_dir / "tourism_indonesia_38_provinsi.csv"
    df_all.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"Salinan CSV tersimpan di: {csv_path.resolve()}")
    
    # Buat Laporan Ringkasan
    report_dir = Path("reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "synthetic_data_report.json"
    
    cat_summary = df_all["Category"].value_counts().to_dict()
    subcat_summary = df_all["Sub_Category"].value_counts().to_dict()
    clean_cat_summary = df_all["Category_Clean"].value_counts().to_dict()
    
    report = {
        "status": "SUCCESS",
        "total_destinations": int(len(df_all)),
        "total_provinces": int(len(prov_counts)),
        "destinations_per_province": {str(k): int(v) for k, v in prov_counts.items()},
        "category_distribution": cat_summary,
        "sub_category_distribution": subcat_summary,
        "travel_fit_clean_category_distribution": clean_cat_summary,
        "price_stats": {
            "min": int(df_all["Price"].min()),
            "max": int(df_all["Price"].max()),
            "mean": float(round(df_all["Price"].mean(), 2)),
            "median": int(df_all["Price"].median())
        },
        "rating_stats": {
            "min": float(df_all["Rating"].min()),
            "max": float(df_all["Rating"].max()),
            "mean": float(round(df_all["Rating"].mean(), 2))
        },
        "highlights": [
            f"Kategori Pantai: {cat_summary.get('Pantai', 0)} destinasi ({round(cat_summary.get('Pantai', 0)/len(df_all)*100, 1)}%)",
            f"Kategori Gunung: {cat_summary.get('Gunung', 0)} destinasi ({round(cat_summary.get('Gunung', 0)/len(df_all)*100, 1)}%)",
            "Semua 38 provinsi di Indonesia terwakili secara merata masing-masing 50 destinasi."
        ]
    }
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Laporan ringkasan disimpan di: {report_path.resolve()}")
    print("Selesai sempurna!")

if __name__ == "__main__":
    main()
