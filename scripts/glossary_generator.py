import os
import logging
import google.generativeai as genai
from pathlib import Path

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
GLOSSARY_DIR = os.path.join(os.getcwd(), "glossary")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

logger.debug(f"Script started, working directory: {os.getcwd()}")
logger.debug(f"GEMINI_API_KEY present: {'Yes' if GEMINI_API_KEY else 'No'}")
logger.debug(f"GLOSSARY_DIR path: {GLOSSARY_DIR}")
logger.debug(f"GLOSSARY_DIR exists: {os.path.exists(GLOSSARY_DIR)}")

# Create glossary directory if it doesn't exist
os.makedirs(GLOSSARY_DIR, exist_ok=True)
logger.debug(f"After creation, GLOSSARY_DIR exists: {os.path.exists(GLOSSARY_DIR)}")

class GlossaryGenerator:
    def __init__(self):
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY environment variable is not set")
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        logger.debug("Gemini API configured successfully")
        
        # List of terms to generate glossary pages for
        self.terms = [
            "Location Intelligence",
            "Geospatial Analysis",
            "Spatial Data",
            "Geographic Information System (GIS)",
            "Geocoding",
            "Reverse Geocoding",
            "Point of Interest (POI)",
            "Trade Area",
            "Catchment Area",
            "Isochrone",
            "Heatmap",
            "Choropleth Map",
            "Spatial Clustering",
            "Spatial Interpolation",
            "Spatial Autocorrelation",
            "Spatial Regression",
            "Spatial Optimization",
            "Spatial Interaction",
            "Spatial Network Analysis",
            "Spatial Temporal Analysis",
            "Spatial Big Data",
            "Spatial Machine Learning",
            "Spatial AI",
            "Spatial Data Mining",
            "Spatial Data Science",
            "Spatial Statistics",
            "Spatial Econometrics",
            "Spatial Modeling",
            "Spatial Simulation",
            "Spatial Visualization",
            "Spatial Decision Support System",
            "Spatial Planning",
            "Spatial Marketing",
            "Spatial Retail",
            "Spatial Real Estate",
            "Spatial Healthcare",
            "Spatial Finance",
            "Spatial Insurance",
            "Spatial Logistics",
            "Spatial Transportation",
            "Spatial Urban Planning",
            "Spatial Rural Planning",
            "Spatial Environmental Planning",
            "Spatial Natural Resource Management",
            "Spatial Disaster Management",
            "Spatial Emergency Management",
            "Spatial Public Safety",
            "Spatial Public Health",
            "Spatial Education",
            "Spatial Government",
        ]
        logger.debug(f"Number of terms defined: {len(self.terms)}")

    def generate_glossary_page(self, term):
        """Generate a glossary page for a given term using Gemini API."""
        logger.debug(f"Generating glossary page for term: {term}")
        
        # Create a prompt for Gemini
        prompt = f"""
        Create a comprehensive glossary entry for the term "{term}" in the context of location intelligence and geospatial analysis.
        
        The entry should include:
        1. A clear, concise definition (1-2 sentences)
        2. A more detailed explanation (3-4 sentences)
        3. Practical applications or use cases (3-5 bullet points)
        4. Related terms or concepts (3-5 terms)
        
        Format the response as HTML that can be directly included in a webpage. Use appropriate HTML tags for structure.
        The HTML should have a clean, professional appearance suitable for a technical glossary.
        Do not include <!DOCTYPE>, <html>, <head>, or <body> tags - just the content HTML.
        
        Start with an <h1> tag for the term, followed by the definition and explanation in <p> tags.
        Use <ul> and <li> tags for the applications and related terms sections.
        Include appropriate <h2> or <h3> tags for section headings.
        """
        
        try:
            # Generate content using Gemini
            response = self.model.generate_content(prompt)
            html_content = response.text
            logger.debug(f"Successfully generated content for {term}, length: {len(html_content)}")
            
            # Create a file for the term
            term_filename = term.lower().replace(" ", "-").replace("(", "").replace(")", "")
            file_path = os.path.join(GLOSSARY_DIR, f"{term_filename}.html")
            logger.debug(f"Writing to file: {file_path}")
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            logger.info(f"Created glossary page for {term} at {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error generating glossary page for {term}: {str(e)}")
            return False

    def generate_all_pages(self):
        """Generate glossary pages for all terms."""
        logger.info(f"Starting to generate {len(self.terms)} glossary pages")
        success_count = 0
        
        for term in self.terms:
            if self.generate_glossary_page(term):
                success_count += 1
        
        logger.info(f"Generated {success_count} out of {len(self.terms)} glossary pages")
        return success_count

if __name__ == "__main__":
    try:
        logger.info("Starting glossary generation process")
        generator = GlossaryGenerator()
        pages_generated = generator.generate_all_pages()
        logger.info(f"Glossary generation completed. Generated {pages_generated} pages.")
    except Exception as e:
        logger.error(f"Error in glossary generation process: {str(e)}")
        raise
