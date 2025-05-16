name: Generate Glossary

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          token: ${{ secrets.REPO_ACCESS_TOKEN }}
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install google-generativeai

      - name: Run glossary generator
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python scripts/glossary_generator.py

      - name: List generated files
        run: |
          echo "Generated files in glossary directory:"
          ls -la glossary/
          echo "Number of files in glossary directory:"
          find glossary -type f | wc -l

      - name: Debug file content
        run: |
          echo "Checking content of a sample file (if it exists):"
          if [ -f "glossary/demographic-segmentation.html" ]; then
            head -n 20 "glossary/demographic-segmentation.html"
          else
            echo "Sample file does not exist"
          fi

      - name: Commit and push changes
        run: |
          git config --global user.name "GitHub Actions"
          git config --global user.email "actions@github.com"
          
          # Show current status
          git status
          
          # Add all files in the glossary directory
          git add -A
          
          # Show what's staged for commit
          git status
          
          # Commit if there are changes
          git diff --staged --quiet || git commit -m "Update glossary pages [skip ci]"
          
          # Pull with rebase to avoid conflicts
          git pull --rebase origin main
          
          # Push changes
          git push https://${{ secrets.REPO_ACCESS_TOKEN }}@github.com/IQSpatialco/placetrends.com.git main
