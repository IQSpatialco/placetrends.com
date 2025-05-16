"""
glossary_generator.py
A script to automatically generate SEO glossary pages for placetrends.com
"""

import google.generativeai as genai
import pandas as pd
import os
from time import sleep
from datetime import datetime
import re
import yaml
from pathlib import Path

class GlossaryGenerator:
    def __init__(self, api_key):
        # Configure Gemini API
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

        # Ensure glossary directory exists
        self.glossary_dir = Path("glossary")
        self.glossary_dir.mkdir(exist_ok=True)

        # Create data directory for CSV exports
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

    def create_slug(self, term):
        """Create a URL-friendly slug from a term."""
        return re.sub(r'[^a-z0-9]+', '-', term.lower()).strip('-')

    def generate_frontmatter(self, content):
        """Generate YAML frontmatter for markdown files."""
        frontmatter = {
            'title': content['term'],
            'description': content['meta_description'],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'draft': False,
            'tags': ['SEO', 'Demographics', 'Glossary'],
            'categories': ['Glossary'],
            'slug': self.create_slug(content['term'])
        }
        return yaml.dump(frontmatter)

    def generate_content(self, term):
        """Generate content for a glossary term using Gemini API."""
        try:
            # Generate definition
            definition_prompt = f"""
            Provide a clear, concise definition of '{term}' for an SEO glossary focused on demographics in SEO.
            Format the response as a simple definition of 50-75 words.
            """
            definition_response = self.model.generate_content(definition_prompt)
            definition = definition_response.text.strip()

            # Generate detailed article
            article_prompt = f"""
            Write a detailed 800-1000 word article about '{term}' that includes:
            1. Why this concept is important for SEO
            2. How to implement it effectively
            3. Best practices and common mistakes
            4. Include 3-4 real-world examples with hypothetical URLs (use example.com domain)
            5. Include specific actionable tips
            6. Current trends and future implications

            Format the article in markdown with appropriate subheadings (use ### for H3 headers).
            Include internal linking opportunities where relevant.
            """
            article_response = self.model.generate_content(article_prompt)
            article = article_response.text.strip()

            # Generate meta content
            meta_prompt = f"""
            Generate SEO metadata for an article about '{term}':
            1. An SEO-optimized title (max 60 characters)
            2. A compelling meta description (max 160 characters)
            Make them engaging and include the target keyword.
            """
            meta_response = self.model.generate_content(meta_prompt)
            meta_content = meta_response.text.strip()

            # Parse meta content
            meta_lines = meta_content.split('\n')
            title = meta_lines[0][:60] if meta_lines else f"Understanding {term} | SEO Demographics Guide"
            meta_desc = meta_lines[1][:160] if len(meta_lines) > 1 else f"Learn about {term} and its impact on SEO demographics. Comprehensive guide with examples and best practices."

            return {
                "term": term,
                "definition": definition,
                "article": article,
                "title": title,
                "meta_description": meta_desc
            }
        except Exception as e:
            print(f"Error generating content for {term}: {e}")
            return None

    def save_markdown(self, content):
        """Save content as a markdown file with frontmatter."""
        slug = self.create_slug(content['term'])
        filepath = self.glossary_dir / f"{slug}.md"

        with open(filepath, 'w', encoding='utf-8') as f:
            # Write frontmatter
            f.write('---\n')
            f.write(self.generate_frontmatter(content))
            f.write('---\n\n')

            # Write content
            f.write(f"## Definition\n\n{content['definition']}\n\n")
            f.write(f"{content['article']}\n")

    def generate_glossary(self, terms):
        """Generate glossary content for all terms."""
        glossary_data = []

        for term in terms:
            print(f"Generating content for: {term}")
            content = self.generate_content(term)
            if content:
                glossary_data.append(content)
                self.save_markdown(content)
                # Add delay to respect rate limits
                sleep(2)

        # Save to CSV for reference
        df = pd.DataFrame(glossary_data)
        csv_path = self.data_dir / f"glossary_data_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(csv_path, index=False)

        return len(glossary_data)

def main():
    # Your terms list - you can modify this or load from a CSV/JSON file
    terms = [
        "Demographic segmentation in SEO",
        "Targeting keywords for Millennials in SEO",
        "Location-based demographics for local SEO",
        "SEO content tone for Gen Z audiences",
        "Accessibility considerations in SEO for diverse demographics",
        "Age-based keyword targeting",
        "Gender-specific SEO strategies",
        "Income-based audience targeting in SEO",
        "Educational demographics and SEO",
        "Cultural SEO optimization"
    ]

    # Initialize generator with your API key
    # You should store this in an environment variable or config file
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Please set GEMINI_API_KEY environment variable")

    generator = GlossaryGenerator(api_key)

    # Generate content
    num_generated = generator.generate_glossary(terms)

    print(f"\nContent Generation Complete!")
    print(f"Generated {num_generated} glossary entries with full articles")
    print(f"Files saved in {generator.glossary_dir}")
    print(f"Data backup saved in {generator.data_dir}")

if __name__ == "__main__":
    main()
