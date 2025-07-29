import pandas as pd
import re
import requests
import os
from io import BytesIO
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

HEADERS = {'User-Agent': 'Mozilla/5.0'}

# ========== PDF EXTRACT FUNCTIONS ==========

def extract_send_from_pdf_fitz(pdf_url):
    import fitz  # PyMuPDF
    try:
        print(f"🟡 Trying FITZ on: {pdf_url}")
        r = requests.get(pdf_url, headers=HEADERS)
        r.raise_for_status()
        doc = fitz.open(stream=r.content, filetype="pdf")

        full_text = ""
        for page in doc:
            full_text += page.get_text()

        # Encode/decode to remove messy characters
        full_text = full_text.encode('latin1', errors='ignore').decode('utf-8', errors='ignore')

        replacements = {
            '‚Äô': "'", 'Äô': "'", 'â€“': '-', 'â€”': '-', 'ÔÅÆ': '-', 'â€˜': "'",
            'â€™': "'", 'â€œ': '"', 'â€': '"', 'Â': ''
        }
        for bad, good in replacements.items():
            full_text = full_text.replace(bad, good)

        full_text = re.sub(r'[●•]', '-', full_text)
        full_text = re.sub(r'\s{2,}', ' ', full_text).strip()

        paragraphs = re.split(r'(?<=[.?!])\s{1,}(?=[A-Z])', full_text)
        paragraphs = [p.strip() for p in paragraphs if len(p.strip().split()) > 10]

        keywords = [
            'SEND', 'SEN', 'EHCP', 'special educational needs', 'disabilities',
            'speech', 'therapist', 'support', 'identified', 'curriculum', 'provision',
            'adjustments', 'resources', 'progress', 'targets', 'plans', 'intervention'
        ]
        actionable_verbs = ['support', 'adapt', 'plan', 'identified', 'provide', 'ensure']

        ranked = []
        for i, para in enumerate(paragraphs):
            score = sum(k.lower() in para.lower() for k in keywords)
            action_hits = sum(v in para.lower() for v in actionable_verbs)
            if score + action_hits > 2:
                ranked.append((score + action_hits - 0.1 * i, para))

        ranked.sort(reverse=True)

        if ranked:
            top_paras = [para for _, para in ranked[:3]]
            joined = '\n\n'.join(top_paras)
            print(f"✅ FITZ selected {len(top_paras)} paragraph(s): {joined[:150]}...")
            return joined, None
        else:
            return "No strong SEND paragraph match found.", None

    except Exception as e:
        return None, f"FITZ error: {str(e)}"


def extract_send_from_pdf_pdfminer(pdf_url):
    from pdfminer.high_level import extract_text
    try:
        print(f"🔸 Falling back to pdfminer: {pdf_url}")
        r = requests.get(pdf_url, headers=HEADERS)
        r.raise_for_status()
        pdf_text = extract_text(BytesIO(r.content))

        keywords = ['SEND', 'special educational needs', 'SEN', 'EHCP', 'disabilities', 'autism']
        sentences = re.split(r'(?<=[.!?]) +', pdf_text)
        matches = [s.strip() for s in sentences if any(k.lower() in s.lower() for k in keywords)]
        return ' '.join(matches[:5]) if matches else "No SEND mentions found.", None
    except Exception as e:
        return None, f"PDFMiner error: {str(e)}"


# ========== SCRAPER RUNNER ==========

def scrape_from_csv(input_csv, output_csv, playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    results = []

    urn_list = pd.read_csv(input_csv)['URN'].tolist()

    for urn in urn_list:
        print(f"🔍 Searching URN: {urn}")
        search_url = f"https://reports.ofsted.gov.uk/search?q={urn}"

        try:
            page.goto(search_url, timeout=10000)
        except PlaywrightTimeoutError:
            results.append({'URN': urn, 'Error': 'Search timeout'})
            continue

        try:
            link = page.query_selector('a[href^="/provider/"]')
            if not link:
                results.append({'URN': urn, 'Error': 'No provider link found'})
                continue

            provider_url = "https://reports.ofsted.gov.uk" + link.get_attribute('href')
            print(f"🔗 Visiting: {provider_url}")
            page.goto(provider_url, timeout=10000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2500)

            with context.expect_page() as new_tab_info:
                button = page.query_selector('a:has-text("School inspection")')
                if not button:
                    results.append({'URN': urn, 'Error': 'No inspection link found', 'Provider URL': provider_url})
                    continue
                button.click()
            pdf_page = new_tab_info.value
            pdf_page.wait_for_load_state()
            pdf_url = pdf_page.url

            if "files.ofsted.gov.uk" not in pdf_url:
                results.append({'URN': urn, 'Error': f"Expected a PDF URL, got: {pdf_url}", 'Provider URL': provider_url})
                pdf_page.close()
                continue

            snippet, err = extract_send_from_pdf_fitz(pdf_url)
            if not snippet or "No strong" in snippet or (err and "fitz" in err.lower()):
                snippet, err = extract_send_from_pdf_pdfminer(pdf_url)

            pdf_page.close()

            results.append({
                'URN': urn,
                'SEND Narrative Snippet': snippet if snippet else '',
                'Provider URL': provider_url,
                'PDF URL': pdf_url,
                'Error': err if err else ''
            })

        except Exception as e:
            results.append({'URN': urn, 'Error': str(e)})

        page.wait_for_timeout(500)

    browser.close()
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"✅ Saved to {output_csv}")


# ========== MAIN BATCH RUN ==========

if __name__ == "__main__":
    input_chunks = [
        "urn_chunks/urn_chunk_1.csv",
        "urn_chunks/urn_chunk_2.csv",
        "urn_chunks/urn_chunk_3.csv"
    ]

    with sync_playwright() as p:
        for i, chunk_path in enumerate(input_chunks, 1):
            output_path = f"send_scrape_results_{i}.csv"
            print(f"\n🚀 Processing {chunk_path}")
            scrape_from_csv(chunk_path, output_path, p)