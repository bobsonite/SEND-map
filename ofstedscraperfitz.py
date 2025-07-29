from playwright.sync_api import sync_playwright
import pandas as pd
import re
import requests
from io import BytesIO
from pdfminer.high_level import extract_text

HEADERS = {'User-Agent': 'Mozilla/5.0'}

URN_LIST = [
    100000, 103682, 106818, 100049, 100050,
    100001, 100015, 100051, 105022, 100052
]

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

        # 🔧 Clean stray encoding artifacts early
        full_text = full_text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')

        full_text = re.sub(r'[●•]', '-', full_text)
        full_text = re.sub(r'\s{2,}', ' ', full_text).strip()

        # 🔎 Break into paragraphs for scoring
        raw_paragraphs = re.split(r'(?<=[.?!])\s{1,}(?=[A-Z])', full_text)
        paragraphs = [p.strip() for p in raw_paragraphs if len(p.strip().split()) > 10]

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

            # 🧼 Final cleanup on joined text
            import unicodedata
            joined = unicodedata.normalize("NFKD", joined)
            joined = joined.encode("ascii", errors="ignore").decode("ascii", errors="ignore")

            print(f"✅ FITZ selected {len(top_paras)} paragraph(s):\n{joined[:150]}...")
            return joined, None
        else:
            return "No strong SEND paragraph match found.", None

    except Exception as e:
        return None, f"FITZ error: {str(e)}"

def extract_send_from_pdf_pdfminer(pdf_url):
    try:
        print(f"🟡 Falling back to pdfminer: {pdf_url}")
        r = requests.get(pdf_url, headers=HEADERS)
        r.raise_for_status()
        pdf_text = extract_text(BytesIO(r.content))

        keywords = ['SEND', 'special educational needs', 'SEN', 'EHCP', 'disabilities', 'autism']
        sentences = re.split(r'(?<=[.!?]) +', pdf_text)
        matches = [s.strip() for s in sentences if any(k.lower() in s.lower() for k in keywords)]
        return ' '.join(matches[:5]) if matches else "No SEND mentions found.", None
    except Exception as e:
        return None, f"PDFMiner error: {str(e)}"

def scrape_ofsted_reports(playwright):
    browser = playwright.chromium.launch(headless=False, slow_mo=250)
    context = browser.new_context()
    page = context.new_page()
    results = []

    for urn in URN_LIST:
        print(f"🔍 Searching URN: {urn}")
        search_url = f"https://reports.ofsted.gov.uk/search?q={urn}"
        page.goto(search_url)
        page.wait_for_timeout(1500)

        try:
            link = page.query_selector('a[href^="/provider/"]')
            if not link:
                results.append({'URN': urn, 'Error': 'No provider link found'})
                continue

            provider_url = "https://reports.ofsted.gov.uk" + link.get_attribute('href')
            print(f"🔗 Visiting: {provider_url}")
            page.goto(provider_url)
            page.wait_for_timeout(2000)

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

            # Try FITZ first
            snippet, err = extract_send_from_pdf_fitz(pdf_url)

            # If FITZ fails or returns weak match, fall back to PDFMiner
            if not snippet or "No strong" in snippet or (err and "fitz" in err.lower()):
                print(f"⚠️ FITZ fallback triggered for URN {urn}")
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

        page.wait_for_timeout(1000)

    browser.close()
    return results

# Run everything
with sync_playwright() as p:
    rows = scrape_ofsted_reports(p)
    df = pd.DataFrame(rows)
    df.to_csv('ofsted_send_playwright_output.csv', index=False)
    print("✅ Done. Saved to ofsted_send_playwright_output.csv")