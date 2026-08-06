import streamlit as st
import asyncio
from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding
from semantic_kernel.memory.semantic_text_memory import SemanticTextMemory
from semantic_kernel.memory.volatile_memory_store import VolatileMemoryStore

from veri_isleyici import pdf_metin_cikar, metni_parcalara_bol

# YENİ: Sayfa yapısını "wide" yaparak ekranı ferahlattık
st.set_page_config(page_title="Omnisys AI", page_icon="⚙️", layout="wide")

# YENİ: Havalı Sol Kontrol Paneli (Sidebar)
with st.sidebar:
    st.title("⚙️ Omnisys Panel")
    st.markdown("*Endüstriyel Otomasyon Asistanı*")
    st.divider()
    st.success("🟢 Sistem Bağlantısı: Aktif (Edge)")
    st.metric(label="Aktif Veritabanı", value="SINAMICS G120C PDF")
    st.metric(label="Yapay Zeka Motoru", value="Qwen 2.5 (7B)")
    st.metric(label="Veri Gizliliği", value="%100 Yerel")
    st.divider()
    st.caption("© 2026 Omnisys Industrial AI Systems")

# Ana Başlık
st.title("⚙️ Omnisys RAG Terminali")
st.markdown("**Saha arıza tespit ve anlık çözümleme sistemi.**")
st.divider()

@st.cache_resource
def get_memory_store():
    return VolatileMemoryStore()

depo = get_memory_store()

# YENİ: Özel Avatarlar Belirledik
ai_avatar = "⚙️"
user_avatar = "👷‍♂️"

if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = [{"role": "assistant", "content": "Sistem hazır. Kılavuzdaki bir arıza kodunu veya prosedürü sorabilirsiniz. "}]

for mesaj in st.session_state.mesajlar:
    # Geçmiş mesajlara da avatarları uyguluyoruz
    aktif_avatar = ai_avatar if mesaj["role"] == "assistant" else user_avatar
    with st.chat_message(mesaj["role"], avatar=aktif_avatar):
        st.markdown(mesaj["content"])

soru = st.chat_input("Arıza kodu veya semptom giriniz...")

if soru:
    st.session_state.mesajlar.append({"role": "user", "content": soru})
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(soru)

    with st.chat_message("assistant", avatar=ai_avatar):
        cevap_alani = st.empty()
        cevap_alani.markdown("⏳ *Yerel veritabanı taranıyor ve GPU ile işleniyor...*")
        
        async def ana_islem(kullanici_sorusu):
            yerel_istemci = AsyncOpenAI(api_key="sk-yerel", base_url="http://localhost:11434/v1")
            embedding_servisi = OpenAITextEmbedding(ai_model_id="nomic-embed-text", async_client=yerel_istemci)
            hafiza = SemanticTextMemory(storage=depo, embeddings_generator=embedding_servisi)
            
            if "db_dolu" not in st.session_state:
                ham_metin = pdf_metin_cikar("ornek_kilavuz.pdf")
                parcalar = metni_parcalara_bol(ham_metin, parca_uzunlugu=150, kesisim=50)
                for i, parca in enumerate(parcalar):
                    await hafiza.save_information(collection="omnisys_v3", id=f"parca_{i}", text=parca)
                st.session_state.db_dolu = True
                
            sonuclar = await hafiza.search("omnisys_v3", query=kullanici_sorusu, limit=10)
            
            if sonuclar:
                bulunan_metin = "\n\n---\n\n".join([sonuc.text for sonuc in sonuclar])
                cevap = await yerel_istemci.chat.completions.create(
                    model="qwen2.5:7b", 
                    messages=[
                        {
                            "role": "system", 
                            "content": "Sen sadece TÜRKÇE konuşan profesyonel bir endüstriyel otomasyon asistanısın. SANA VERİLEN METİN DIŞINDA HİÇBİR BİLGİ KULLANMA. Yanıtını KESİNLİKLE VE SADECE TÜRKÇE dilinde ver. Çince, İngilizce veya başka bir dil ASLA kullanma. Kullanıcının sorusunun cevabı metinde yoksa sadece 'Verilen kılavuz parçasında bu sorunun cevabı bulunmamaktadır.' yaz. Asla uydurma ve yorum yapma."
                        },
                        {"role": "user", "content": f"KILAVUZ METNİ:\n{bulunan_metin}\n\nSORU: {kullanici_sorusu}"}
                    ],
                    temperature=0.0
                )
                return cevap.choices[0].message.content
            return "Veritabanında eşleşme bulunamadı."
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            asistan_cevabi = loop.run_until_complete(ana_islem(soru))
        finally:
            loop.close()
            
        cevap_alani.markdown(asistan_cevabi)
        st.session_state.mesajlar.append({"role": "assistant", "content": asistan_cevabi})