import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from streamlit_option_menu import option_menu


@st.cache_data
#Load Data CSV
def load_data(url) :
    df = pd.read_csv(url)
    return df

def Analisis_Preferensi_Pelanggan_Pola_Pembayaran(df_products, df_products_category_translation, df_order_payments, df_order_items) :
    st.markdown("10122901 - Aip Ariyadi - IF-13")

    #Alasan Analisis ini Penting
    st.write("Analisis terhadap penjualan berdasarkan kategori produk memberikan pemahaman mendalam terkait preferensi dan tren konsumen. Mengetahui kategori produk yang menjadi favorit pelanggan dan yang kurang diminati memungkinkan perusahaan untuk mengoptimalkan stok, strategi pemasaran, dan penawaran produk. Produk favorit dapat mendapatkan perhatian lebih lanjut, sementara produk yang kurang diminati dapat diperbaiki atau dikembangkan ulang. Analisis ini membantu perusahaan dalam pengambilan keputusan strategis untuk meningkatkan kepuasan pelanggan dan meningkatkan efisiensi operasional.")
    st.write("Sementara itu, analisis terhadap tipe pembayaran yang mendominasi transaksi memberikan wawasan tentang preferensi pembayaran pelanggan. Mengetahui tipe pembayaran yang paling umum digunakan memungkinkan perusahaan untuk menyusun strategi transaksi yang lebih efisien, termasuk negosiasi dengan penyedia pembayaran atau penerapan promosi khusus.")
    #Menggabungkan Ketiga Dataframe yang akan digunakan berdasarkan atribut kuncinya
    df_order_details = pd.merge(df_order_items, df_products, on='product_id')
    df_order_details = pd.merge(df_order_details, df_products_category_translation, on='product_category_name', how='left')

    #Memfilter baris dengan nilai null di kolom 'product_category_name_english'
    df_result_null_english = df_order_details[df_order_details['product_category_name_english'].isnull()]

    #Mencari daftar kategori yang belum memiliki terjemahan
    null_english_categories = df_result_null_english['product_category_name'].unique()

    #Membuat pemetaan terjemahan kategori yang akan diisi
    category_translation_mapping = {
        'portateis_cozinha_e_preparadores_de_alimentos': 'portable_kitchen_and_food_reparers',
        'pc_gamer': 'gaming_pc'
    }

    #Menambahkan terjemahan kategori pada dataframe asal
    df_order_details['product_category_name_english'] = df_order_details['product_category_name_english'].fillna(df_order_details['product_category_name'].map(category_translation_mapping))

    #Menghitung total produk yang dijual untuk setiap kategori yang ada
    category_counts = df_order_details.groupby('product_category_name_english').size().reset_index(name='total_items')

    #Mengurutkan hasil dari yang terbesar
    category_counts = category_counts.sort_values(by='total_items', ascending=False)

    #Menghitung jumlah transaksi untuk setiap tipe pembayaran
    transaction_counts = df_order_payments['payment_type'].value_counts()

    #Menghitung total nominal pembayaran untuk setiap tipe pembayaran
    total_payment_amounts = df_order_payments.groupby('payment_type')['payment_value'].sum()

    #Membuat dataframe baru untuk menampung hasil perhitungan
    df_payments_summary = pd.DataFrame({
        'Jumlah Transaksi': transaction_counts,
        'Total Nominal Pembayaran': total_payment_amounts
    })

    #Menghapus tipe pembayaran 'not_defined'
    df_payments_summary = df_payments_summary[(df_payments_summary.index != 'not_defined')]

    #Mengurutkan dataframe berdasarkan jumlah transaksi
    df_payments_summary = df_payments_summary.sort_values(by='Jumlah Transaksi', ascending=False)

    #Menambahkan kolom status kategori berdasarkan kondisi
    category_counts['category_status'] = pd.cut(category_counts['total_items'],
                                                bins=[float('-inf'), 10, 5000, float('inf')],
                                                labels=['not favorite', 'normal', 'favorite'])
    
    #Menghitung jumlah kategori untuk setiap status
    status_counts = category_counts['category_status'].value_counts()

    #Mengelompokkan berdasarkan category_status dan menjumlahkan total_items
    status_totals = category_counts.groupby('category_status', observed=False)['total_items'].sum().reset_index(name='total_items')

    #Grafik Penjualan Produk berdasarkan Kategori Produk
    st.header("Grafik Penjualan Produk berdasarkan Status Kategori")
    st.markdown("Dari Total 74 Kategori Produk, setelah dilakukan analisis terdapat 7 Kategori Produk Favorit & 3 Kategori Produk Kurang Diminati. Adapun Total Penjualan Produk berdasarkan statusnya (Favorit, Normal, Kurang Diminati) adalah sebagai berikut.")

    total_items_not_favorite = status_totals.loc[status_totals['category_status'] == 'not favorite', 'total_items'].values[0]
    total_items_normal = status_totals.loc[status_totals['category_status'] == 'normal', 'total_items'].values[0]
    total_items_favorite = status_totals.loc[status_totals['category_status'] == 'favorite', 'total_items'].values[0]

    data_penjualan_produk = pd.DataFrame({
        'Kategori': ['Favorit', 'Normal', 'Kurang Diminati'],
        'Jumlah Produk': [total_items_favorite, total_items_normal, total_items_not_favorite]
    })

    st.dataframe(data_penjualan_produk)

    fig, ax = plt.subplots(figsize=(8, 8))
    labels = ['Kurang Diminati', 'Normal', 'Favorit']
    sizes = status_totals['total_items']
    colors = ['#FF8849', '#69BE28', '#3DB7E4']

    # Plot pie
    ax.pie(sizes, labels=labels, autopct='%1.2f%%', startangle=140, colors=colors)
    ax.axis('equal')
    st.pyplot(fig)

    #Expander Grafik
    with st.expander("Penjelasan Persentase Penjualan Produk berdasarkan Status Kategori") :
        st.write("Dari visualisasi di atas, kita dapat mengetahui persentase penjualan produk untuk setiap status kategori. Kategori Favorit mencapai 51,97% dengan 7 kategori, sedangkan Kategori Normal menyumbang 48,02% dengan 64 kategori. Yang menarik, Kategori Kurang Diminati hanya menyumbang 0,02% dengan hanya 3 kategori. Meskipun jumlahnya kecil, angka ini mencerminkan diversitas penjualan di seluruh kategori produk. Sebagai catatan positif, proporsi yang sangat rendah dari Kategori Kurang Diminati menunjukkan bahwa mayoritas produk mendapatkan perhatian pelanggan. Dengan demikian, analisis ini menggambarkan keragaman dan keseimbangan penjualan produk, dan proporsi yang kecil pada Kategori Kurang Diminati dapat dianggap sebagai indikator positif.")

    st.write('<hr>', unsafe_allow_html=True) #hr Garis Pemisah
    #Grafik Klastering Kategori Produk berdasarkan Jumlah Pembelian
    st.header("Grafik Klastering Kategori Produk berdasarkan Jumlah Pembelian")
    st.write("Untuk tahap analisis lebih lanjut, dilakukan analisis klastering menggunakan algoritma K-Means untuk mengelompokkan kategori produk berdasarkan pola pembelian produk. Klastering adalah teknik analisis data yang digunakan untuk mengelompokkan data menjadi kelompok-kelompok yang memiliki kesamaan tertentu. Alasan utama di balik pembuatan klastering adalah untuk mengidentifikasi pola tersembunyi dalam data yang mungkin sulit dilihat secara langsung. Klastering dapat membantu dalam mengidentifikasi segmentasi pelanggan, pola pembelian yang dapat memberikan wawasan berharga untuk pengambilan keputusan.")
    category_counts_copy = category_counts[['product_category_name_english', 'total_items']].copy()

    #Rename nama kolom untuk memudahkan proses klastering
    category_counts_copy = category_counts_copy.rename(columns={'product_category_name_english': 'Kategori_Produk', 'total_items': 'Jumlah_Pembelian'})

    #Pemilihan fitur untuk analisis klastering
    features_for_clustering = category_counts_copy[['Jumlah_Pembelian']]

    #Standarisasi Fitur
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features_for_clustering)

    #Menentukan jumlah cluster menggunakan metode Elbow
    wcss = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
        kmeans.fit(features_scaled)
        wcss.append(kmeans.inertia_)

    #Memilih jumlah cluster yang optimal dan melakukan clustering
    optimal_clusters = 8
    kmeans = KMeans(n_clusters=optimal_clusters, init='k-means++', max_iter=300, n_init=10, random_state=0)
    clusters = kmeans.fit_predict(features_scaled)

    #Menambahkan kolom 'Cluster' ke DataFrame
    category_counts_copy['Cluster'] = clusters

    #Visualisasi data hasil klastering
    fig, ax = plt.subplots()
    scatter = ax.scatter(features_scaled[:, 0], [0] * len(features_scaled), c=clusters, cmap='viridis', s=50)
    ax.scatter(kmeans.cluster_centers_[:, 0], [0] * optimal_clusters, s=200, c='red', marker='X', label='Centroids')
    ax.set_xlabel('Jumlah Pembelian (Scaled)')
    ax.set_yticks([])
    ax.legend()
    st.pyplot(fig)

    #Expander Grafik
    with st.expander("Penjelasan Hasil Klastering Produk berdasarkan Jumlah Pembelian") :
        st.write('Dari visualisasi diatas, dalam konteks klastering kategori produk berdasarkan jumlah pembelian, hasil klastering memberikan kelompok-kelompok kategori produk yang memiliki perilaku pembelian serupa. Pemilihan jumlah kluster didasarkan pada plot analisis metode Elbow, yang mencoba menemukan jumlah kluster optimal. Dalam plot Elbow terdapat 10 kluster, namun terdapat penyesuaian menjadi 8 kluster (dilihat dari penyebaran Centroids/Titik Pusat Kluster). Setiap kluster mewakili sekelompok kategori produk yang memiliki karakteristik pembelian yang mirip. Dengan demikian, hasil klastering memberikan pandangan yang lebih terperinci tentang bagaimana produk berbeda-beda dalam hal perilaku pembelian mereka.') 

    st.write('<hr>', unsafe_allow_html=True) #hr Garis Pemisah
    #Grafik Pola Pembayaran Transaksi
    st.header("Grafik Pola Pembayaran Transaksi")

    st.write("Setelah dilakukan analisis, dapat diidentifikasi bahwa terdapat 4 tipe pembayaran yang digunakan oleh pelanggan dalam melakukan transaksi. Adapun rincian jumlah transaksi dan total pembayaran untuk masing-masing tipe pembayaran adalah sebagai berikut:")
    st.dataframe(df_payments_summary)

    st.subheader("Persentase Jumlah Transaksi & Nominal Pembayaran untuk Setiap Tipe Pembayaran")
    fig, ax = plt.subplots(figsize=(10, 6), ncols=2)
    # Visualisasi jumlah transaksi menggunakan bar chart
    # sns.barplot(ax=ax[0], x=df_payments_summary.index, y='Jumlah Transaksi', data=df_payments_summary, palette='viridis')
    sns.barplot(ax=ax[0], x=df_payments_summary.index, y='Jumlah Transaksi', hue=df_payments_summary.index, data=df_payments_summary, palette='viridis', dodge=False)
    # ax[0].legend().set_visible(False)
    ax[0].set_title('Jumlah Transaksi untuk Setiap Tipe Pembayaran')
    ax[0].set_xlabel('Tipe Pembayaran')
    ax[0].set_ylabel('Jumlah Transaksi')

    # Visualisasi total nominal pembayaran menggunakan bar chart
    # sns.barplot(ax=ax[1], x=df_payments_summary.index, y='Total Nominal Pembayaran', data=df_payments_summary, palette='magma')
    sns.barplot(ax=ax[1], x=df_payments_summary.index, y='Total Nominal Pembayaran', hue=df_payments_summary.index, data=df_payments_summary, palette='magma', dodge=False)
    # ax[1].legend().set_visible(False)
    ax[1].set_title('Total Nominal Pembayaran untuk Setiap Tipe Pembayaran')
    ax[1].set_xlabel('Tipe Pembayaran')
    ax[1].set_ylabel('Total Nominal Pembayaran')

    fig.tight_layout()
    st.pyplot(fig)

    #Expander Grafik
    with st.expander("Penjelasan Persentase Jumlah Transaksi & Total Nominal Pembayaran berdasarkan Tipe Pembayaran") :
        st.write('Dari visualisasi di atas, Perbandingan antara Jumlah Transaksi dan Total Nominal Pembayaran berdasarkan Tipe Pembayaran menggambarkan hubungan yang berbanding lurus, di mana semakin tinggi jumlah transaksi, total nominal pembayaran juga cenderung meningkat. Fenomena ini menunjukkan bahwa terdapat korelasi positif antara aktivitas transaksi dan nilai pembayaran. Peningkatan jumlah transaksi berkontribusi langsung terhadap pertumbuhan total nominal pembayaran, menciptakan dinamika yang seimbang dalam proses pembelian.') 

    st.subheader("Persentase Total Transaksi berdasarkan Tipe Pembayaran")
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(df_payments_summary['Jumlah Transaksi'], labels=df_payments_summary.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))

    for autotext in autotexts:
        autotext.set_color('white')

    st.pyplot(fig)

    #Expander Grafik
    with st.expander("Penjelasan Persentase Total Transaksi berdasarkan Tipe Pembayaran") :
        st.write('Dari visualisasi di atas, kita mendapatkan pemahaman yang signifikan mengenai persentase Total Transaksi untuk setiap Tipe Pembayaran. Dominasi Kartu Kredit terlihat sangat jelas, mencapai 73,9% dari keseluruhan transaksi. Kemudian, metode pembayaran Boleto memberikan kontribusi sebesar 19,0%. Sementara itu, penggunaan Voucher mencapai 5,6%, menyajikan opsi pembayaran yang signifikan selain Kartu Kredit dan Boleto. Adapun Kartu Debit, meskipun jumlahnya lebih kecil, tetap memberikan sumbangan sebesar 1,5%. Analisis persentase transaksi ini memberikan gambaran yang kuat tentang preferensi pembayaran pelanggan, dan dapat menjadi dasar strategi untuk meningkatkan pengalaman transaksi dan mengoptimalkan layanan pembayaran sesuai dengan kebutuhan dan keinginan pelanggan.') 


