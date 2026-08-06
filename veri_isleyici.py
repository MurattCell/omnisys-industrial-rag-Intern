import pymupdf4llm

def pdf_metin_cikar(dosya_yolu):
    try:
        # Tabloları kusursuz Markdown formatına çevirir
        return pymupdf4llm.to_markdown(dosya_yolu)
    except Exception as e:
        print(f"PDF okunurken hata: {e}")
        return ""

def metni_parcalara_bol(metin, parca_uzunlugu=150, kesisim=50):
    # DİKKAT: app.py'den gelen kelime limitlerini yok sayıyoruz.
    # Tabloların (satır atlamalarının) bozulmaması için KARAKTER bazlı dilimleme yapıyoruz.
    gercek_uzunluk = 2000  # Her parça 2000 karakter olacak
    gercek_kesisim = 400   # 400 karakter bir öncekiyle kesişecek
    
    parcalar = []
    adim = gercek_uzunluk - gercek_kesisim
    
    for i in range(0, len(metin), adim):
        # Metni string olarak kesiyoruz, böylece \n komutları ve tablo yapısı ( |---| ) silinmiyor
        parca = metin[i:i + gercek_uzunluk]
        parcalar.append(parca)
        
    return parcalar