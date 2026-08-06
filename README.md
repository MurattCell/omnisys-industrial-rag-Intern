-TR-
# ⚙️ Omnisys Endüstriyel AI - Local Edge RAG

**Ağır Sanayide %100 Çevrimdışı, Güvenli ve Hızlı Arıza Çözümleme Asistanı**

Endüstriyel üretim tesislerinde (haddehane, sinter, izabe vb.) veri güvenliği nedeniyle saha ekipmanlarının internete bağlanması genellikle kısıtlıdır. Omnisys Endüstriyel AI, bulut tabanlı yapay zeka çözümlerinin (ChatGPT vb.) veri sızdırma riskini ortadan kaldırarak **tamamen yerel (Edge)** çalışan bir RAG (Retrieval-Augmented Generation) mimarisi sunar.

Saha teknisyenlerinin binlerce sayfalık PDF kılavuzları içinde spesifik arıza kodlarını (Örn: F30001) ararken kaybettiği kritik üretim zamanını, yapay zeka destekli anlık çözümlemelerle saniyelere indirir.

## 🚀 Öne Çıkan Mühendislik Çözümleri

* **%100 Yerel Veri Gizliliği:** Qwen 2.5 (7B) LLM ve Nomic-Embed-Text vektör modelleri tamamen yerel donanımda çalışır. İnternet bağlantısı gerektirmez.
* **Multimodal Tablo Okuma Yeteneği:** Standart RAG sistemlerinin en büyük zayıflığı olan "PDF içindeki karmaşık endüstriyel tabloları okuyamama" sorunu, `pymupdf4llm` entegrasyonu ile çözülmüştür. Kılavuzdaki tablolar kayıpsız Markdown formatına çevrilerek vektörleştirilir.
* **Karakter Bazlı Kesişimli Dilimleme:** Anlam bütünlüğünün kopmaması için klasik kelime bazlı (word-chunking) yöntemler yerine, satır atlamalarını koruyan overlapping karakter dilimleme algoritması kullanılmıştır.
* **Sıfır Halüsinasyon (Strict Prompting):** Asistan, yalnızca sağlanan PDF kılavuzundaki verileri kullanmak üzere sert dil ve kapsam kilitleriyle (System Prompt) sınırlandırılmıştır.

## 🛠️ Teknoloji Yığını (Tech Stack)

* **Dil Modeli (LLM):** Ollama & Qwen 2.5 (7B)
* **Vektör Veritabanı & Orchestration:** Semantic Kernel
* **Veri Çıkarımı:** PyMuPDF4LLM
* **Arayüz (UI):** Streamlit (Özel Kurumsal Dashboard Tasarımı)
* **Asenkron Yapı:** Python `asyncio`

## ⚙️ Kurulum ve Çalıştırma

## ⚙️ Kurulum ve Çalıştırma Rehberi

Bu proje tamamen yerel (Edge) donanımda çalışacak şekilde tasarlanmıştır.
-EN-
# ⚙️ Omnisys Industrial AI - Local Edge RAG

**100% Offline, Secure, and Fast Fault Resolution Assistant for Heavy Industry**

In industrial production facilities (rolling mills, sinter plants, smelting, etc.), connecting field equipment to the internet is generally restricted due to data security concerns. Omnisys Industrial AI eliminates the data leakage risks associated with cloud-based AI solutions (like ChatGPT) by offering a **completely local (Edge)** RAG (Retrieval-Augmented Generation) architecture.

It reduces the critical production time field technicians lose while searching for specific fault codes (e.g., F30001) within thousands of pages of PDF manuals down to seconds through AI-powered instant analytics.

## 🚀 Prominent Engineering Solutions

* **100% Local Data Privacy:** The Qwen 2.5 (7B) LLM and Nomic-Embed-Text vector models run entirely on local hardware. No internet connection is required.
* **Multimodal Table Reading Capability:** The inability to read complex industrial tables within PDFs, which is a major weakness of standard RAG systems, has been solved via `pymupdf4llm` integration. Tables in the manuals are converted into lossless Markdown format and vectorized.
* **Character-Based Overlapping Chunking:** To maintain semantic integrity, an overlapping character chunking algorithm that preserves line breaks is used instead of classic word-chunking methods.
* **Zero Hallucination (Strict Prompting):** The assistant is restricted with strict language and scope locks (System Prompt) to use only the data provided in the PDF manual.

## 🛠️ Tech Stack

* **Language Model (LLM):** Ollama & Qwen 2.5 (7B)
* **Vector Database & Orchestration:** Semantic Kernel
* **Data Extraction:** PyMuPDF4LLM
* **User Interface (UI):** Streamlit (Custom Corporate Dashboard Design)
* **Asynchronous Architecture:** Python `asyncio`

## ⚙️ Setup and Execution Guide

This project is designed to run entirely on local (Edge) hardware.


### Adım 1/Step 1: Modeli İndirin/Download the Model
Ollama'yı kurduktan sonra terminalinizi açın ve Qwen 2.5 (7B) modelini bilgisayarınıza indirin:
After installing Ollama, open your terminal and download the Qwen 2.5 (7B) model to your computer:
```bash
ollama run qwen2.5:7b

git clone [https://github.com/MurattCell/omnisys-industrial-rag.git](https://github.com/MurattCell/omnisys-industrial-rag.git)
cd omnisys-industrial-rag

python -m venv .venv
.\.venv\Scripts\activate
pip install streamlit openai semantic-kernel pymupdf4llm

streamlit run app.py

