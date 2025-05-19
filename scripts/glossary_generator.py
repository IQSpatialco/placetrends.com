import os
import logging
import google.generativeai as genai
from pathlib import Path
import time
from bs4 import BeautifulSoup  # For HTML validation

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
GLOSSARY_DIR = os.path.join(os.getcwd(), "glossary")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MAX_RETRIES = 3  # Maximum retries for API calls
RETRY_DELAY = 2  # Initial delay in seconds, will be doubled on each retry

# Create glossary directory if it doesn't exist
os.makedirs(GLOSSARY_DIR, exist_ok=True)

class GlossaryGenerator:
    def __init__(self):
        """Initializes the GlossaryGenerator class."""
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY environment variable is not set")
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)

        # Get available models and log them
        try:
            models = genai.list_models()
            model_names = [model.name for model in models]
            logger.debug(f"Available models: {model_names}")

            # Find a suitable text generation model - look for the latest Gemini model
            # Try specific known models first
            preferred_models = [
                "models/gemini-1.5-pro",
                "models/gemini-1.5-flash",
                "models/gemini-pro",
                "models/gemini-1.0-pro"
            ]
            
            # Try to use one of our preferred models if available
            selected_model = None
            for model_name in preferred_models:
                if model_name in model_names:
                    selected_model = model_name
                    break
            
            # If none of our preferred models are available, try to find any Gemini model
            if not selected_model:
                for model_name in model_names:
                    if "gemini" in model_name.lower() and not "vision" in model_name.lower():
                        selected_model = model_name
                        break
            
            if not selected_model:
                raise ValueError("No suitable text generation models available")
            
            self.model = genai.GenerativeModel(selected_model)
            logger.debug(f"Using model: {selected_model}")

        except Exception as e:
            logger.error(f"Error configuring Gemini API: {str(e)}")
            raise

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

    def _generate_content(self, prompt, term):
        """
        Generates content using the Gemini API with retry logic.

        Args:
            prompt (str): The prompt to send to the Gemini API.
            term (str): The term being processed.

        Returns:
            str: The generated content, or None on failure.
        """
        retries = 0
        delay = RETRY_DELAY
        while retries < MAX_RETRIES:
            try:
                response = self.model.generate_content(prompt)
                if response.text:
                    return response.text
                else:
                    logger.warning(f"Empty response from Gemini API for term: {term}")
                    return None

            except Exception as e:
                logger.error(f"Error generating content for {term} (attempt {retries + 1}): {str(e)}")
                retries += 1
                if retries < MAX_RETRIES:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to generate content for {term} after {MAX_RETRIES} attempts")
                    return None
        return None

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

        html_content = self._generate_content(prompt, term)
        if not html_content:
            return False

        # Validate the generated HTML
        if not self._validate_html(html_content, term):
            return False
        
        # Create a file for the term
        term_filename = term.lower().replace(" ", "-").replace("(", "").replace(")", "")
        file_path = os.path.join(GLOSSARY_DIR, f"{term_filename}.html")
        logger.debug(f"Writing to file: {file_path}")

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"Created glossary page for {term} at {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error writing to file {file_path} for term {term}: {str(e)}")
            return False
        

    def _validate_html(self, html_content, term):
        """
        Validates the generated HTML using BeautifulSoup.

        Args:
            html_content (str): The HTML content to validate.
            term (str):  The term

        Returns:
            bool: True if the HTML is valid, False otherwise.
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Check for essential tags and structure (you can customize this)
            if soup.find('h1') and soup.find('p'):  # Basic check, refine as needed
                return True
            else:
                logger.warning(f"HTML validation failed for {term}: Missing essential tags")
                return False
        except Exception as e:
            logger.error(f"Error validating HTML for {term}: {str(e)}")
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
