import re

def pdf_metin_cikar(dosya_yolu):
    """
    Endüstriyel PDF'lerdeki tabloların yapısını korumak için 
    PyMuPDF4LLM kütüphanesi kullanılarak Markdown'a çevirir.
    """
    try:
        import pymupdf4llm
        md_text = pymupdf4llm.to_markdown(dosya_yolu)
        return md_text
    except ImportError:
        # Eğer pymupdf4llm kurulu değilse standart okuma yapar
        import fitz
        doc = fitz.open(dosya_yolu)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

def metni_parcalara_bol(metin, parca_uzunlugu=800, kesisim=150):
    """
    Metni standart bir şekilde üst üste binen (overlapping) parçalara böler.
    Bağlamın kopmaması için kesisim (overlap) değeri önemlidir.
    """
    parcalar = []
    baslangic = 0
    metin_uzunlugu = len(metin)
    
    while baslangic < metin_uzunlugu:
        bitis = baslangic + parca_uzunlugu
        parcalar.append(metin[baslangic:bitis])
        baslangic += (parca_uzunlugu - kesisim)
        
    return parcalar

def kod_bazli_parcala(metin, baglam_limiti=1500):
    """
    F/A/C ile başlayan ve 3-6 rakam içeren hata kodlarını tespit eder,
    kodun geçtiği yerin etrafını (nedeni, çözümü) tek bir blok olarak alır.
    Böylece arıza tabloları parçalanıp vektör uzayında kaybolmaz.
    """
    kod_deseni = r"\b[A-Za-z]\d{3,6}\b"
    parcalar = []
    
    for m in re.finditer(kod_deseni, metin):
        # Kodun 200 karakter öncesinden başla, 1500 karakter sonrasına kadar al
        baslangic = max(0, m.start() - 200)
        bitis = min(len(metin), m.end() + baglam_limiti)
        parcalar.append(metin[baslangic:bitis])
        
    return parcalar