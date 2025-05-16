"""
glossary_generator.py
A script to automatically generate SEO-optimized glossary pages for placetrends.com
focusing on demographics, business, real estate, and online SEO
"""

import google.generativeai as genai
import pandas as pd
import os
from time import sleep
from datetime import datetime
import re
import yaml
from pathlib import Path
from urllib.parse import quote
from bs4 import BeautifulSoup
import html

class SEOOptimizer:
    """Helper class for SEO optimization"""
    
    @staticmethod
    def create_seo_slug(term):
        """Create SEO-friendly slug from term"""
        # Convert to lowercase and remove special characters
        slug = term.lower()
        # Replace special characters with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        # Ensure slug is not too long (max 60 chars)
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
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.seo_optimizer = SEOOptimizer()

        # Ensure directories exist
        self.glossary_dir = Path("glossary")
        self.glossary_dir.mkdir(exist_ok=True)
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

    def generate_seo_elements(self, term):
        """Generate SEO-optimized elements for the content"""
        try:
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
            seo_elements = yaml.safe_load(seo_response.text)
            return seo_elements
        except Exception as e:
            print(f"Error generating SEO elements for {term}: {e}")
            return None

    def generate_content(self, term):
        """Generate enhanced SEO-optimized content for a glossary term"""
        try:
            # Generate SEO elements first
            seo_elements = self.generate_seo_elements(term)
            
            # Generate definition with keyword optimization
            definition_prompt = f"""
            Provide a clear, concise definition of '{term}' in the context of demographics,
            business strategy, real estate, and online marketing/SEO.
            Naturally incorporate these keywords: {', '.join(seo_elements['secondary_keywords'][:2])}
            Format as a simple definition of 50-75 words.
            Focus on practical business applications and value.
            """
            definition_response = self.model.generate_content(definition_prompt)
            definition = definition_response.text.strip()

            # Generate detailed article with SEO optimization
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

            # Generate enhanced meta content
            meta_prompt = f"""
            Generate SEO metadata incorporating '{term}' and these keywords: {', '.join(seo_elements['secondary_keywords'][:2])}
            1. SEO title (50-60 characters)
            2. Meta description (150-160 characters)
            3. Social media title (65 characters)
            4. Social media description (200 characters)
            Focus on click-through rate optimization and value proposition.
            """
            meta_response = self.model.generate_content(meta_prompt)
            meta_content = yaml.safe_load(meta_response.text)

            # Create the content dictionary with all SEO elements
            content = {
                "term": term,
                "slug": self.seo_optimizer.create_seo_slug(term),
                "definition": definition,
                "article": article,
                "title": meta_content['seo_title'],
                "meta_description": meta_content['meta_description'],
                "social_title": meta_content['social_title'],
                "social_description": meta_content['social_description'],
                "keywords": seo_elements['secondary_keywords'] + seo_elements['lsi_keywords'],
                "primary_keyword": seo_elements['primary_keyword'],
                "schema_markup": self.seo_optimizer.generate_schema_markup({
                    'title': meta_content['seo_title'],
                    'meta_description': meta_content['meta_description'],
                    'keywords': seo_elements['secondary_keywords']
                }),
                "meta_tags": self.seo_optimizer.generate_meta_tags({
                    'title': meta_content['seo_title'],
                    'meta_description': meta_content['meta_description'],
                    'keywords': seo_elements['secondary_keywords'],
                    'slug': self.seo_optimizer.create_seo_slug(term)
                })
            }

            return content

        except Exception as e:
            print(f"Error generating content for {term}: {e}")
            return None

    def save_markdown(self, content):
        """Save content as an SEO-optimized markdown file"""
        filepath = self.glossary_dir / f"{content['slug']}.md"

        with open(filepath, 'w', encoding='utf-8') as f:
            # Write frontmatter
            f.write('---\n')
            frontmatter = {
                'title': content['title'],
                'description': content['meta_description'],
                'date': datetime.now().strftime('%Y-%m-%d'),
                'lastmod': datetime.now().strftime('%Y-%m-%d'),
                'draft': False,
                'tags': content['keywords'],
                'categories': ['Glossary'],
                'slug': content['slug'],
                'seo': {
                    'title': content['title'],
                    'description': content['meta_description'],
                    'canonical': f"https://placetrends.com/glossary/{content['slug']}",
                    'ogTitle': content['social_title'],
                    'ogDescription': content['social_description']
                }
            }
            f.write(yaml.dump(frontmatter))
            f.write('---\n\n')

            # Write SEO meta tags
            f.write('<!-- SEO Meta Tags -->\n')
            f.write(content['meta_tags'])
            f.write('\n\n')

            # Write Schema.org markup
            f.write('<!-- Schema.org Markup -->\n')
            f.write('<script type="application/ld+json">\n')
            f.write(yaml.dump(content['schema_markup']))
            f.write('</script>\n\n')

            # Write content
            f.write(f"## Definition\n\n{content['definition']}\n\n")
            f.write(f"{content['article']}\n")

    def generate_glossary(self, terms):
        """Generate SEO-optimized glossary content for all terms"""
        glossary_data = []

        for term in terms:
            print(f"Generating SEO-optimized content for: {term}")
            content = self.generate_content(term)
            if content:
                glossary_data.append(content)
                self.save_markdown(content)
                sleep(2)  # Rate limiting

        # Save to CSV with SEO metrics
        df = pd.DataFrame(glossary_data)
        csv_path = self.data_dir / f"glossary_data_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(csv_path, index=False)

        return len(glossary_data)

# [Previous terms list remains the same]

def main():
    # [Previous terms list remains the same]

    # Initialize generator with your API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Please set GEMINI_API_KEY environment variable")

    generator = GlossaryGenerator(api_key)

    # Generate SEO-optimized content
    num_generated = generator.generate_glossary(terms)

    print(f"\nSEO-Optimized Content Generation Complete!")
    print(f"Generated {num_generated} glossary entries with full SEO optimization")
    print(f"Files saved in {generator.glossary_dir}")
    print(f"Data backup saved in {generator.data_dir}")

if __name__ == "__main__":
    main()
