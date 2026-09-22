"""
Database Lengkap 38 Provinsi Indonesia untuk Dataset Pariwisata TravelFit.
Memuat metadata geografis, kabupaten/kota autentik, dan daftar destinasi nyata
mencakup Pantai, Gunung, Cagar Alam, Bahari, Budaya, Taman Hiburan, Pusat Perbelanjaan, dan Tempat Ibadah.
"""

ALL_38_PROVINCES = [
    # ==================== 1. SUMATERA (10 PROVINSI) ====================
    {
        "nama": "Aceh", "pulau": "Sumatera", "ibukota": "Banda Aceh",
        "cities": [
            ("Kota Banda Aceh", 5.5483, 95.3238), ("Kota Sabang", 5.8933, 95.3167),
            ("Aceh Besar", 5.3833, 95.5167), ("Aceh Tengah", 4.6283, 96.8453),
            ("Aceh Barat", 4.4500, 96.1667), ("Aceh Selatan", 3.2500, 97.2500),
            ("Bener Meriah", 4.7333, 96.8667), ("Aceh Jaya", 4.7833, 95.6333),
            ("Aceh Singkil", 2.3333, 97.8000), ("Kota Lhokseumawe", 5.1800, 97.1400)
        ],
        "pantai": [
            "Pantai Lampuuk", "Pantai Iboih Sabang", "Pantai Lhoknga", "Pantai Ujong Batee",
            "Pantai Pasir Putih Lhok Me", "Pantai Sumur Tiga", "Pantai Anoi Itam", "Pantai Ujong Kareung",
            "Pantai Suak Ribee", "Pantai Batee Puteh", "Pantai Kuala Merisi", "Pantai Gapang Sabang",
            "Pantai Alue Naga", "Pantai Lange", "Pantai Kasih Sabang", "Pantai Pasir Putih Kuala Panga"
        ],
        "gunung": [
            "Gunung Burni Telong", "Gunung Leuser (TNGL)", "Gunung Seulawah Agam", "Gunung Seulawah Inong",
            "Gunung Geureudong", "Gunung Abong-Abong", "Gunung Peuet Sago", "Puncak Burni Kelieten",
            "Puncak Pantan Terong Takengon", "Bukit Cot Panglima", "Bukit Lamreh", "Bukit Teletubbies Blang Bintang"
        ],
        "alam": [
            "Danau Laut Tawar", "Air Terjun Suhom", "Air Terjun Blang Kolam", "Air Terjun Tansaran Bidin",
            "Gua Sarang Pulau Weh", "Pemandian Air Panas Ie Suum", "Taman Hutan Raya Pocut Meurah Intan",
            "Ekowisata Hutan Mangrove Langsa", "Pulo Aceh", "Kuala Merisi Jaya"
        ],
        "budaya": [
            "Museum Tsunami Aceh", "Tugu Nol Kilometer Indonesia", "Rumah Cut Nyak Dhien",
            "Taman Sari Gunongan", "Benteng Anoi Itam", "Museum Aceh", "Makam Sultan Iskandar Muda",
            "Pusat Kerajinan Rencong Baet", "Desa Wisata Lubok Sukon"
        ],
        "hiburan": ["Taman Ratu Safiatuddin", "Taman Bustanussalatin", "Waterpark Taman Impian", "Kolam Mata Ie", "Taman Krueng Daroy"],
        "belanja": ["Pasar Atjeh Banda Aceh", "Pusat Oleh-Oleh Kopi Ulee Kareng", "Sentra Souvenir Peunayong", "Pasar Buah Puncak Gayo", "Sentra Bordir Kasab"],
        "religi": ["Masjid Raya Baiturrahman", "Masjid Rahmatullah Lampuuk", "Masjid Tuha Indrapuri", "Masjid Islamic Center Lhokseumawe", "Makam Teuku Cik Di Tiro"]
    },
    {
        "nama": "Sumatera Utara", "pulau": "Sumatera", "ibukota": "Medan",
        "cities": [
            ("Kota Medan", 3.5952, 98.6722), ("Samosir", 2.6333, 98.7167),
            ("Karo", 3.1167, 98.5000), ("Toba", 2.3833, 99.0667),
            ("Nias Selatan", 0.7667, 97.7500), ("Langkat", 3.7500, 98.2500),
            ("Simalungun", 2.9500, 99.0000), ("Tapanuli Tengah", 1.8833, 98.6667),
            ("Deli Serdang", 3.4833, 98.7000), ("Kota Pematangsiantar", 2.9600, 99.0600)
        ],
        "pantai": [
            "Pantai Sorake Nias", "Pantai Lagundri", "Pantai Pasir Putih Parbaba Samosir", "Pantai Batu Hoda",
            "Pantai Pandan Sibolga", "Pantai Bosur Tapanuli", "Pantai Cermin Theme Park", "Pantai Romance Bay",
            "Pantai Sigurgur Samosir", "Pantai Lumban Bulbul Balige", "Pantai Bintang Lagundri", "Pantai Tureloto Laut Mati Nias",
            "Pantai Muara Indah Deli", "Pantai Bali Lestari Serdang", "Pantai Sialang Buah", "Pantai Pondok Permai"
        ],
        "gunung": [
            "Gunung Sibayak Berastagi", "Gunung Sinabung", "Gunung Sibuatan", "Gunung Pusuk Buhit Samosir",
            "Bukit Gundaling Berastagi", "Bukit Holbung Samosir", "Bukit Sibea-bea", "Puncak 2000 Siosar",
            "Bukit Gajah Bobok", "Bukit Siadtaratas Silalahi", "Puncak Tarabunga Balige", "Gunung Sorik Marapi"
        ],
        "alam": [
            "Danau Toba (Parapat)", "Air Terjun Sipiso-piso", "Taman Wisata Alam Tangkahan", "Bukit Lawang Ekowisata Orangutan",
            "Air Terjun Sigura-gura", "Air Terjun Ponot Asahan", "Pemandian Air Panas Aek Rangat", "Danau Lau Kawar",
            "Kawah Putih Dolok Tinggi Raja", "Air Terjun Efrata Samosir"
        ],
        "budaya": [
            "Istana Maimun Medan", "Desa Adat Tomok Samosir", "Desa Bawomataluo Nias (Lompat Batu)", "Museum TB Silalahi Center",
            "Perkampungan Batu Huta Siallagan", "Tjong A Fie Mansion", "Makam Raja Sidabutar", "Museum Negeri Sumatera Utara"
        ],
        "hiburan": ["Mikie Funland Berastagi", "Rahmat International Wildlife Museum", "Taman Hewan Pematang Siantar", "The Le Hu Garden Deli", "Hairos Water Park Medan"],
        "belanja": ["Pajak Ikan Lama Medan", "Pusat Oleh-Oleh Bolu Meranti", "Sentra Bika Ambon Zulaikha", "Pasar Buah Berastagi", "Sentra Ulos Batak Silalahi"],
        "religi": ["Masjid Raya Al-Mashun Medan", "Salib Kasih Siatas Barita Tarutung", "Maha Vihara Maitreya Cemara Asri", "Graha Maria Annai Velangkanni", "Masjid Azizi Langkat"]
    },
    {
        "nama": "Sumatera Barat", "pulau": "Sumatera", "ibukota": "Padang",
        "cities": [
            ("Kota Padang", -0.9471, 100.4172), ("Kota Bukittinggi", -0.3056, 100.3692),
            ("Tanah Datar", -0.4500, 100.5833), ("Pesisir Selatan", -1.3500, 100.5667),
            ("Agam", -0.2500, 100.1667), ("Lima Puluh Kota", -0.0500, 100.6500),
            ("Kepulauan Mentawai", -2.0000, 99.6000), ("Solok", -0.8000, 100.6500),
            ("Kota Sawahlunto", -0.6800, 100.7800), ("Kota Payakumbuh", -0.2200, 100.6300)
        ],
        "pantai": [
            "Pantai Air Manis Malin Kundang", "Pantai Padang Taplau", "Pantai Pasumpahan",
            "Pantai Carocok Painan", "Pantai Sikele Mentawai", "Pantai Kata Pariaman", "Pantai Gandoriah",
            "Pantai Nirwana Padang", "Pantai Carolina Bungus", "Pantai Pagai Mentawai",
            "Pantai Sipora Surfing Mentawai", "Pantai Muaro Bikuang", "Pantai Tiku Agam", "Pantai Sasak Pasaman",
            "Pantai Arga Indah", "Pantai Suwarnadwipa"
        ],
        "gunung": [
            "Gunung Marapi", "Gunung Singgalang", "Gunung Talang", "Gunung Talamau",
            "Puncak Lawang Maninjau", "Puncak Mandeh Pesisir", "Bukit Langkisau Painan", "Puncak Kelok Sembilan",
            "Bukit Nobita Padang", "Bukit Harau", "Puncak Gagoan Solok", "Gunung Sago Payakumbuh"
        ],
        "alam": [
            "Lembah Harau", "Danau Maninjau", "Danau Singkarak", "Danau Kembar Diatas dan Dibawah",
            "Ngarai Sianok Bukittinggi", "Kawasan Bahari Mandeh", "Air Terjun Lembah Anai",
            "Danau Tarusan Kamang", "Gua Ngalau Indah", "Air Terjun Sarasah Ulu Gadut"
        ],
        "budaya": [
            "Jam Gadang Bukittinggi", "Istano Basa Pagaruyung", "Desa Adat Nagari Pariangan",
            "Lubang Jepang Bukittinggi", "Rumah Kelahiran Buya Hamka", "Tambang Batubara Ombilin Sawahlunto",
            "Museum Kereta Api Sawahlunto", "Rumah Gadang 21 Ruang Solok"
        ],
        "hiburan": ["Taman Margasatwa Kinantan Bukittinggi", "Mifan Waterpark Padang Panjang", "Taman Panorama Bukittinggi", "Harau Sky Park", "Green Marsawa Park"],
        "belanja": ["Pasar Atas Bukittinggi", "Sentra Keripik Balado Christine Hakim", "Pusat Tenun Pandai Sikek", "Sentra Songket Silungkang", "Pasar Raya Padang"],
        "religi": ["Masjid Raya Sumatera Barat", "Masjid Asasi Sigando Padang Panjang", "Masjid Tuo Kayu Jao Solok", "Masjid Raya Bayur Maninjau", "Masjid Jami Bingkudu Agam"]
    },
    {
        "nama": "Riau", "pulau": "Sumatera", "ibukota": "Pekanbaru",
        "cities": [
            ("Kota Pekanbaru", 0.5071, 101.4478), ("Siak", 0.8000, 102.0500),
            ("Kampar", 0.3333, 101.0500), ("Pelalawan", 0.3800, 102.1000),
            ("Bengkalis", 1.4667, 102.1333), ("Rokan Hulu", 0.8800, 100.5000),
            ("Kota Dumai", 1.6667, 101.4500), ("Indragiri Hilir", -0.3300, 103.1500),
            ("Indragiri Hulu", -0.5500, 102.3000), ("Kuantan Singingi", -0.5000, 101.4500)
        ],
        "pantai": [
            "Pantai Rupat Utara Bengkalis", "Pantai Selat Baru", "Pantai Marina Dumai", "Pantai Koneng Dumai",
            "Pantai Solop Tembilahan", "Pantai Puak Teluk Makmur", "Pantai Ketapang Rupat",
            "Pantai Tanjung Lapin", "Pantai Teluk Rhu", "Pantai Medang Deras", "Pantai Alohong", "Pantai Pasir Putih Tualang",
            "Pantai Tanjung Medang", "Pantai Makeruh Rupat", "Pantai Cinta Teluk Jering", "Pantai Dermaga Dumai"
        ],
        "gunung": [
            "Puncak Bukit Suligi Rokan Hulu", "Bukit Naang Bangkinang", "Bukit Betabuh Kuansing",
            "Bukit Tiga Puluh (TNBT)", "Puncak Pukatan Kampar", "Bukit Condong Inhu", "Bukit Rimbang Baling",
            "Bukit Tabur Kampar", "Puncak Pematang Pangean", "Bukit Selancang", "Bukit Susun Rokan", "Bukit Perhentian Raja"
        ],
        "alam": [
            "Ombak Bono Sungai Kampar", "Taman Nasional Tesso Nilo", "Danau Buatan Lembah Sari Pekanbaru",
            "Air Terjun Aek Martua", "Danau PLTA Koto Panjang", "Air Terjun Batang Kapas",
            "Ekowisata Hutan Mangrove Dumai", "Air Terjun Guruh Gemurai", "Rawa Bento Siak", "Danau Naga Sakti Siak"
        ],
        "budaya": [
            "Istana Siak Sri Indrapura", "Candi Muara Takus Kampar", "Rumah Singgah Tuan Kadi Pekanbaru",
            "Museum Sang Nila Utama", "Balai Kerapatan Tinggi Siak", "Benteng Tujuh Lapis Dalu-Dalu",
            "Arena Perahu Jalur Kuantan Singingi", "Desa Adat Petalangan Pelalawan"
        ],
        "hiburan": ["Labersa Riau Fantasi Waterpark", "Asia Farm Hayday Pekanbaru", "Taman Rekreasi Alam Mayang", "Stanum Bangkinang Park", "Rainbow Hills Rumbai"],
        "belanja": ["Pasar Bawah Pekanbaru", "Sentra Bolu Kemojo Al-Mahdi", "Sentra Keripik Nanas Tambang", "Pusat Tenun Siak Songket", "Pasar Kodim Pekanbaru"],
        "religi": ["Masjid Agung An-Nur Riau", "Masjid Raya Syahabuddin Siak", "Masjid Raya Senapelan Pekanbaru", "Masjid Islamic Center Pasir Pengaraian", "Kelenteng Jin De Bao Bengkalis"]
    },
    {
        "nama": "Kepulauan Riau", "pulau": "Sumatera", "ibukota": "Tanjung Pinang",
        "cities": [
            ("Kota Batam", 1.1301, 104.0529), ("Kota Tanjung Pinang", 0.9167, 104.4500),
            ("Bintan", 1.1500, 104.5500), ("Karimun", 0.9833, 103.4333),
            ("Natuna", 3.9000, 108.2500), ("Kepulauan Anambas", 3.1000, 106.2500),
            ("Lingga", -0.2000, 104.6000)
        ],
        "pantai": [
            "Pantai Trikora Bintan", "Pantai Nongsa Batam", "Pantai Melur Pulau Galang", "Pantai Lagoi Bay Bintan",
            "Pantai Mirota Batam", "Pantai Pelawan Karimun", "Pantai Batu Kasah Natuna", "Pantai Padang Melang Anambas",
            "Pantai Senggiling Bintan", "Pantai Tanjung Siambang", "Pantai Viovio Batam", "Pantai Tanjung Pinggir Batam",
            "Pantai Piugus Anambas", "Pantai Sisi Serasan Natuna", "Pantai Pasir Panjang Lingga", "Pantai Cemaga Natuna"
        ],
        "gunung": [
            "Gunung Bintan", "Gunung Ranai Natuna", "Gunung Daik Lingga", "Bukit Senyum Batam",
            "Bukit Kursi Pulau Penyengat", "Puncak Bukit Gajah Natuna", "Bukit Tengkorak Karimun", "Puncak Cengkeh Natuna",
            "Bukit Pasir Busung Bintan", "Bukit Matak Anambas", "Bukit Manuk Tarempa", "Bukit Pelawan Karimun"
        ],
        "alam": [
            "Gurun Pasir Telaga Biru Busung", "Danau Biru Kawal Bintan", "Lagoi Crystal Lagoon",
            "Taman Bawah Laut Pulau Abang Batam", "Alif Stone Park Natuna", "Cagar Konservasi Pulau Bawah Anambas",
            "Air Terjun Ciklat Lingga", "Air Terjun Temburun Anambas", "Batu Lepe Anambas", "Pulau Ranoh Batam"
        ],
        "budaya": [
            "Jembatan Barelang Batam", "Pulau Penyengat Warisan Melayu", "Museum Sultan Sulaiman Badrul Alamsyah",
            "Maha Vihara Duta Maitreya Batam", "Kamp Pengungsi Vietnam Pulau Galang", "Istana Kantor Pulau Penyengat",
            "Benteng Bukit Kursi", "Gedung Mesiu Penyengat"
        ],
        "hiburan": ["Treasure Bay Bintan", "Mega Wisata Ocarina Batam", "Batam Wakepark", "Sea Forest Adventure Batam", "Bintan Desert Safari Park"],
        "belanja": ["Nagoya Hill Shopping Mall Batam", "Mega Mall Batam Centre", "Pasar Wisata Tanjung Pinang", "Sentra Kerupuk Gonggong Bintan", "BCS Mall Batam"],
        "religi": ["Masjid Raya Sultan Riau Penyengat", "Masjid Sultan Mahmud Riayat Syah Batam", "Vihara Ksitigarbha Bodhisattva (1000 Patung)", "Gereja Ayam Tanjung Pinang", "Masjid Agung Natuna"]
    },
    {
        "nama": "Jambi", "pulau": "Sumatera", "ibukota": "Jambi",
        "cities": [
            ("Kota Jambi", -1.6101, 103.6131), ("Kerinci", -2.0833, 101.5000),
            ("Kota Sungai Penuh", -2.0667, 101.4000), ("Merangin", -2.2500, 102.2000),
            ("Sarolangun", -2.3000, 102.6500), ("Batanghari", -1.7500, 103.1000),
            ("Muaro Jambi", -1.5500, 103.8000), ("Tanjung Jabung Barat", -1.1000, 103.3500),
            ("Tanjung Jabung Timur", -1.2500, 103.8500), ("Bungo", -1.5000, 102.0000)
        ],
        "pantai": [
            "Pantai Cemara Habitat Burung Migran", "Pantai Pasir Pandak Nipah Panjang", "Pantai Babussalam Kuala Tungkal",
            "Pantai Air Hitam Laut", "Pantai Kampung Laut", "Pantai Tanjung Solok", "Pantai Sungai Itik Sadu",
            "Pantai Kuala Jambi", "Pantai Teluk Majelis", "Pantai Alahan Panjang", "Pantai Remau Bako", "Pantai Lambur Luar",
            "Pantai Pangkal Duri", "Pantai Mendahara", "Pantai Teluk Nilau", "Pantai Kayu Aro Tanjab"
        ],
        "gunung": [
            "Gunung Kerinci (Puncak Tertinggi 3.805 mdpl)", "Gunung Kunyit Belerang Alami", "Gunung Masurai Merangin",
            "Bukit Khayangan Sungai Penuh", "Gunung Tujuh Kerinci", "Bukit Tapan Kerinci", "Puncak Danau Belibis",
            "Bukit Cinta Kerinci", "Bukit Ngalau Merangin", "Puncak Rawa Bento", "Bukit Selasih Sarolangun", "Bukit Rayo Bungo"
        ],
        "alam": [
            "Danau Gunung Tujuh", "Danau Kaco Bercahaya Biru", "Danau Kerinci", "Geopark Merangin Fosil Purba",
            "Taman Nasional Bukit Duabelas", "Rawa Bento Amazon Kerinci", "Air Terjun Telun Berasap",
            "Kebun Teh Kayu Aro Tertua", "Gua Tiangko Merangin", "Air Terjun Tumbukan Tebing"
        ],
        "budaya": [
            "Kompleks Percandian Muaro Jambi", "Jembatan Pedestrian Gentala Arasy", "Museum Siginjai Jambi",
            "Rumah Batu Olak Kemang", "Desa Adat Lempur Kerinci", "Makam Orang Kayo Hitam", "Desa Wisata Muara Jangga",
            "Candi Gumpung Muaro Jambi"
        ],
        "hiburan": ["Taman Rimba Zoo Jambi", "Kampoeng Radja Jambi", "Taman Wisata Air Kito", "Jambi Paradise", "Taman Bunga Hesti Garden"],
        "belanja": ["Pasar Angso Duo Jambi", "Sentra Batik Jambi Sebrang", "Sentra Kopi Arabika Kerinci", "Sentra Dodol Kentang Siulak", "Jambi Town Square"],
        "religi": ["Masjid Agung Al-Falah Seribu Tiang", "Menara Gentala Arasy Jambi", "Masjid Keramat Pulau Tengah Kerinci", "Masjid Agung Pondok Tinggi", "Klenteng Siu San Keng Jambi"]
    },
    {
        "nama": "Sumatera Selatan", "pulau": "Sumatera", "ibukota": "Palembang",
        "cities": [
            ("Kota Palembang", -2.9909, 104.7565), ("Kota Pagar Alam", -4.0167, 103.2667),
            ("Lahat", -3.7833, 103.5333), ("Muara Enim", -3.6500, 103.7833),
            ("OKU Baturaja", -4.1333, 104.1667), ("Banyuasin", -2.8833, 104.3833),
            ("Ogan Ilir", -3.4333, 104.6500), ("Kota Prabumulih", -3.4333, 104.2333),
            ("Musi Banyuasin", -2.8833, 103.8333), ("Kota Lubuklinggau", -3.2833, 102.8667)
        ],
        "pantai": [
            "Pantai Tanjung Carat Banyuasin", "Pantai Pasir Payung Sungsang", "Pantai Pulau Kemaro Sungai Musi",
            "Pantai Danau Ranau Banding Agung", "Pantai Pelangi Danau Ranau", "Pantai Bidadari Danau Ranau",
            "Pantai Supat Barat Muba", "Pantai Sinjar Musi Banyuasin", "Pantai Air Salek", "Pantai Muara Sugihan",
            "Pantai Sembilang Laut", "Pantai Tanjung Menjangan", "Pantai Pasir Putih Sukapindah", "Pantai Alur Betung",
            "Pantai Teluk Kijing", "Pantai Muara Kumbang"
        ],
        "gunung": [
            "Gunung Dempo Pagar Alam", "Bukit Serelo Jempol Lahat", "Gunung Patah Sumsel",
            "Bukit Siguntang Palembang", "Bukit Besak Lahat", "Puncak Rimba Candi", "Bukit Sulap Lubuklinggau",
            "Bukit Gajah Lahat", "Puncak Perkebunan Teh Pagar Alam", "Bukit Cogong Musi Rawas", "Bukit Barisan Lahat", "Bukit Pendape Muba"
        ],
        "alam": [
            "Danau Ranau Sumsel", "Air Terjun Curup Tenang Bedegung", "Taman Nasional Sembilang",
            "Air Terjun Lematang Indah", "Air Terjun Temam Lubuklinggau", "Danau Shuji Lembak",
            "Air Terjun Cuhup Maung", "Kawasan Megalitikum Lahat", "Danau Ulak Lia Sekayu", "Gua Putri Baturaja"
        ],
        "budaya": [
            "Jembatan Ampera Palembang", "Benteng Kuto Besak Palembang", "Pulau Kemaro Pagoda",
            "Museum Balaputradeva Rumah Limas", "Taman Purbakala Kerajaan Sriwijaya",
            "Rumah Adat Baghi Pagar Alam", "Kampung Arab Al-Munawar", "Museum Sultan Mahmud Badaruddin II"
        ],
        "hiburan": ["Jakabaring Sport City Palembang", "Amanzi Waterpark Palembang", "Punti Kayu Forest Park", "Fantasy Island Palembang", "Kambang Iwak Park"],
        "belanja": ["Pasar 16 Ilir Palembang", "Sentra Pempek 26 Ilir", "Sentra Songket Tangga Buntung", "Palembang Icon Mall", "Pasar Cinde Palembang"],
        "religi": ["Masjid Agung Sultan Mahmud Badaruddin I", "Masjid Cheng Ho Jakabaring", "Al-Qur'an Raksasa Gandus", "Masjid Lawang Kidul", "Vihara Dharmakirti"]
    },
    {
        "nama": "Bengkulu", "pulau": "Sumatera", "ibukota": "Bengkulu",
        "cities": [
            ("Kota Bengkulu", -3.8004, 102.2655), ("Rejang Lebong", -3.4667, 102.5333),
            ("Bengkulu Utara", -3.4333, 102.1833), ("Kepahiang", -3.6500, 102.5833),
            ("Bengkulu Selatan", -4.4667, 102.9000), ("Kaur", -4.7500, 103.3500),
            ("Mukomuko", -2.5833, 101.1167), ("Seluma", -4.0833, 102.5833),
            ("Bengkulu Tengah", -3.7333, 102.4333), ("Lebong", -3.1833, 102.2167)
        ],
        "pantai": [
            "Pantai Panjang Bengkulu", "Pantai Pasir Putih Bengkulu", "Pantai Tapak Paderi",
            "Pantai Jakat Bengkulu", "Pantai Sungai Suci", "Pantai Linau Kaur",
            "Pantai Laguna Samudra Kaur", "Pantai Pasar Bawah Manna", "Pantai Abrasi Mukomuko",
            "Pantai Way Hawang Kaur", "Pantai Alur Maung", "Pantai Cemara Indah Seluma",
            "Pantai Pekik Nyaring", "Pantai Kura-Kura Seluma", "Pantai Pandan Wangi Mukomuko", "Pantai Baai Bengkulu"
        ],
        "gunung": [
            "Gunung Kaba Curup", "Gunung Daun Rejang Lebong", "Gunung Bungkuk Bengkulu Tengah",
            "Bukit Kandis Karang Tinggi", "Bukit Kaba Ekowisata", "Puncak Bukit Jipang Curup", "Bukit Daun Kembar",
            "Bukit Hitam Kepahiang", "Bukit Kumbang Seluma", "Puncak Bukit Peninjauan", "Bukit Pematang Danau", "Puncak Bukit Menangis"
        ],
        "alam": [
            "Habitat Bunga Rafflesia Taba Penanjung", "Pulau Tikus Karang Laut", "Danau Dendam Tak Sudah",
            "Danau Mas Harun Bastari", "Air Terjun Kepala Curup", "Pemandian Air Panas Suban",
            "Air Terjun Tri Muara Karang", "Danau Tes Lebong", "Air Terjun Sengkuang Kepahiang", "Sungai Air Berau Mukomuko"
        ],
        "budaya": [
            "Benteng Marlborough Inggris", "Rumah Pengasingan Bung Karno", "Rumah Fatmawati Soekarno",
            "Tugu Thomas Parr", "Monumen Hamilton", "Museum Negeri Bengkulu", "Perkampungan Tradisional Rejang",
            "Makam Sentot Ali Basya"
        ],
        "hiburan": ["Taman Berkas Kota Bengkulu", "Taman Smart City Bengkulu", "Wahana Surya Bengkulu Tengah", "Danau Picung Park Lebong", "Taman Kota Curup"],
        "belanja": ["Pasar Barukoto Bengkulu", "Sentra Kerajinan Kulit Lantung", "Sentra Sirup Kalamansi Anggut", "Sentra Kopi Robusta Kepahiang", "Bencoolen Mall"],
        "religi": ["Masjid Jamik Bengkulu Arsitektur Soekarno", "Masjid Raya Baitul Izzah", "Masjid Agung At-Taqwa Bengkulu", "Vihara Rukun Maitreya", "Gereja Santo Yohanes Bengkulu"]
    },
    {
        "nama": "Lampung", "pulau": "Sumatera", "ibukota": "Bandar Lampung",
        "cities": [
            ("Kota Bandar Lampung", -5.4292, 105.2625), ("Lampung Selatan", -5.7333, 105.5833),
            ("Pesawaran", -5.4333, 105.1833), ("Tanggamus", -5.5000, 104.6833),
            ("Lampung Barat", -5.0333, 104.1000), ("Pesisir Barat Krui", -5.2000, 103.9333),
            ("Lampung Timur", -5.1000, 105.6833), ("Lampung Tengah", -4.9500, 105.2000),
            ("Kota Metro", -5.1133, 105.3067), ("Pringsewu", -5.3500, 104.9833)
        ],
        "pantai": [
            "Pantai Tanjung Setia Krui", "Pantai Mutun Pesawaran", "Pantai Sari Ringgit",
            "Pantai Pasir Putih Lampung", "Pantai Gigi Hiu Karang Layar", "Pantai Marina Kalianda",
            "Pantai Clara Pesawaran", "Pantai Minang Rua Bakauheni", "Pantai Labuhan Jukung Krui",
            "Pantai Embe Kalianda", "Pantai Guci Batu Kapal", "Pantai Sebalang Tarahan",
            "Pantai Mandiri Krui", "Pantai Batu Tihang", "Pantai Ketang Kalianda", "Pantai Wartawan Karang Purba"
        ],
        "gunung": [
            "Gunung Anak Krakatau Selat Sunda", "Gunung Pesagi Liwa", "Gunung Rajabasa Kalianda",
            "Gunung Tanggamus", "Gunung Betung Bandar Lampung", "Bukit Asahan Pesawaran", "Puncak Muncak Teropong Laut",
            "Bukit BLT Pringsewu", "Puncak Bawang Bakauheni", "Bukit Kabut Bawang Liwa", "Gunung Seminung Ranau", "Bukit Sakura Bandar Lampung"
        ],
        "alam": [
            "Taman Nasional Way Kambas", "Pulau Pahawang Snorkeling", "Teluk Kiluan Lumba-Lumba",
            "Pulau Kelagian Pesawaran", "Danau Suoh Lampung Barat", "Air Terjun Way Lalaan",
            "Air Terjun Curup Tujuh", "Pulau Tegal Mas Maldives Lampung", "Air Terjun Putri Malu", "Bendungan Batutegi"
        ],
        "budaya": [
            "Menara Siger Bakauheni", "Museum Negeri Lampung Ruwa Jurai", "Desa Wisata Kain Tapis Negeri Katon",
            "Situs Megalitikum Pugung Raharjo", "Rumah Adat Lamban Gedung Liwa", "Monumen Krakatau Bandar Lampung",
            "Kerajaan Adat Paksi Pak Sekala Brak", "Desa Adat Wana Lampung Timur"
        ],
        "hiburan": ["Taman Wisata Lembah Hijau", "Bumi Kedaton Resort Waterpark", "Taman Kupu-kupu Gita Persada", "Camp 91 Kedaung", "Wira Garden Lampung"],
        "belanja": ["Sentra Keripik Pisang Gang PU", "Pasar Bambu Kuning", "Sentra Kopi Robusta Liwa", "Sentra Tenun Tapis Soekardi", "Mall Boemi Kedaton"],
        "religi": ["Masjid Al-Furqon Bandar Lampung", "Masjid Terapung Al-Aminah", "Gereja Katedral Kristus Raja", "Vihara Thay Hin Bio", "Masjid Islamic Center Tubaba"]
    },
    {
        "nama": "Kepulauan Bangka Belitung", "pulau": "Sumatera", "ibukota": "Pangkal Pinang",
        "cities": [
            ("Kota Pangkal Pinang", -2.1333, 106.1167), ("Bangka", -1.8500, 106.1167),
            ("Belitung", -2.7333, 107.6500), ("Belitung Timur", -2.8833, 108.2667),
            ("Bangka Barat", -2.0667, 105.1667), ("Bangka Tengah", -2.4833, 106.2167),
            ("Bangka Selatan", -2.9833, 106.4500)
        ],
        "pantai": [
            "Pantai Tanjung Tinggi Belitung Granit", "Pantai Tanjung Kelayang UNESCO", "Pantai Parai Tenggiri Sungailiat",
            "Pantai Matras Bangka", "Pantai Pasir Padi Pangkalpinang", "Pantai Penyusuk Belinyu",
            "Pantai Tikus Emas Sungailiat", "Pantai Burung Mandi Manggar", "Pantai Punai Belitung Timur",
            "Pantai Batu Bedaun Sungailiat", "Pantai Tongaci Bangka", "Pantai Nyiur Melambai",
            "Pantai Batu Dinding Belinyu", "Pantai Siangau Bangka Barat", "Pantai Nek Aji Toboali", "Pantai Batu Kapur Toboali"
        ],
        "gunung": [
            "Gunung Menumbing Muntok", "Gunung Maras Bangka", "Bukit Berahu Belitung",
            "Bukit Samak Manggar", "Bukit Menara Belitung", "Bukit Kejora Koba",
            "Bukit Pala Muntok", "Bukit Gebang Toboali", "Puncak Bukit Peramun Belitung",
            "Bukit Batu Baginde Belitung Selatan", "Bukit Panjang Sungailiat", "Bukit Betung Pangkal Pinang"
        ],
        "alam": [
            "Pulau Lengkuas Mercusuar 1882", "Danau Kaolin Air Raya Belitung", "Danau Kaolin Nibung Bangka Tengah",
            "Pulau Batu Berlayar Belitung", "Pulau Pasir Bintang Laut Belitung", "Batu Belimbing Toboali",
            "Hutan Mangrove Munjut", "Air Terjun Gurok Beraye Belitung", "Pemandian Air Panas Tirta Tapta", "Batu Mentas Konservasi Tarsius"
        ],
        "budaya": [
            "Museum Kata Andrea Hirata Gantung", "Replika SD Laskar Pelangi Gantong", "Pesanggrahan Menumbing Muntok",
            "Museum Timah Indonesia", "Benteng Toboali Bangka Selatan", "Kampung Adat Gebong Memarong",
            "Rumah Adat Melayu Bangka", "Pha Kak Liang Belinyu"
        ],
        "hiburan": ["Bangka Botanical Garden (BBG)", "Alun-alun Taman Merdeka Pangkalpinang", "De Locomotief Pantai Tongaci", "Tirta Teratai Sungailiat", "Manggar Waterpark"],
        "belanja": ["Sentra Kerupuk Kemplang Pangkalpinang", "Sentra Kopi Manggar 1001 Warung", "Sentra Terasi Toboali", "Pasar Mambo Pangkalpinang", "Sentra Batik Cual Ishadi"],
        "religi": ["Puri Tri Agung Sungailiat", "Vihara Dewi Kwan Im Belitung Timur", "Masjid Jamik Pangkalpinang", "Klenteng Kwan Tie Miau", "Kelenteng Fuk Tet Che Muntok"]
    },

    # ==================== 2. JAWA (6 PROVINSI) ====================
    {
        "nama": "Banten", "pulau": "Jawa", "ibukota": "Serang",
        "cities": [
            ("Kota Serang", -6.1200, 106.1500), ("Kota Cilegon", -6.0167, 106.0500),
            ("Kota Tangerang", -6.1783, 106.6319), ("Kota Tangerang Selatan", -6.2889, 106.7181),
            ("Pandeglang", -6.3083, 106.1067), ("Lebak", -6.6500, 106.2167),
            ("Tangerang", -6.2000, 106.5000), ("Serang", -6.1500, 106.0500)
        ],
        "pantai": [
            "Pantai Anyer", "Pantai Carita", "Pantai Tanjung Lesung", "Pantai Sawarna",
            "Pantai Bagedur Lebak", "Pantai Karang Bolong Anyer", "Pantai Ciputih Ujung Kulon", "Pantai Sambolo",
            "Pantai Florida Anyer", "Pantai Marina Anyer", "Pantai Pasir Putih Sirih", "Pantai Karang Taraje Sawarna",
            "Pantai Goa Langir Sawarna", "Pantai Pulau Umang", "Pantai Bugel Cemara", "Pantai Batu Saung Anyer"
        ],
        "gunung": [
            "Gunung Pulosari Pandeglang", "Gunung Karang Pandeglang", "Gunung Aseupan", "Gunung Honje Ujung Kulon",
            "Bukit Waruwangi Serang", "Puncak Bukit Batu Gede Sayar", "Gunung Kencana Lebak", "Gunung Luhur Negeri di Atas Awan",
            "Bukit Teletubbies Cilegon", "Puncak Cibaja Anyer", "Gunung Pinang Serang", "Gunung Kendeng Lebak"
        ],
        "alam": [
            "Taman Nasional Ujung Kulon", "Curug Putri Tahura Carita", "Danau Tasikardi Serang", "Curug Cigumawang",
            "Curug Dengdeng Lebak", "Pulau Sangiang Selat Sunda", "Pulau Merak Kecil", "Rawa Dano Konservasi",
            "Pemandian Air Panas Cisolong", "Danau Biru Cisoka Cigaru"
        ],
        "budaya": [
            "Desa Adat Suku Baduy Luar & Dalam", "Kawasan Keraton Kaibon Banten Lama", "Benteng Speelwijk",
            "Museum Situs Kepurbakalaan Banten Lama", "Keraton Surosowan Banten Lama", "Museum Multatuli Rangkasbitung",
            "Makam Pangeran Jaga Lautan Pulau Cangkir", "Vihara Avalokitesvara Banten Lama"
        ],
        "hiburan": ["Scientia Square Park Tangerang", "Ocean Park Water Adventure BSD", "Taman Potret Tangerang", "Taman Tebing Koja Kandang Godzila", "Citra Raya World of Wonders"],
        "belanja": ["Pasar Lama Kuliner Tangerang", "Sentra Emping Menes Pandeglang", "Sentra Kerajinan Golok Ciomas", "Pasar Modern BSD City", "Bintaro Jaya Xchange"],
        "religi": ["Masjid Agung Banten Menara Mercusuar", "Masjid Raya Al-A'zhom Tangerang (Kubah Terbesar)", "Klenteng Boen Tek Bio Pasar Lama", "Masjid Pintu Seribu Tangerang", "Vihara Boen San Bio"]
    },
    {
        "nama": "DKI Jakarta", "pulau": "Jawa", "ibukota": "Jakarta",
        "cities": [
            ("Jakarta Pusat", -6.1865, 106.8341), ("Jakarta Selatan", -6.2615, 106.8106),
            ("Jakarta Barat", -6.1683, 106.7589), ("Jakarta Timur", -6.2250, 106.9004),
            ("Jakarta Utara", -6.1384, 106.8640), ("Kepulauan Seribu", -5.6122, 106.5614)
        ],
        "pantai": [
            "Pantai Ancol Lagoon", "Pantai Pasir Perawan Pulau Pari", "Pantai Pulau Pramuka", "Pantai Pulau Tidung",
            "Pantai Karnaval Ancol", "Pantai Festival Ancol", "Pantai Indah Kapuk (PIK 2)", "Pantai Pasir Putih PIK 2",
            "Pantai Pulau Harapan", "Pantai Pulau Sepa", "Pantai Pulau Macan", "Pantai Pulau Bidadari",
            "Pantai Pulau Onrust", "Pantai Pulau Semak Daun", "Pantai Pulau Kotok", "Pantai Mutiara Pluit"
        ],
        "gunung": [
            "Tebet Eco Park Canopy Trail", "Hutan Kota GBK Senayan", "Taman Suropati Menteng", "Taman Situ Lembang",
            "Taman Mataram Kebayoran", "Taman Ayodia Barito", "Taman Langsat Kebayoran Baru", "Taman Cattleya Tomang",
            "Taman Spathodea Jagakarsa", "Taman Waduk Pluit", "Taman Puring", "Taman Lapangan Banteng"
        ],
        "alam": [
            "Taman Margasatwa Ragunan", "Taman Wisata Alam Mangrove Angke Kapuk", "Akuarium Sea World Ancol",
            "Jakarta Aquarium & Safari Neo Soho", "Taman Hutan Kota Penjaringan", "Suaka Margasatwa Muara Angke",
            "Hutan Kota Srengseng Jakarta Barat", "Setu Babakan Perkampungan Betawi", "Danau Sunter Jakarta Utara", "Taman Tribeca Central Park"
        ],
        "budaya": [
            "Monumen Nasional (Monas)", "Kawasan Kota Tua Fatahillah", "Museum Fatahillah Jakarta", "Museum Wayang Kota Tua",
            "Museum Bank Indonesia", "Museum Nasional Gajah", "Gedung Kesenian Jakarta", "Museum Bahari Sunda Kelapa",
            "Museum Macan Seni Modern", "Gedung Joang 45 Menteng"
        ],
        "hiburan": ["Dunia Fantasi (Dufan)", "Taman Mini Indonesia Indah (TMII)", "Atlantis Water Adventure Ancol", "Ocean Dream Samudra Ancol", "KidZania Pacific Place"],
        "belanja": ["Grand Indonesia Shopping Town", "Plaza Indonesia Bundaran HI", "Pasar Tanah Abang Tekstil", "Pasar Baru Heritage Jakarta", "Senayan City Mall"],
        "religi": ["Masjid Istiqlal Jakarta", "Gereja Katedral Santa Maria Pelindung Diangkat Ke Surga", "Gereja Immanuel Gambir", "Kelenteng Jin De Yuan Glodok", "Masjid Ramlie Musofa Danau Sunter"]
    },
    {
        "nama": "Jawa Barat", "pulau": "Jawa", "ibukota": "Bandung",
        "cities": [
            ("Kota Bandung", -6.9175, 107.6191), ("Bandung Barat", -6.8500, 107.5000),
            ("Bogor", -6.5950, 106.7890), ("Kota Bogor", -6.5971, 106.7949),
            ("Sukabumi", -6.9200, 106.9300), ("Cianjur", -6.8200, 107.1400),
            ("Garut", -7.2100, 107.9000), ("Kuningan", -6.9800, 108.4800),
            ("Pangandaran", -7.6950, 108.6550), ("Cirebon", -6.7200, 108.5600)
        ],
        "pantai": [
            "Pantai Pangandaran Barat & Timur", "Pantai Batu Karas Pangandaran", "Pantai Ujung Genteng Sukabumi",
            "Pantai Pelabuhan Ratu", "Pantai Karang Hawu Sukabumi", "Pantai Santolo Garut", "Pantai Sayang Heulang Garut",
            "Pantai Rancabuaya Garut", "Pantai Madasari Pangandaran", "Pantai Lembah Putri Pangandaran",
            "Pantai Kejawanan Cirebon", "Pantai Cibangban Sukabumi", "Pantai Cipatujah Tasikmalaya", "Pantai Karapyak Pangandaran",
            "Pantai Karang Tawulan Tasikmalaya", "Pantai Karang Paranje Garut"
        ],
        "gunung": [
            "Gunung Tangkuban Perahu", "Kawah Putih Gunung Patuha", "Gunung Papandayan Garut",
            "Gunung Gede Pangrango", "Gunung Ciremai Kuningan", "Gunung Salak Bogor", "Gunung Puntang Bandung Selatan",
            "Tebing Keraton Dago Bandung", "Tebing Citatah Karst Padalarang", "Puncak Pass Bogor", "Gunung Galunggung Tasikmalaya", "Gunung Cikuray Garut"
        ],
        "alam": [
            "Green Canyon Cukang Taneuh Pangandaran", "Kebun Raya Bogor", "Situ Patenggang Ciwidey",
            "Taman Safari Indonesia Cisarua", "Curug Cikaso Sukabumi", "Curug Malela Little Niagara",
            "Kawah Kamojang Garut", "Situ Bagendit Garut", "Curug Cimahi Pelangi", "Telaga Remis Kuningan"
        ],
        "budaya": [
            "Saung Angklung Udjo Bandung", "Gedung Sate Bandung", "Keraton Kasepuhan Cirebon", "Keraton Kanoman Cirebon",
            "Kampung Naga Tasikmalaya", "Situs Megalitikum Gunung Padang Cianjur", "Museum Geologi Bandung", "Museum Konferensi Asia Afrika"
        ],
        "hiburan": ["Dusun Bambu Lembang", "Trans Studio Bandung", "Floating Market Lembang", "Farmhouse Susu Lembang", "The Great Asia Africa Lembang"],
        "belanja": ["Pasar Baru Trade Center Bandung", "Sentra Rajut Binong Jati", "Sentra Sepatu Cibaduyut", "Sentra Batik Trusmi Cirebon", "Paris Van Java Mall"],
        "religi": ["Masjid Raya Al Jabbar Gedebage", "Masjid Raya Bandung Alun-Alun", "Masjid Agung Sang Cipta Rasa Cirebon", "Gua Maria Sawer Rahmat Cisantana", "Vihara Dharma Ramsi Bandung"]
    },
    {
        "nama": "Jawa Tengah", "pulau": "Jawa", "ibukota": "Semarang",
        "cities": [
            ("Kota Semarang", -6.9667, 110.4167), ("Kota Surakarta Solo", -7.5667, 110.8167),
            ("Magelang", -7.4833, 110.2167), ("Wonosobo", -7.3667, 109.9000),
            ("Karanganyar", -7.6000, 110.9500), ("Jepara", -6.5833, 110.6667),
            ("Banyumas", -7.5167, 109.2833), ("Klaten", -7.7000, 110.6000),
            ("Kebumen", -7.6667, 109.6500), ("Pekalongan", -6.8833, 109.6667)
        ],
        "pantai": [
            "Pantai Menganti Kebumen", "Pantai Kartini Jepara", "Pantai Karang Jahe Rembang",
            "Pantai Bandengan Jepara", "Pantai Marina Semarang", "Pantai Suwuk Kebumen",
            "Pantai Logending Ayah Kebumen", "Pantai Pecaron Kebumen", "Pantai Widarapayung Cilacap",
            "Pantai Teluk Penyu Cilacap", "Pantai Tanjung Karang Jepara", "Pantai Sigandu Batang",
            "Pantai Pasir Kencana Pekalongan", "Pantai Cahaya Kendal", "Pantai Jatimalang Purworejo", "Pantai Tirang Semarang"
        ],
        "gunung": [
            "Gunung Merbabu Selo", "Gunung Slamet Banyumas", "Gunung Prau Dieng Golden Sunrise",
            "Gunung Sindoro Kledung", "Gunung Sumbing Bowongso", "Gunung Lawu Karanganyar",
            "Bukit Sikunir Dieng", "Puncak Telomoyo Magelang", "Bukit Rhema Gereja Ayam", "Ketep Pass Merapi Magelang",
            "Puncak Suroloyo Menoreh", "Gunung Ungaran Gedong Songo"
        ],
        "alam": [
            "Candi Borobudur Magelang", "Candi Prambanan Klaten", "Dataran Tinggi Dieng Telaga Warna",
            "Taman Nasional Karimunjawa", "Grojogan Sewu Tawangmangu", "Air Terjun Jumog Karanganyar",
            "Baturraden Banyumas", "Umbul Ponggok Klaten Snorkeling Tawar", "Rawa Pening Ambarawa", "Kawah Sikidang Dieng"
        ],
        "budaya": [
            "Lawang Sewu Semarang", "Keraton Kasunanan Surakarta", "Pura Mangkunegaran Solo", "Candi Sukuh Karanganyar",
            "Candi Cetho Karanganyar", "Kota Lama Semarang Little Netherlands", "Museum Kereta Api Ambarawa", "Museum Batik Pekalongan"
        ],
        "hiburan": ["Saloka Theme Park Ungaran", "Dusun Semilir Eco Park Bawen", "Taman Kyai Langgeng Magelang", "The Lawu Park Tawangmangu", "Pandawa Water World Solo Baru"],
        "belanja": ["Pasar Klewer Solo", "Sentra Batik Laweyan Solo", "Pasar Johar Semarang", "Sentra Ukir Mebel Jepara", "Sentra Bandeng Juwana Semarang"],
        "religi": ["Masjid Agung Jawa Tengah (MAJT)", "Gereja Blenduk Kota Lama Semarang", "Klenteng Sam Poo Kong Semarang", "Masjid Menara Kudus", "Masjid Raya Sheikh Zayed Solo"]
    },
    {
        "nama": "Daerah Istimewa Yogyakarta", "pulau": "Jawa", "ibukota": "Yogyakarta",
        "cities": [
            ("Kota Yogyakarta", -7.7956, 110.3695), ("Sleman", -7.7167, 110.3500),
            ("Bantul", -7.8833, 110.3333), ("Gunungkidul", -7.9667, 110.6000),
            ("Kulon Progo", -7.7667, 110.1667)
        ],
        "pantai": [
            "Pantai Parangtritis Bantul", "Pantai Indrayanti Pulang Syawal", "Pantai Pok Tunggal Gunungkidul",
            "Pantai Timang Gondola Laut", "Pantai Drini Gunungkidul", "Pantai Baron Muara Tawar",
            "Pantai Krakal Gunungkidul", "Pantai Kukup Karang Laut", "Pantai Siung Panjat Tebing",
            "Pantai Wediombo Laguna Karang", "Pantai Sadranan Snorkeling", "Pantai Glagah Dermaga Pemecah Ombak",
            "Pantai Depok Kuliner Ikan", "Pantai Ngrenehan Nelayan", "Pantai Jogan Air Terjun Tepi Laut", "Pantai Kuwaru Cemara Udang"
        ],
        "gunung": [
            "Gunung Merapi Bunker Kaliadem", "Klangon Merapi Gravity Park", "Puncak Gunung Nglanggeran Purba",
            "Bukit Bintang Patuk Gunungkidul", "Puncak Becici Dlingo", "Bukit Panguk Kediwung Bantul",
            "Puncak Tebing Breksi", "Puncak Sosok Bantul", "Bukit Paralayang Watugupit Parangtritis",
            "Puncak Menoreh Kulon Progo", "Bukit Mojo Gumelem", "Gunung Gambar Ngawen"
        ],
        "alam": [
            "Goa Pindul Cave Tubing", "Goa Jomblang Cahaya Surga", "Hutan Pinus Mangunan Dlingo",
            "Kalibiru Kulon Progo", "Ekowisata Sungai Mudal", "Air Terjun Kedung Pedut",
            "Taman Sungai Mudal Menoreh", "Gua Rancang Kencono", "Lava Tour Merapi Jeep", "Telaga Biru Semin Gunungkidul"
        ],
        "budaya": [
            "Keraton Ngayogyakarta Hadiningrat", "Taman Sari Water Castle", "Candi Ratu Boko Sunset",
            "Candi Sambisari Bawah Tanah", "Benteng Vredeburg Malioboro", "Museum Sonobudoyo",
            "Makam Raja-Raja Imogiri", "Museum Ullen Sentalu Kaliurang"
        ],
        "hiburan": ["HeHa Sky View Patuk", "HeHa Ocean View Gunungkidul", "Sindu Kusuma Edupark (SKE)", "Jogja Bay Pirates Waterpark", "Taman Pintar Yogyakarta"],
        "belanja": ["Jalan Malioboro Pedestrian", "Pasar Beringharjo Batik Tradisional", "Sentra Bakpia Pathok 25", "Sentra Kerajinan Perak Kotagede", "Sentra Gerabah Kasongan"],
        "religi": ["Masjid Gedhe Kauman Yogyakarta", "Gereja Ganjuran Hati Kudus Yesus", "Klenteng Fuk Ling Miau Gondomanan", "Pura Jagatnatha Banguntapan", "Masjid Jogokariyan Yogyakarta"]
    },
    {
        "nama": "Jawa Timur", "pulau": "Jawa", "ibukota": "Surabaya",
        "cities": [
            ("Kota Surabaya", -7.2575, 112.7521), ("Kota Malang", -7.9797, 112.6304),
            ("Kota Batu", -7.8700, 112.5200), ("Banyuwangi", -8.2167, 114.3667),
            ("Probolinggo", -7.7500, 113.2167), ("Pasuruan", -7.6467, 112.9067),
            ("Pacitan", -8.2000, 111.1000), ("Blitar", -8.1000, 112.1667),
            ("Jember", -8.1700, 113.7000), ("Mojokerto", -7.4700, 112.4300)
        ],
        "pantai": [
            "Pantai Klayar Pacitan Sphinx", "Pantai Papuma Jember", "Pantai Pulau Merah Banyuwangi",
            "Pantai Balekambang Malang Pura Ismoyo", "Pantai Teluk Hijau Green Bay Meru Betiri", "Pantai Sukamade Penyu Bertelur",
            "Pantai Tiga Warna Malang Clungup", "Pantai Goa Cina Malang", "Pantai Buyutan Pacitan Karang Mahkota",
            "Pantai Banyu Tibo Air Terjun Laut", "Pantai Plengkung G-Land Ombak Dunia", "Pantai Kenjeran Surabaya",
            "Pantai Pasir Putih Situbondo", "Pantai Boom Banyuwangi", "Pantai Kasap Raja Ampat Pacitan", "Pantai Ungapan Malang"
        ],
        "gunung": [
            "Gunung Bromo Kaldera Lautan Pasir", "Kawah Ijen Fenomena Api Biru", "Gunung Semeru Puncak Mahameru",
            "Gunung Arjuno Welirang", "Gunung Kelud Kawah Danau Blitar", "Gunung Panderman Batu",
            "Gunung Penanggungan Pawitra Sejarah", "Puncak B29 Lumajang Negeri di Atas Awan", "Gunung Butak Sirah Kencong",
            "Bukit Kingkong Bromo View", "Seruni Point Bromo", "Gunung Raung Kaldera Raksasa"
        ],
        "alam": [
            "Taman Nasional Baluran Afrika Jawa", "Taman Nasional Bromo Tengger Semeru", "Ranu Kumbolo Danau Surgawi Semeru",
            "Coban Rondo Air Terjun Malang", "Coban Sewu Tumpak Sewu Lumajang", "Air Terjun Madakaripura Mahapatih Gajah Mada",
            "Gua Gong Pacitan Terindah Se-Asia Tenggara", "De Djawatan Benculuk Hutan Fangorn", "Danau Ranu Bedali", "Batu Secret Zoo Jatim Park 2"
        ],
        "budaya": [
            "Museum Angkut Kota Batu", "Monumen Kapal Selam Monkasel Surabaya", "Jembatan Suramadu Selat Madura",
            "Situs Trowulan Ibu Kota Majapahit", "Candi Penataran Blitar", "Museum Rekor Dunia Trowulan",
            "Makam Proklamator Bung Karno Blitar", "Desa Adat Osing Kemiren Banyuwangi"
        ],
        "hiburan": ["Jatim Park 1 Edukasi", "Jatim Park 3 Dino Park", "Batu Night Spectacular (BNS)", "Selecta Taman Rekreasi Bunga Batu", "Hawai Waterpark Malang"],
        "belanja": ["Pasar Atom Surabaya", "Sentra Oleh-Oleh Keripik Tempe Sanan Malang", "Pasar Wisata Songgoriti", "Pusat Kerajinan Kulit Tanggulangin Sidoarjo", "Tunjungan Plaza Surabaya"],
        "religi": ["Masjid Nasional Al-Akbar Surabaya", "Masjid Tiban Turen Malang Arsitektur Unik", "Gereja Kelahiran Santa Perawan Maria Kepanjen", "Klenteng Hong San Ko Tee Surabaya", "Makam Sunan Ampel Surabaya"]
    }
]

print(f"Total Master Provinsi yang terdefinisi di batch 1: {len(ALL_38_PROVINCES)}")
