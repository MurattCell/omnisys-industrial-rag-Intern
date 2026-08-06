import pymupdf4llm

print("PDF okunuyor, lütfen bekleyin...")

# PDF'i doğrudan ham Markdown metnine çeviriyoruz
ham_metin = pymupdf4llm.to_markdown("ornek_kilavuz.pdf")

# Vektörleri ve yapay zekayı devreden çıkarıp dümdüz kelime araması yapıyoruz
aranan_kod = "F30001"

if aranan_kod in ham_metin:
    print(f"\n✅ ZAFER: '{aranan_kod}' PDF'in içinde başarıyla bulundu!")
    
    # Kelimenin geçtiği yeri bulup etrafındaki 200 karakteri yazdırıyoruz
    indeks = ham_metin.find(aranan_kod)
    etrafındaki_metin = ham_metin[max(0, indeks - 50) : indeks + 150]
    print("\n--- İŞTE O SATIRLAR ---")
    print(etrafındaki_metin)
    print("-----------------------")
else:
    print(f"\n❌ HATA: '{aranan_kod}' kelimesi PDF metninin hiçbir yerinde YOK!")
    print("Muhtemelen o tablo bir resim formatında veya kodun arasına boşluk/tire konulmuş (Örn: F 30001).")