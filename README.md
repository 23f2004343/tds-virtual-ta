# 🤖 TDS Virtual TA

This project is a **Virtual Teaching Assistant** designed for the *Tools in Data Science (TDS)* course offered by **IIT Madras' Online BSc in Data Science** program. It aims to reduce the workload of human TAs by automatically answering frequently asked student questions using course content and Discourse forum discussions.

The API accepts a natural language question (with optional image attachments) and responds with a concise answer. It also includes supporting links to relevant Discourse threads or course content when available. This system is powered by OpenAI’s GPT models and utilizes scraped data for grounding.

The application is built with **FastAPI** and exposes a public API endpoint that can be evaluated using PromptFoo. It takes in a question via a simple POST request and outputs an intelligent response. The backend includes a scraping component for fetching and processing data from the TDS Discourse forum between January and April 2025, which is used to guide the model’s answers.

This project has been structured with best practices, including modular APIs, utility functions, environmental configuration, and automated testing. It’s designed to be deployed easily on platforms like **Render** or exposed via **ngrok** during development. By combining scraping, NLP, and API design, this project serves as a valuable assistant to students navigating the TDS course.
