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

def extract_send_from_pdf(pdf_url):
    try:
        r = requests.get(pdf_url, headers=HEADERS)
        r.raise_for_status()
        pdf_text = extract_text(BytesIO(r.content))

        # Clean common encoding issues
        pdf_text = pdf_text.encode('latin1', 'ignore').decode('utf-8', 'ignore')

        # Combine paragraphs (split by 2+ newlines)
        paragraphs = re.split(r'\n{2,}', pdf_text)
        keywords = ['SEND', 'special educational needs', 'SEN', 'EHCP', 'disabilities', 'autism', 'provision', 'additional needs']

        # Prioritise full paragraphs with multiple keywords
        matched = []
        for para in paragraphs:
            lower = para.lower()
            score = sum(k.lower() in lower for k in keywords)
            if score >= 2 and len(para.split()) > 10:
                matched.append(para.strip())

        if matched:
            return matched[0], None  # Return top-scoring paragraph
        else:
            # Fallback: return up to 3 short keyword mentions
            fallback = [p for p in paragraphs if any(k in p.lower() for k in keywords)]
            return ' '.join(fallback[:2]).strip() if fallback else "No SEND mentions found.", None

    except Exception as e:
        return None, f"PDF error: {str(e)}"

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

            # ✅ Check domain, but allow any valid PDF link format
            if "files.ofsted.gov.uk" not in pdf_url:
                results.append({'URN': urn, 'Error': f"Expected a PDF URL, got: {pdf_url}", 'Provider URL': provider_url})
                pdf_page.close()
                continue

            snippet, err = extract_send_from_pdf(pdf_url)
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