def Analisis_Pola_Pembelian_Korelasi_Peristiwa_Geografis(df_orders, df_order_items, df_products, df_customers) :
    st.markdown("10122907 - Vina Lestari - IF-13")

    #Alasan Analisis ini Penting
    st.write("Analisis pola pembelian terhadap peristiwa tertentu dapat memberikan pemahaman mengenai perilaku pelanggan pada peristiwa tersebut. Hal ini dapat membantu e-commerce dalam mengembangkan strategi pemasaran dan pengelolaan stok barang yang efektif. Analisis ini juga memberikan pemahaman mengenai dampak yang terjadi akibat perilaku pelanggan tersebut. Dengan memahami dampak yang terjadi, e-commerce dapat membuat keputusan strategi bisnis yang tepat, seperti dalam menentukan investasi bagi manajemen perusahaan.")
    st.write("Analisis korelasi antara volume pembelian dan geografi pelanggan mengidentifikasi penyebab minimnya dan banyaknya volume pembelian di setiap kota. Dari hasil analisis ini, dapat ditentukan strategi bisnis untuk memperluas pemasaran.")
    
    #Grafik Penjualan Produk berdasarkan Kategori Produk
    st.header("Grafik Volume Pembelian Berdasarkan Bulan dan Tanggal")
    st.markdown("Setelah dilakukan analisis terhadap data pembelian selama 3 tahun (2016 s.d. 2018) dengan melakukan segmentasi pembelian berdasarkan bulan dan tanggal yang sama, bahwa 3 tanggal dengan jumlah pembelian tertinggi terdapat pada tanggal 24 November menjadi jumlah pembelian terbanyak dengan 1.366 pembelian. Sementara pada tanggal 7 Agustus sebanyak 613 pembelian dan tanggal 15 Mei sebanyak 594 pembelian. Berikut detail jumlah pembelian yang sudah diurutkan dari jumlah pembelian terbanyak.")

    #Menggabungkan Ketiga Dataframe yang akan digunakan berdasarkan atribut kuncinya
    df_order_m = pd.merge(df_orders, df_order_items, on='order_id')
    df_order_merge = pd.merge(df_order_m, df_products, on='product_id', how='left')

    #Kemudian membuang semua kolom yang tidak diperlukan dan mengurutkan semua data berdasarkan tanggal
    df_order_merge = df_order_merge[['order_id', 'order_purchase_timestamp', 'product_id', 'product_category_name']]
    df_order_merge = df_order_merge.sort_values('order_purchase_timestamp')

    #Selanjuknya menyatukan kategori produk berdasarkan tanggal pemesanan
    df_order_merge['order_purchase_timestamp'] = pd.to_datetime(df_order_merge['order_purchase_timestamp'])

    # Extract only the date part
    df_order_merge['date'] = df_order_merge['order_purchase_timestamp'].dt.date
    df_count_order = df_order_merge['date'].value_counts().reset_index()

    # Group by the date and concatenate values in 'product_category_name'
    def convert_to_string(product_category_name):
        if isinstance(product_category_name, float):
            return str(product_category_name)
        else:
            return product_category_name

    df_result = df_order_merge.groupby('date')['product_category_name'].apply(lambda x: ', '.join(map(convert_to_string, x))).reset_index()
    df_result = pd.merge(df_result, df_count_order, on='date')

    #Mengambil jumlah pesanan berdasarkan tanggal dan bulan pemesanan yang sama di antara 3 tahun tersebut

    df_order_merge['order_purchase_timestamp'] = pd.to_datetime(df_order_merge['order_purchase_timestamp'])

    df_order_merge['Bulan'] = df_order_merge['order_purchase_timestamp'].dt.month
    df_order_merge['Tanggal'] = df_order_merge['order_purchase_timestamp'].dt.day

    # Count orders by month and day
    df_count_order = df_order_merge.groupby(['Bulan', 'Tanggal'])['order_purchase_timestamp'].count().reset_index()
    df_count_order.columns = ['Bulan', 'Tanggal', 'Jumlah Pembelian']

    # Group by month and day and concatenate product categories
    df_result = df_order_merge.groupby(['Bulan', 'Tanggal'])['product_category_name'].apply(lambda x: ', '.join(x)).reset_index()
    df_result.columns = ['Bulan', 'Tanggal', 'Kategori Produk']
    
    df_result = pd.merge(df_result, df_count_order, on=['Bulan', 'Tanggal'])

    # Sort by count
    df_result = df_result.sort_values('Jumlah Pembelian', ascending=False)
    st.dataframe(df_result)

    # Visualisasi
    df_order_merge['order_purchase_timestamp'] = pd.to_datetime(df_order_merge['order_purchase_timestamp'])

    df_order_merge['month'] = df_order_merge['order_purchase_timestamp'].dt.month
    df_order_merge['day'] = df_order_merge['order_purchase_timestamp'].dt.day

    df_count_order = df_order_merge.groupby(['month', 'day'])['order_purchase_timestamp'].count().reset_index()
    df_count_order.columns = ['month', 'day', 'count']

    df_result = df_count_order.sort_values('count', ascending=False)

    max = df_result.head(10)

    month_day_labels = []
    for index, row in max.iterrows():
        month_day_labels.append(f"{row['month']}-{row['day']}")

    # Calculate percentages
    total_orders = df_result['count'].sum()
    df_result['percentage'] = (df_result['count'] / total_orders) * 100

    # top 10 order
    max = df_result.head(10)

    # pie chart
    fig, ax = plt.subplots()
    ax.pie(max['count'], labels=month_day_labels, autopct='%1.1f%%', startangle=140, colors=sns.set_palette("ch:s=-.2,r=.6"))
    ax.set_title('Persentase Top 10 Pembelian Terbanyak berdasarkan Bulan-Tanggal')
    plt.tight_layout()

    fig.tight_layout()
    st.pyplot(fig)
    
    #Expander Grafik
    with st.expander("Penjelasan Persentase Top 10 Pembelian berdasarkan Bulan dan Tanggal") :
        st.markdown("Berdasarkan visualisasi di atas, terlihat bahwa pada tanggal 24 November dalam 3 tahun tersebut terdapat 1.366 pembelian dengan persentase sebesar 21.0%. Jumlah ini lebih dari 2 kali lipat dibandingkan seluruh tanggal lain dalam nominasi 10 besar pembelian terbanyak. Analisis terpisah menunjukkan bahwa tanggal 24 November merupakan masa di mana warga Brasil mempersiapkan Hari Natal.")
        st.markdown("Pada tanggal 7 Agustus, terdapat 613 pembelian dengan persentase 9.4%. Diketahui bahwa pada bulan Agustus, warga Brasil merayakan Festa Junina, dan barang-barang yang dibeli berkorelasi dengan festival tersebut. Sisanya tidak berkorelasi dengan hari perayaan tertentu.")

    #Grafik Penjualan Produk berdasarkan Kategori Produk
    st.header("Grafik Frekuensi Pembelian berdasarkan Kota Pelanggan")
    st.markdown("Hasil analisis terhadap frekuensi pembelian pada setiap kota pelanggan didapat bahwa mayoritas pelanggan berasal dari kota-kota besar. Sedangkan banyak kota pedesaan yang menjadi minoritas jumlah pembelian dengan total 1 pembelian dalam kurun waktu 3 tahun.")

    #Menggabungkan Dua Dataframe yang akan digunakan berdasarkan atribut kuncinya
    df_locOrder_details = pd.merge(df_orders, df_customers, on='customer_id')

    df_locOrder_merge = df_locOrder_details[['order_id', 'customer_id', 'customer_zip_code_prefix', 'customer_city']]
    df_locOrder_merge = df_locOrder_merge.sort_values('customer_city')

    #count
    locOrder_count = df_locOrder_merge['customer_city'].value_counts()

    # Convert locOrder_count menjadi dataframe
    city_counts_df = pd.DataFrame(locOrder_count).reset_index()
    city_counts_df.columns = ['Kota Pelanggan', 'Jumlah Pembelian']

    st.dataframe(city_counts_df)

    # Visualisasi Terbesar
    max = 10

    city_counts_df_sort = city_counts_df.sort_values('Jumlah Pembelian', ascending=False)

    top_cities_df = city_counts_df_sort.head(max)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(top_cities_df['Kota Pelanggan'], top_cities_df['Jumlah Pembelian'], color=sns.color_palette("rocket"))
    ax.set_xlabel('Kota Pelanggan')
    ax.set_ylabel('Jumlah Pembelian')
    ax.set_title(f'Top {max} Kota dengan Pemesanan Pembelian Terbanyak Selama 3 Tahun')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    city_counts_df_sort = city_counts_df.sort_values('Jumlah Pembelian' , ascending=True)

    st.dataframe(city_counts_df_sort)

    #Visualisasi Terkecil
    city_counts_df_sort = city_counts_df.sort_values('Jumlah Pembelian')

    top_cities_df = city_counts_df_sort.head(max)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(top_cities_df['Kota Pelanggan'], top_cities_df['Jumlah Pembelian'], color=sns.color_palette('rocket'))
    ax.set_xlabel('Kota Pelanggan')
    ax.set_ylabel('Jumlah Pembelian')
    ax.set_title(f'Top {max} Kota dengan Pemesanan Pembelian Terkecil Selama 3 Tahun')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()

    st.pyplot(fig)

    with st.expander("Penjelasan Frekuensi Pembelian berdasarkan Kota Pelanggan") :
        st.markdown("Dari hasil analisis, didapat bahwa penduduk di kota-kota besar menjadi penduduk dengan jumlah pemesanan barang tertinggi dibandingkan dengan kota-kota pedesaan di Brasil. Perbedaan jumlah pemesanan penduduk di kota besar dengan penduduk yang tinggal di kota pedesaan sangat signifikan. Hal ini dapat menjadi perhatian agar pemasaran produk dapat menjangkau kota pedesaan di Brasil dimulai dari apa yang mereka butuhkan, transportasi, dan lamanya barang yang dikirim dari luar kota yang tentunya dengan pendekatan keseharian penduduk di kota-kota tersebut. Untuk di kota-kota besar dapat dipertahankan dan ditingkatkan dengan pendekatan tren dan tawaran diskon yang terjadwalkan sehingga dapat mempertahankan loyalitas pembeli.")


