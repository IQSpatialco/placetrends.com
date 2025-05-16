import google.generativeai as genai
import pandas as pd
import os
from time import sleep
from datetime import datetime
import re
import yaml
from pathlib import Path
import html
import logging
import sys
import traceback

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

class SEOOptimizer:
    """Helper class for SEO optimization"""

    @staticmethod
    def create_seo_slug(term):
        """Create SEO-friendly slug from term"""
        slug = term.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        slug = slug[:60]
        return slug

    @staticmethod
    def generate_schema_markup(content):
        """Generate Schema.org JSON-LD markup"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": content['title'],
            "description": content['meta_description'],
            "keywords": content['keywords'],
            "datePublished": datetime.now().strftime('%Y-%m-%d'),
            "dateModified": datetime.now().strftime('%Y-%m-%d'),
            "author": {
                "@type": "Organization",
                "name": "PlaceTrends"
            },
            "publisher": {
                "@type": "Organization",
                "name": "PlaceTrends",
                "url": "https://placetrends.com"
            }
        }
        return schema

    @staticmethod
    def generate_meta_tags(content):
        """Generate HTML meta tags for SEO"""
        meta_tags = f"""
        <!-- Primary Meta Tags -->
        <meta name="title" content="{html.escape(content['title'])}">
        <meta name="description" content="{html.escape(content['meta_description'])}">
        <meta name="keywords" content="{html.escape(', '.join(content['keywords']))}">

        <!-- Open Graph / Facebook -->
        <meta property="og:type" content="article">
        <meta property="og:title" content="{html.escape(content['title'])}">
        <meta property="og:description" content="{html.escape(content['meta_description'])}">
        <meta property="og:url" content="https://placetrends.com/glossary/{content['slug']}">

        <!-- Twitter -->
        <meta property="twitter:card" content="summary_large_image">
        <meta property="twitter:title" content="{html.escape(content['title'])}">
        <meta property="twitter:description" content="{html.escape(content['meta_description'])}">
        """
        return meta_tags

class GlossaryGenerator:
    def __init__(self, api_key):
        # Configure Gemini API
        logging.info("Initializing GlossaryGenerator")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.seo_optimizer = SEOOptimizer()

        # Ensure directories exist
        self.glossary_dir = Path("glossary")
        self.glossary_dir.mkdir(exist_ok=True)
        logging.info(f"Glossary directory: {self.glossary_dir.absolute()}")

        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        logging.info(f"Data directory: {self.data_dir.absolute()}")

    def generate_seo_elements(self, term):
        """Generate SEO-optimized elements for the content"""
        try:
            logging.info(f"Generating SEO elements for: {term}")
            seo_prompt = f"""
            Generate SEO elements for the term '{term}':
            1. Primary keyword (the main term)
            2. 5-7 related secondary keywords
            3. 3-5 LSI (Latent Semantic Indexing) keywords
            4. A list of internal linking opportunities
            5. Suggested external reference sources
            Format as YAML with clear sections.
            """
            seo_response = self.model.generate_content(seo_prompt)
            seo_text = seo_response.text
            logging.info(f"Received SEO response: {seo_text[:100]}...")

            # Handle potential YAML parsing issues
            try:
                seo_elements = yaml.safe_load(seo_text)
                if not isinstance(seo_elements, dict):
                    logging.warning(f"SEO elements not in expected format: {seo_elements}")
                    # Create a basic structure if parsing fails
                    seo_elements = {
                        "primary_keyword": term,
                        "secondary_keywords": [term, "demographics", "business strategy"],
                        "lsi_keywords": ["analysis", "trends", "data"],
                        "internal_linking": ["demographics", "business", "real estate"],
                        "external_sources": ["Wikipedia", "Census.gov"]
                    }
            except Exception as yaml_error:
                logging.error(f"YAML parsing error: {yaml_error}")
                logging.error(f"Raw YAML content: {seo_text}")
                # Create a basic structure if parsing fails
                seo_elements = {
                    "primary_keyword": term,
                    "secondary_keywords": [term, "demographics", "business strategy"],
                    "lsi_keywords": ["analysis", "trends", "data"],
                    "internal_linking": ["demographics", "business", "real estate"],
                    "external_sources": ["Wikipedia", "Census.gov"]
                }

            return seo_elements
        except Exception as e:
            logging.error(f"Error generating SEO elements for {term}: {e}")
            logging.error(traceback.format_exc())
            # Return a basic structure if generation fails
            return {
                "primary_keyword": term,
                "secondary_keywords": [term, "demographics", "business strategy"],
                "lsi_keywords": ["analysis", "trends", "data"],
                "internal_linking": ["demographics", "business", "real estate"],
                "external_sources": ["Wikipedia", "Census.gov"]
            }

    def generate_content(self, term):
        """Generate enhanced SEO-optimized content for a glossary term"""
        try:
            logging.info(f"Generating content for: {term}")

            # Generate SEO elements first
            seo_elements = self.generate_seo_elements(term)
            if not seo_elements:
                logging.error(f"Failed to generate SEO elements for {term}")
                return None

            # Generate definition with keyword optimization
            logging.info(f"Generating definition for: {term}")
            definition_prompt = f"""
            Provide a clear, concise definition of '{term}' in the context of demographics,
            business strategy, real estate, and online marketing/SEO.
            Naturally incorporate these keywords: {', '.join(seo_elements['secondary_keywords'][:2])}
            Format as a simple definition of 50-75 words.
            Focus on practical business applications and value.
            """
            definition_response = self.model.generate_content(definition_prompt)
            definition = definition_response.text.strip()
            logging.info(f"Definition generated: {len(definition)} characters")

            # Generate detailed article with SEO optimization
            logging.info(f"Generating article for: {term}")
            article_prompt = f"""
            Write a detailed 800-1000 word article about '{term}' that includes:
            1. Natural integration of these keywords: {', '.join(seo_elements['secondary_keywords'])}
            2. Use these LSI keywords where appropriate: {', '.join(seo_elements['lsi_keywords'])}
            3. Include internal linking opportunities to: {', '.join(seo_elements['internal_linking'])}
            4. Cite these authoritative sources: {', '.join(seo_elements['external_sources'])}

            Structure the article with:
            - Introduction (with keyword-rich first paragraph)
            - Why this concept matters for business and ROI
            - Implementation strategies and best practices
            - Real-world examples and case studies
            - Common challenges and solutions
            - Future trends and implications
            - Actionable tips and next steps
            - Conclusion with call-to-action

            Format in markdown with H3 headers (###).
            Optimize for featured snippets and rich results.
            Include relevant statistics and data points.
            """
            article_response = self.model.generate_content(article_prompt)
            article = article_response.text.strip()
            logging.info(f"Article generated: {len(article)} characters")

            # Generate enhanced meta content
            logging.info(f"Generating meta content for: {term}")
            meta_prompt = f"""
            Generate SEO metadata incorporating '{term}' and these keywords: {', '.join(seo_elements['secondary_keywords'][:2])}
            1. SEO title (50-60 characters)
            2. Meta description (150-160 characters)
            3. Social media title (65 characters)
            4. Social media description (200 characters)
            Focus on click-through rate optimization and value proposition.
            Format as YAML with clear labels.
            """
            meta_response = self.model.generate_content(meta_prompt)
            meta_text = meta_response.text

            try:
                meta_content = yaml.safe_load(meta_text)
                if not isinstance(meta_content, dict):
                    logging.warning(f"Meta content not in expected format: {meta_content}")
                    # Create a basic structure if parsing fails
                    meta_content = {
                        "seo_title": f"{term} - Demographics Guide | PlaceTrends",
                        "meta_description": f"Learn about {term} and its impact on business strategy, real estate, and online marketing. Practical insights and actionable tips.",
                        "social_title": f"{term} - Essential Demographics Guide",
                        "social_description": f"Discover how {term} affects business decisions, real estate investments, and marketing strategies. Get practical insights and actionable tips."
                    }
            except Exception as yaml_error:
                logging.error(f"YAML parsing error for meta content: {yaml_error}")
                logging.error(f"Raw YAML content: {meta_text}")
                # Create a basic structure if parsing fails
                meta_content = {
                    "seo_title": f"{term} - Demographics Guide | PlaceTrends",
                    "meta_description": f"Learn about {term} and its impact on business strategy, real estate, and online marketing. Practical insights and actionable tips.",
                    "social_title": f"{term} - Essential Demographics Guide",
                    "social_description": f"Discover how {term} affects business decisions, real estate investments, and marketing strategies. Get practical insights and actionable tips."
                }

            logging.info(f"Meta content generated")

            # Create the content dictionary with all SEO elements
            slug = self.seo_optimizer.create_seo_slug(term)
            logging.info(f"Created slug: {slug}")

            content = {
                "term": term,
                "slug": slug,
                "definition": definition,
                "article": article,
                "title": meta_content.get('seo_title', f"{term} - PlaceTrends"),
                "meta_description": meta_content.get('meta_description', f"Learn about {term} and its impact on business."),
                "social_title": meta_content.get('social_title', f"{term} - PlaceTrends"),
                "social_description": meta_content.get('social_description', f"Discover how {term} affects business decisions."),
                "keywords": seo_elements.get('secondary_keywords', []) + seo_elements.get('lsi_keywords', []),
                "primary_keyword": seo_elements.get('primary_keyword', term),
            }

            # Generate schema markup and meta tags
            content["schema_markup"] = self.seo_optimizer.generate_schema_markup({
                'title': content['title'],
                'meta_description': content['meta_description'],
                'keywords': content['keywords']
            })

            content["meta_tags"] = self.seo_optimizer.generate_meta_tags({
                'title': content['title'],
                'meta_description': content['meta_description'],
                'keywords': content['keywords'],
                'slug': content['slug']
            })

            logging.info(f"Content generation complete for: {term}")
            return content

        except Exception as e:
            logging.error(f"Error generating content for {term}: {e}")
            logging.error(traceback.format_exc())
            return None

    def save_html(self, content):
        """Save content as an SEO-optimized HTML file"""
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
                <meta name="keywords" content="{html.escape(', '.join(content['keywords']))}">
                {content['meta_tags']}
                <script type="application/ld+json">
                    {yaml.dump(content['schema_markup'])}
                </script>
                <link rel="stylesheet" href="../assets/css/style.css"> <!-- Adjust path if needed -->
            </head>
            <body>
                <header>
                    <!-- Your header content -->
                    <div class="logo-container">
                        <img src="../assets/images/logo.avif" alt="PlaceTrends Logo" class="logo">
                        <h1>PlaceTrends Glossary</h1>
                    </div>
                    <nav>
                        <ul>
                            <li><a href="../home.html">Home</a></li>  <!-- Link to your main page -->
                            <li><a href="../index.html">Glossary</a></li>
                            <li><a href="../soon/">Coming Soon</a></li>
                        </ul>
                    </nav>
                </header>

                <div class="main-container">
                    <div class="content-area">
                        <section id="glossary-content">
                            <h2>{html.escape(content['title'])}</h2>
                            <h3>Definition</h3>
                            <p>{content['definition']}</p>
                            <h3>Article</h3>
                            {content['article']}
                        </section>
                    </div>
                </div>

                <footer>
                    <!-- Your footer content -->
                </footer>
            </body>
            </html>
            """

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logging.info(f"Successfully saved HTML file: {filepath}")
            return True
        except Exception as e:
            logging.error(f"Error saving HTML file for {content['term']}: {e}")
            logging.error(traceback.format_exc())
            return False

    def generate_glossary_index(self, terms):
        """Generate the glossary/index.html file with links to all terms"""
        try:
            index_filepath = self.glossary_dir / "index.html"
            logging.info(f"Generating glossary index at: {index_filepath}")

            html_links = ""
            for term in terms:
                slug = self.seo_optimizer.create_seo_slug(term)
                html_links += f'<li><a href="{slug}.html">{html.escape(term)}</a></li>\n'

            index_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>PlaceTrends Glossary</title>
                <link rel="stylesheet" href="../assets/css/style.css"> <!-- Adjust path if needed -->
            </head>
            <body>
                <header>
                    <!-- Your header content -->
                    <div class="logo-container">
                        <img src="../assets/images/logo.avif" alt="PlaceTrends Logo" class="logo">
                        <h1>PlaceTrends Glossary</h1>
                    </div>
                    <nav>
                        <ul>
                            <li><a href="../home.html">Home</a></li>  <!-- Link to your main page -->
                            <li><a href="#">Glossary</a></li>
                            <li><a href="../soon/">Coming Soon</a></li>
                        </ul>
                    </nav>
                </header>

                <div class="main-container">
                    <div class="content-area">
                        <section id="glossary-content">
                            <h2>Glossary</h2>
                            <ul>
                                {html_links}
                            </ul>
                        </section>
                    </div>
                </div>

                <footer>
                    <!-- Your footer content -->
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
            logging.error(traceback.format_exc())
            return False

    def generate_glossary(self, terms):
        """Generate SEO-optimized glossary content for all terms"""
        glossary_data = []
        successful_terms = []

        logging.info(f"Starting glossary generation for {len(terms)} terms")

        for i, term in enumerate(terms):
            logging.info(f"[{i+1}/{len(terms)}] Processing term: {term}")
            try:
                content = self.generate_content(term)
                if content:
                    glossary_data.append(content)
                    if self.save_html(content):
                        successful_terms.append(term)
                        logging.info(f"✓ Successfully processed term: {term}")
                    else:
                        logging.warning(f"✗ Failed to save HTML for term: {term}")
                else:
                    logging.warning(f"✗ Failed to generate content for term: {term}")

                # Add a delay to avoid rate limiting
                sleep(5)  # Increased from 2 to 5 seconds
            except Exception as e:
                logging.error(f"Unexpected error processing term '{term}': {e}")
                logging.error(traceback.format_exc())

        # Generate the glossary index page with all terms (even if some failed)
        # This ensures the index has links to all intended pages
        logging.info(f"Generating glossary index with {len(terms)} terms")
        self.generate_glossary_index(terms)

        # Save to CSV with SEO metrics for successful terms
        if glossary_data:
            try:
                df = pd.DataFrame(glossary_data)
                csv_path = self.data_dir / f"glossary_data_{datetime.now().strftime('%Y%m%d')}.csv"
                df.to_csv(csv_path, index=False)
                logging.info(f"Saved data to CSV: {csv_path}")
            except Exception as e:
                logging.error(f"Error saving CSV data: {e}")
                logging.error(traceback.format_exc())

        logging.info(f"Glossary generation complete!")
        logging.info(f"Successfully processed {len(successful_terms)} out of {len(terms)} terms")
        return len(successful_terms)

def main():
    # Define terms list - using a smaller list for testing
    terms = [
        "Demographic Segmentation for Business Strategy",
        "Age-Based Marketing in Real Estate",
        "Gender-Specific Product Targeting Online",
        "Income-Based Real Estate Investment Analysis",
        "Educational Attainment and Business Location",
        "Cultural Demographics in International SEO",
        "Location-Based Business Demographics",
        "Urban vs. Rural Market Segmentation",
        "Multilingual SEO for Global Business",
        "Ethnicity and Targeted Advertising"
    ]

    # Initialize generator with your API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logging.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("Please set GEMINI_API_KEY environment variable")

    logging.info(f"API key found, length: {len(api_key)}")
    generator = GlossaryGenerator(api_key)

    # Generate SEO-optimized content
    num_generated = generator.generate_glossary(terms)

    logging.info(f"\nSEO-Optimized Content Generation Complete!")
    logging.info(f"Generated {num_generated} glossary entries with full SEO optimization")
    logging.info(f"Files saved in {generator.glossary_dir}")
    logging.info(f"Data backup saved in {generator.data_dir}")

if __name__ == "__main__":
    main()
