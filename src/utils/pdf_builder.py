import os
import markdown
from playwright.sync_api import sync_playwright

def compile_pdf(state: dict) -> dict:
    md_content = state.get("tailored_resume_markdown", "")
    job_id = state.get("job_id", "resume")
    
    # Convert Markdown to HTML
    html_body = markdown.markdown(md_content, extensions=['tables'])
    
    # Wrap the body in a full HTML document with inline CSS
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @page {{ margin: 0.75in; size: letter; }}
        body {{ 
            font-family: Arial, Helvetica, sans-serif; 
            font-size: 11pt; 
            line-height: 1.4;
            color: #000000;
        }}
        h1, h2, h3 {{ color: #000000; margin-bottom: 5px; }}
        h1 {{ font-size: 16pt; text-align: center; border-bottom: 1px solid #000; padding-bottom: 5px; }}
        h2 {{ font-size: 13pt; text-transform: uppercase; border-bottom: 1px solid #ccc; margin-top: 15px; }}
        ul {{ margin-top: 2px; padding-left: 20px; }}
        li {{ margin-bottom: 3px; }}
    </style>
    </head>
    <body>
    {html_body}
    </body>
    </html>
    """
    
    output_dir = "data/generated_resumes"
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f"{job_id}_tailored.pdf")
    
    # Generate PDF using Playwright (synchronous API)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(full_html)
        page.pdf(path=pdf_path, format="Letter", print_background=True)
        browser.close()
    
    print(f"[PDF Compiler] Compiled ATS-compliant PDF via Playwright: {pdf_path}")
    return {"pdf_path": pdf_path}