def Analisis_Retensi_Pelanggan_dan_Pola_Pembelian(df_customers, df_orders, df_order_items, df_order_payments) :
    st.markdown("10122918 - Muhamad Farhan - IF-13")
    
    #Alasan Analisis ini Penting
    st.write("Analisis terhadap berapa banyak pelanggan yang melakukan pembelian hanya sekali dan tidak kembali lagi memberikan wawasan tentang tingkat retensi pelanggan. Mengetahui jumlah pelanggan yang melakukan pembelian sekali dan tidak kembali memungkinkan perusahaan untuk mengevaluasi efektivitas strategi retensi pelanggan dan meningkatkan upaya untuk mempertahankan pelanggan.")
    st.write("Sementara itu, analisis terhadap apakah ada kelompok pelanggan yang cenderung membeli produk dengan nilai transaksi lebih rendah dan nilai transaksi lebih tinggi memberikan pemahaman tentang perilaku pembelian pelanggan berdasarkan nilai transaksi. Identifikasi kelompok pelanggan ini memungkinkan perusahaan untuk menyesuaikan strategi pemasaran, penawaran produk, dan segmentasi pasar agar lebih efektif dalam menjangkau dan memenuhi kebutuhan berbagai kelompok pelanggan.")
    
    #Grafik Pelanggan
    st.header("Grafik Pelanggan")
    st.markdown("Dari total 99.441 jumlah pelanggan, setelah dilakukan analisis terdapat 2 kategori pelanggan. Adapun total pelanggan berdasarkan pembeliannya adalah sebagai berikut.")
    
    # Menghitung jumlah pesanan untuk setiap pelanggan berdasarkan ID pesanan
    order_counts = df_customers['customer_id'].value_counts()
    # Menghitung jumlah pesanan untuk setiap pelanggan berdasarkan ID unik pelanggan
    unique_order_counts = df_customers['customer_unique_id'].value_counts()
    # Mengidentifikasi pelanggan yang hanya melakukan satu pesanan
    single_order_customers = unique_order_counts[unique_order_counts == 1]
    # Mengidentifikasi pelanggan yang melakukan lebih dari satu pesanan
    multiple_order_customers = unique_order_counts[unique_order_counts > 1]
    # Menampilkan hasil perhitungan
    total_customers = len(order_counts)
    single_order_customers_count = len(single_order_customers)
    multiple_order_customers_count = len(multiple_order_customers)
    other_customers_count = total_customers - (single_order_customers_count + multiple_order_customers_count)
    multiple_order_customers_count += other_customers_count

    data_jumlah_pelanggan = pd.DataFrame({
        'Pelanggan': ['Pembelian Hanya Satu Kali', 'Pembelian Lebih Dari Satu Kali'],
        'Jumlah': [single_order_customers_count, multiple_order_customers_count]
    })

    st.dataframe(data_jumlah_pelanggan)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    labels = ['Pembelian Hanya Satu Kali', 'Pembelian Lebih Dari Satu Kali']
    sizes = [single_order_customers_count, multiple_order_customers_count]
    bars = ax.bar(labels, sizes, color=['blue', 'green'])

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, round(yval), va='bottom')
    ax.set_ylabel('Jumlah Pelanggan')
    ax.set_title('Jumlah Pelanggan Berdasarkan Pembelian')
    st.pyplot(fig)
    
    #Expander Grafik
    with st.expander("Penjelasan Pelanggan Berdasarkan Pembelian") :
        st.write("Dari visualisasi diatas, kita dapat melihat bahwa sebagian besar pelanggan hanya melakukan pembelian satu kali, sementara jumlah pelanggan yang melakukan pembelian lebih dari satu kali relatif sedikit. Dari sini, dapat disimpulkan bahwa penting untuk tidak hanya menarik pelanggan baru, tetapi juga mempertahankan pelanggan yang sudah ada dan mendorong mereka untuk melakukan pembelian berulang. Ini menekankan pentingnya strategi retensi pelanggan dan upaya untuk membangun hubungan jangka panjang dengan pelanggan yang ada.")
        
    st.write('<hr>', unsafe_allow_html=True) #hr Garis Pemisah
    #Grafik Pola Pembelian Transaksi
    st.header("Grafik Pola Pembelian Transaksi")
    #Menggabungkan Ketiga Dataframe yang akan digunakan berdasarkan atribut kuncinya
    df_order_detailed = pd.merge(df_orders, df_order_items)
    df_order_detailed = pd.merge(df_order_detailed, df_order_payments)
    
    st.write("Setelah dilakukan analisis, dapat di identifikasi bahwa terdapat 2 kategori nilai transaksi pembelian yang dilakukan oleh pelanggan. Adapun rincian 2 kategori nilai transaksi pembeliannya adalah sebagai berikut:")
    # Menentukan batas nilai transaksi rendah dan tinggi
    threshold_low_payment_value = 100  # misalnya, nilai transaksi kurang dari 100 dianggap rendah
    threshold_high_payment_value = 500  # misalnya, nilai transaksi lebih dari 500 dianggap tinggi
    # Mengidentifikasi pelanggan yang melakukan pembelian dengan nilai transaksi rendah
    low_value_buyers = df_order_detailed[df_order_detailed['payment_value'] < threshold_low_payment_value]['customer_id'].unique()
    # Mengidentifikasi pelanggan yang melakukan pembelian dengan nilai transaksi tinggi
    high_value_buyers = df_order_detailed[df_order_detailed['payment_value'] > threshold_high_payment_value]['customer_id'].unique()
    
    data_nilai_transaksi = pd.DataFrame({
        'Kategori Pelanggan': ['Nilai Transaksi Rendah', 'Nilai Transaksi Tinggi'],
        'Jumlah': [len(low_value_buyers), len(high_value_buyers)]
    })
    
    st.dataframe(data_nilai_transaksi)

    fig, ax = plt.subplots(figsize=(8, 8))
    labels = ['Nilai Transaksi Rendah', 'Nilai Transaksi Tinggi']
    sizes = [len(low_value_buyers), len(high_value_buyers)]
    bars = ax.bar(labels, sizes, color=['red', 'blue'])

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, round(yval), va='bottom')
    ax.set_ylabel('Jumlah Pelanggan')
    ax.set_title('Jumlah Pelanggan Berdasarkan Nilai Transaksi')
    st.pyplot(fig)
    
    #Expander Grafik
    with st.expander("Penjelasan Pembelian Berdasarkan Nilai Transaksi") :
        st.write("Dari visualisasi diatas, kita dapat melihat bahwa sebagian besar pelanggan dengan pembelian nilai transaksi rendah sangat banyak, sementara pelanggan dengan jumlah pembelian dengan nilai transaksi tinggi relatif sangat sedikit. Dari sini, dapat disimpulkan bahwa penting untuk mengadopsi strategi yang berbeda untuk setiap kategori pelanggan. Untuk pelanggan dengan pembelian nilai transaksi rendah, mungkin diperlukan strategi untuk meningkatkan frekuensi pembelian atau menawarkan produk dengan harga yang lebih terjangkau. Sementara untuk pelanggan dengan nilai transaksi tinggi, mungkin lebih penting untuk menjaga kualitas layanan dan produk agar mereka tetap loyal dan melakukan pembelian berulang.")


