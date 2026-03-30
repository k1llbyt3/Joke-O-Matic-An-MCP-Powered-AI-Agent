# 🎤 Joke-O-Matic 9000: MCP Edition
> **An AI Comedian that bridges the gap between LLMs and real-world data.**

---

## 🚀 Live Demo
**[Experience the Comedy Here!](https://joke-o-matic-an-mcp-powered-ai-agent-267460236055.europe-west1.run.app/)**
*(Hosted on Google Cloud Run)*

---

## 🌟 Project Overview
Developed for the **Google Gen AI Academy (March 2026)**, this project demonstrates a high-performance integration between the **Google Agent Development Kit (ADK)** and the **Model Context Protocol (MCP)**. 

### 💡 The Innovation
Unlike standard chatbots, **Joke-O-Matic 9000** doesn't just guess jokes. It uses a dedicated tool-calling architecture to fetch live content from external APIs, ensuring every punchline is fresh and data-driven.

## 🛠️ Features & UI
* **Agentic Intelligence:** Powered by `gemini-2.5-flash` for witty, high-energy delivery.
* **Standard Protocol:** Implements **MCP (Standard Input/Output)** for bulletproof tool communication.
* **Premium Dashboard:** A custom-built **Glassmorphism UI** featuring:
    * 🤖 **Floating Robot Avatar** for an interactive feel.
    * 💭 **Real-time Thinking Indicator** to improve User Experience.
    * 🎤 **Drop Mic Exit** for a grand finale to your session.

## 🏗️ Technical Architecture
This app uses a **Cloud-Native** approach:
* **Frontend/Agent:** FastAPI handled by the Google ADK Runner.
* **Toolset:** A secure MCP server fetching data via `requests`.
* **Deployment:** Containerized via Docker for global scalability on Google Cloud.

## 📂 Repository Contents
* `agent.py`: The brain of the operation, managing UI and LLM logic.
* `server.py`: The specialized MCP tool for joke retrieval.
* `Dockerfile`: The blueprint for our Google Cloud environment.
* `requirements.txt`: The essential library stack (FastAPI, ADK, etc.).

---
**Developed by Adwaith** *Location: India* | *Track 2: Google Gen AI Academy 2026*
