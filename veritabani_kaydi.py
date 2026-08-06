import asyncio
from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding
from semantic_kernel.memory.semantic_text_memory import SemanticTextMemory
from semantic_kernel.memory.volatile_memory_store import VolatileMemoryStore

from veri_isleyici import pdf_metin_cikar, metni_parcalara_bol

async def ana_islem():
    print("Microsoft Semantic Kernel başlatılıyor...")
    
    hafiza_deposu = VolatileMemoryStore()
    
    yerel_istemci = AsyncOpenAI(
        api_key="sk-yerel-sifre-gerekmez",
        base_url="http://localhost:11434/v1"
    )
    
    embedding_servisi = OpenAITextEmbedding(
        ai_model_id="nomic-embed-text",
        async_client=yerel_istemci
    )
    
    hafiza = SemanticTextMemory(storage=hafiza_deposu, embeddings_generator=embedding_servisi)
    
    print("Kılavuz okunuyor...")
    ham_metin = pdf_metin_cikar("ornek_kilavuz.pdf")
    parcalar = metni_parcalara_bol(ham_metin, kelime_limiti=100)
    
    print(f"Toplam {len(parcalar)} parça Semantic Kernel hafızasına (vektör olarak) kaydediliyor...")
    print("GPU ile Vektörleştirme yapılıyor, bu işlem kılavuzun boyutuna göre 1-2 dakika sürebilir, lütfen bekleyin...")
    
    for i, parca in enumerate(parcalar):
        await hafiza.save_information(
            collection="endustriyel_bilgiler",
            id=f"parca_{i}",
            text=parca
        )
    
    print("Kayıt tamam! Arama motoru test ediliyor...\n")
    
    soru = "Motor arızası veya uyarısı durumunda ne yapılmalıdır?" 
    
    print(f"Soru: {soru}")
    
    sonuclar = await hafiza.search("endustriyel_bilgiler", query=soru, limit=1)
    
    if sonuclar:
        bulunan_metin = sonuclar[0].text
        print("\n--- Semantic Kernel'in Bulduğu Kılavuz Metni ---")
        print(bulunan_metin)
        print("---------------------------------------------------\n")
        
        print("Phi-3 Modeli bu bilgiyi yorumlayıp cevap üretiyor (GPU kullanılıyor)...\n")
        
        # GÜNCELLEME: Prompt basitleştirildi, temperature=0.0 (Sıfır halüsinasyon) ve max_tokens eklendi
        cevap = await yerel_istemci.chat.completions.create(
            model="phi3",
            messages=[
                {"role": "system", "content": "Sen bir otomasyon asistanısın. SADECE sana verilen 'Kılavuz Bilgisi' içindeki metni kullanarak Türkçe ve maddeler halinde cevap ver. Bilgi metinde yoksa 'Kılavuzda bu bilgi bulunmuyor' de. Asla kendi bilgini katma."},
                {"role": "user", "content": f"Kılavuz Bilgisi: {bulunan_metin}\n\nTeknisyenin Sorusu: {soru}"}
            ],
            temperature=0.0,
            max_tokens=250
        )
        
        print("🤖 ASİSTANIN CEVABI:")
        print(cevap.choices[0].message.content)
        print("\n===================================================")
        
    else:
        print("Eşleşen bilgi bulunamadı.")

if __name__ == "__main__":
    asyncio.run(ana_islem())