df_products = load_data("https://raw.githubusercontent.com/ariyadiaip/ScipyAnalisisData/main/products_dataset.csv")
df_products_category_translation = load_data("https://raw.githubusercontent.com/ariyadiaip/ScipyAnalisisData/main/product_category_name_translation.csv")
df_orders = load_data('https://raw.githubusercontent.com/ariyadiaip/ScipyAnalisisData/main/orders_dataset.csv')
df_order_items = load_data("https://raw.githubusercontent.com/ariyadiaip/ScipyAnalisisData/main/order_items_dataset.csv")
df_order_payments = load_data("https://raw.githubusercontent.com/ariyadiaip/ScipyAnalisisData/main/order_payments_dataset.csv")
df_customers = load_data('https://raw.githubusercontent.com/ariyadiaip/ScipyAnalisisData/main/customers_dataset.csv')

#Cleaning Data
#Menggantikan nilai null di kolom 'product_category_name' dengan 'uncategorized'
df_products['product_category_name'].fillna('uncategorized', inplace=True)

#Membuat DataFrame baru untuk baris yang akan ditambahkan
new_row = pd.DataFrame({'product_category_name': ['uncategorized'],
                            'product_category_name_english': ['uncategorized']})

#Menggunakan pandas.concat untuk menambahkan baris baru pada DataFrame Utama
df_products_category_translation = pd.concat([df_products_category_translation, new_row], ignore_index=True)


with st.sidebar :
    selected = option_menu('Menu',['Dashboard'],
    icons =["house", "graph-up"],
    menu_icon="cast",
    default_index=0)
    
if (selected == 'Dashboard') :
    st.header(f"Dashboard Analisis Data E-Commerce Public Dataset")
    tab1,tab2,tab3 = st.tabs(["Analisis Preferensi Pelanggan & Pola Pembayaran", 
                              "Analisis Pola Pembelian: Korelasi Peristiwa dan Geografis", 
                              "Analisis Retensi Pelanggan dan Pola Pembelian"])

    with tab1 :
        Analisis_Preferensi_Pelanggan_Pola_Pembayaran(df_products, df_products_category_translation, df_order_payments, df_order_items)
    with tab2 :
        Analisis_Pola_Pembelian_Korelasi_Peristiwa_Geografis(df_orders, df_order_items, df_products, df_customers)
    with tab3 :
        Analisis_Retensi_Pelanggan_dan_Pola_Pembelian(df_customers, df_orders, df_order_items, df_order_payments)

st.caption('Copyright (c) 2024')