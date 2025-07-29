from playwright.sync_api import sync_playwright

TEST_URN = 100000
PROVIDER_URL = f"https://reports.ofsted.gov.uk/provider/21/{TEST_URN}"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Open visible browser
    page = browser.new_page()
    print(f"🔍 Visiting {PROVIDER_URL}")
    page.goto(PROVIDER_URL)
    page.wait_for_timeout(3000)

    try:
        # ✅ Wait for the "All reports" section
        page.wait_for_selector('"All reports"', timeout=5000)

        # ✅ Print every <a> tag and its attributes
        all_links = page.query_selector_all('a')
        print(f"🔗 Found {len(all_links)} links:")
        for link in all_links:
            href = link.get_attribute('href')
            text = link.inner_text().strip().replace('\n', ' ')
            if href and href.endswith('.pdf'):
                print(f"✅ PDF LINK: {text} → {href}")
            else:
                print(f"  - {text} → {href}")

    except Exception as e:
        print(f"❌ Failed to load or parse: {str(e)}")

    page.wait_for_timeout(5000)  # Let you view the browser
    browser.close()