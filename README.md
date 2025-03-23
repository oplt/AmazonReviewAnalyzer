# Amazon Review Analyzer

This guide will help you set up the AmazonReviewAnalyzer project on your local machine, including downloading the required LLM (Large Language Model) and installing dependencies.

## Downloading LLM on Local Machine

1. Go to [Ollama Download Page](https://ollama.com/download).
2. Select your operating system and download Ollama.
3. Click on "Models" and select `deepseek-r1`.
4. Choose the model from the available tags and run the following command in your terminal:
   ```bash
   ollama run deepseek-r1:8b
   ```
 
## Clone repo on your local machine :
5- Generate a project folder and environment in it with Python 3.11
6- On command line go to directory of the project and run this:
```bash 
git clone git@github.com:oplt/AmazonReviewAnalyzer.git --depth 1
```

## Installing dependencies:
6- Go to project directory and run this on command line: pip install -r requirements      
