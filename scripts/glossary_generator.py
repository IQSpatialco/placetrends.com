import google.generativeai as genai
import os
from datetime import datetime
import re
import yaml
from pathlib import Path
import html
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

class GlossaryGenerator:
    def __init__(self, api_key):
        # Configure Gemini API
        logging.info("Initializing GlossaryGenerator")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

        # Ensure directories exist
        self.glossary_dir = Path("glossary")
        self.glossary_dir.mkdir(exist_ok=True)
        logging.info(f"Glossary directory: {self.glossary_dir.absolute()}")

    def create_seo_slug(self, term):
        """Create SEO-friendly slug from term"""
        slug = term.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        slug = slug[:60]
        return slug

    def generate_simple_content(self, term):
        """Generate simple content for a glossary term"""
        try:
            logging.info(f"Generating simple content for: {term}")

            # Generate a simple definition
            definition_prompt = f"Provide a clear, concise definition of '{term}' in 2-3 sentences."
            definition_response = self.model.generate_content(definition_prompt)
            definition = definition_response.text.strip()

            # Generate a simple article
            article_prompt = f"Write a short article about '{term}' in 3-4 paragraphs."
            article_response = self.model.generate_content(article_prompt)
            article = article_response.text.strip()

            # Create content dictionary
            content = {
                "term": term,
                "slug": self.create_seo_slug(term),
                "definition": definition,
                "article": article,
                "title": f"{term} - PlaceTrends Glossary",
                "meta_description": f"Learn about {term} and its impact on business and demographics."
            }

            logging.info(f"Content generation complete for: {term}")
            return content

        except Exception as e:
            logging.error(f"Error generating content for {term}: {e}")
            return None

    def save_html(self, content):
        """Save content as an HTML file"""
        try:
            filepath = self.glossary_dir / f"{content['slug']}.html"
            logging.info(f"Saving HTML file to: {filepath}")

            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{html.escape(content['title'])}</title>
                <meta name="description" content="{html.escape(content['meta_description'])}">
                <link rel="stylesheet" href="../assets/css/style.css">
            </head>
            <body>
                <header>
                    <div class="logo-container">
                        <img src="../assets/images/logo.avif" alt="PlaceTrends Logo" class="logo">
                        <h1>PlaceTrends Glossary</h1>
                    </div>
                    <nav>
                        <ul>
                            <li><a href="../home.html">Home</a></li>
                            <li><a href="../index.html">Glossary</a></li>
                            <li><a href="../soon/">Coming Soon</a></li>
                        </ul>
                    </nav>
                </header>

                <div class="main-container">
                    <div class="content-area">
                        <section id="glossary-content">
                            <h2>{html.escape(content['term'])}</h2>
                            <h3>Definition</h3>
                            <p>{content['definition']}</p>
                            <h3>Article</h3>
                            {content['article']}
                            <p><a href="index.html">Back to Glossary</a></p>
                        </section>
                    </div>
                </div>

                <footer>
                    <p>&copy; {datetime.now().year} PlaceTrends</p>
                </footer>
            </body>
            </html>
            """

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logging.info(f"Successfully saved HTML file: {filepath}")
            logging.info(f"File exists after saving: {filepath.exists()}")
            return True

        except Exception as e:
            logging.error(f"Error saving HTML file for {content['term']}: {e}")
            return False

    def generate_glossary_index(self, terms):
        """Generate the glossary/index.html file with links to all terms"""
        try:
            index_filepath = self.glossary_dir / "index.html"
            logging.info(f"Generating glossary index at: {index_filepath}")

            html_links = ""
            for term in terms:
                slug = self.create_seo_slug(term)
                html_links += f'<li><a href="{slug}.html">{html.escape(term)}</a></li>\n'

            index_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>PlaceTrends Glossary</title>
                <link rel="stylesheet" href="../assets/css/style.css">
            </head>
            <body>
                <header>
                    <div class="logo-container">
                        <img src="../assets/images/logo.avif" alt="PlaceTrends Logo" class="logo">
                        <h1>PlaceTrends Glossary</h1>
                    </div>
                    <nav>
                        <ul>
                            <li><a href="../home.html">Home</a></li>
                            <li><a href="#">Glossary</a></li>
                            <li><a href="../soon/">Coming Soon</a></li>
                        </ul>
                    </nav>
                </header>

                <div class="main-container">
                    <div class="content-area">
                        <section id="glossary-content">
                            <h2>Glossary of Terms</h2>
                            <ul>
                                {html_links}
                            </ul>
                        </section>
                    </div>
                </div>

                <footer>
                    <p>&copy; {datetime.now().year} PlaceTrends</p>
                </footer>
            </body>
            </html>
            """

            with open(index_filepath, 'w', encoding='utf-8') as f:
                f.write(index_content)

            logging.info(f"Successfully generated glossary index: {index_filepath}")
            return True

        except Exception as e:
            logging.error(f"Error generating glossary index: {e}")
            return False

    def generate_glossary(self, terms):
        """Generate glossary content for all terms"""
        successful_terms = []

        logging.info(f"Starting glossary generation for {len(terms)} terms")

        for i, term in enumerate(terms):
            logging.info(f"[{i+1}/{len(terms)}] Processing term: {term}")

            # Generate content
            content = self.generate_simple_content(term)
            if content:
                # Save HTML file
                if self.save_html(content):
                    successful_terms.append(term)
                    logging.info(f"✓ Successfully processed term: {term}")
                else:
                    logging.warning(f"✗ Failed to save HTML for term: {term}")
            else:
                logging.warning(f"✗ Failed to generate content for term: {term}")

        # Generate the glossary index page
        self.generate_glossary_index(terms)

        logging.info(f"Glossary generation complete!")
        logging.info(f"Successfully processed {len(successful_terms)} out of {len(terms)} terms")
        return len(successful_terms)

def main():
    # Define a small list of terms for testing
    terms = [
        "Demographic Segmentation",
        "Age-Based Marketing",
        "Income Demographics"
    ]

    # Initialize generator with API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logging.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("Please set GEMINI_API_KEY environment variable")

    logging.info(f"API key found, length: {len(api_key)}")
    generator = GlossaryGenerator(api_key)

    # Generate glossary content
    num_generated = generator.generate_glossary(terms)

    logging.info(f"\nGlossary Generation Complete!")
    logging.info(f"Generated {num_generated} glossary entries")
    logging.info(f"Files saved in {generator.glossary_dir}")

if __name__ == "__main__":
    main()
