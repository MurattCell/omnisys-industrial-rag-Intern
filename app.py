import streamlit as st
import asyncio
import re
from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding
from semantic_kernel.memory.semantic_text_memory import SemanticTextMemory
from semantic_kernel.memory.volatile_memory_store import VolatileMemoryStore

from veri_isleyici import pdf_metin_cikar, metni_parcalara_bol, kod_bazli_parcala

def kod_cikar(metin):
    """Sorudaki F30001, A50012, C0301 gibi arıza/alarm kodlarını yakalar."""
    return re.findall(r"\b[A-Za-z]\d{3,6}\b", metin)

def kod_ile_tam_eslesme_ara(tam_metin, kod, baglam_uzunlugu=450):
    """Sadece aranan kodun satırını ve çözüm adımlarını alacak kadar dar bir alan."""
    eslesmeler = []
    for m in re.finditer(re.escape(kod), tam_metin, flags=re.IGNORECASE):
        baslangic = max(0, m.start() - 50)
        bitis = min(len(tam_metin), m.end() + baglam_uzunlugu)
        eslesmeler.append(tam_metin[baslangic:bitis])
    return eslesmeler

st.set_page_config(page_title="Omnisys AI", page_icon="⚙️", layout="wide")

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

MIN_RELEVANCE = 0.3

st.title("⚙️ Omnisys RAG Terminali")
st.markdown("**Saha arıza tespit ve anlık çözümleme sistemi.**")
st.divider()

@st.cache_resource
def get_memory_store():
    return VolatileMemoryStore()

depo = get_memory_store()

ai_avatar = "⚙️"
user_avatar = "👷‍♂️"

if "mesajlar" not in st.session_state:
    st.session_state.mesajlar = [{"role": "assistant", "content": "Sistem hazır. Kılavuzdaki bir arıza kodunu veya prosedürü sorabilirsiniz."}]

for mesaj in st.session_state.mesajlar:
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

        async def ana_islem(kullanici_sorusu, min_relevance_score):
            yerel_istemci = AsyncOpenAI(api_key="sk-yerel", base_url="http://localhost:11434/v1")
            embedding_servisi = OpenAITextEmbedding(ai_model_id="nomic-embed-text", async_client=yerel_istemci)
            hafiza = SemanticTextMemory(storage=depo, embeddings_generator=embedding_servisi)

            if "db_dolu" not in st.session_state:
                ham_metin = pdf_metin_cikar("ornek_kilavuz.pdf")
                st.session_state.ham_metin = ham_metin 

                kod_parcalari = kod_bazli_parcala(ham_metin)
                genel_parcalar = metni_parcalara_bol(ham_metin, parca_uzunlugu=800, kesisim=150)
                parcalar = kod_parcalari + genel_parcalar

                for i, parca in enumerate(parcalar):
                    await hafiza.save_information(collection="omnisys_v3", id=f"parca_{i}", text=parca)
                st.session_state.db_dolu = True
                st.session_state.toplam_parca = len(parcalar)

            cikarilan_kodlar = kod_cikar(kullanici_sorusu)
            tum_parcalar = []

            if cikarilan_kodlar:
                for kod in cikarilan_kodlar:
                    tum_parcalar.extend(
                        kod_ile_tam_eslesme_ara(st.session_state.get("ham_metin", ""), kod)
                    )
            else:
                sonuclar = await hafiza.search(
                    "omnisys_v3",
                    query=kullanici_sorusu,
                    limit=3,
                    min_relevance_score=MIN_RELEVANCE,
                )
                tum_parcalar = [sonuc.text for sonuc in sonuclar]

            if tum_parcalar:
                essiz_parcalar = list(dict.fromkeys(tum_parcalar))
                bulunan_metin = "\n\n---\n\n".join(essiz_parcalar)

                # YENİ VE DAHA KESİN PARAMETRE ŞABLONU
                sistem_komutu = """Sen Kardemir A.Ş. sahası için çalışan uzman bir endüstriyel bakım asistanısın.

KURALLAR:
1. Yanıtını SADECE sana verilen 'KILAVUZ METNİ' içindeki bilgiye dayandır.
2. Kılavuz metni PDF'ten tablo halinde çekildiği için içinde "<br>", "•", "|" gibi işaretler olabilir. Bunları ayıkla ve mantıklı bir metne dönüştür.
3. Cevabını HER ZAMAN şu 4 başlık altında, temiz bir Türkçe ile ver:
   **Arızanın Ne Olduğu:** (Arızanın adını veya nedenini metinden bulup yaz)
   **Dikkat Edilmesi Gerekenler:** (Metinde vurgulanan uyarıları yaz. Yoksa "Belirtilmemiş." yaz)
   **İlgili Parametreler:** (SADECE metinde geçen, 'p' veya 'r' harfi ile başlayıp rakamlarla devam eden Siemens parametre kodlarını yaz. Örn: p0210, r0037, p1082 gibi. Buraya KESİNLİKLE normal kelime veya çözüm cümlesi yazma! Metinde bu formatta bir kod yoksa sadece "Belirtilmemiş." yaz)
   **Çözüm Adımları:** (Metindeki çözüm önerilerini maddeler halinde yaz)
4. YANITINDA KESİNLİKLE ÇİNCE KARAKTER KULLANMA. SADECE TÜRKÇE KONUŞ."""

                kati_kullanici_mesaji = f"""KILAVUZ METNİ:
{bulunan_metin}

SORU: {kullanici_sorusu}

MUTLAK EMİR: Yukarıdaki kılavuz metnini dikkatlice incele. HTML etiketlerini (<br> vb.) temizle ve SADECE sistem talimatındaki 4 BAŞLIKLI ŞABLONU kullanarak cevap ver. İlgili Parametreler kısmına sadece 'p' veya 'r' ile başlayan kodları yaz, cümle kurma! Kendi cümleni asla uydurma!"""

                cevap = await yerel_istemci.chat.completions.create(
                    model="qwen2.5:7b",
                    messages=[
                        {"role": "system", "content": sistem_komutu},
                        {"role": "user", "content": kati_kullanici_mesaji},
                    ],
                    temperature=0.0, 
                    top_p=0.1,
                )
                return cevap.choices[0].message.content
            return "Bu bilgi sağlanan kılavuzda bulunmamaktadır."

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            asistan_cevabi = loop.run_until_complete(
                ana_islem(soru, MIN_RELEVANCE)
            )
        finally:
            loop.close()

        cevap_alani.markdown(asistan_cevabi)
        st.session_state.mesajlar.append({"role": "assistant", "content": asistan_cevabi})