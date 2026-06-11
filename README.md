# OWASP for GenAI

## Overview

This repository contains the implementation and demonstration platform developed as part of our OWASP for GenAI capstone project. The project investigates security vulnerabilities in Large Language Models (LLMs), evaluates their real-world impact, and demonstrates practical mitigation strategies through an interactive AI-powered career portal.

The repository serves two primary purposes:

1. **Vulnerability Research** – Experiments and findings related to LLM security vulnerabilities, including model poisoning, prompt injection, sensitive information disclosure, improper output handling, and model theft.
2. **Career Portal Demonstration Platform** – A full-stack web application that allows users to interact with AI-powered career services while observing how identified vulnerabilities can affect system behavior and how mitigations reduce risk.

---

## System Architecture

The application follows a distributed cloud architecture deployed on AWS.

### Frontend

- React-based web application
- Hosted using AWS S3 static website hosting
- Provides interfaces for resume analysis and AI chatbot interaction

### Backend

- Flask API deployed on AWS EC2
- Handles business logic, request processing, and communication between services
- Implements security controls and mitigation strategies

### AI Inference Layer

- Dedicated EC2 instance hosting Ollama
- Dedicated EC2 instance hosting a poisoned Mistral model
- Backend communicates with inference services through HTTP APIs
- Supports comparison between vulnerable and mitigated model behavior
  
---

## Technology Stack

### Frontend

- React
- TypeScript
- HTML/CSS

### Backend

- Python
- Flask
- REST APIs

### AI & Machine Learning

- Ollama
- Mistral 7B Instruct
- Custom poisoned (fine-tuned) Mistral 7B

### Cloud Infrastructure

- AWS S3
- AWS EC2

---

## Research Methodology

Our research process follows six primary phases:

1. Identify relevant LLM security vulnerabilities.
2. Review academic and industry literature.
3. Develop proof-of-concept attacks.
4. Integrate attack scenarios into the career portal.
5. Implement mitigation techniques.
6. Evaluate and compare system behavior before and after mitigation.

---

## Vulnerabilities Investigated

The project explores several categories of LLM security risks, including:

- Prompt Injection
- Retrieval-Augmented Generation (RAG) Manipulation
- Data and Model Poisoning
- Sensitive Information Disclosure
- Improper Output Handling
- Model Theft

Each vulnerability includes:

- Background research
- Threat analysis
- Proof-of-concept demonstrations
- Mitigation recommendations

---

## Educational Purpose

This project was developed for educational and research purposes to improve understanding of AI security risks and defensive techniques. The demonstrations are intended to help students, researchers, and developers better understand the challenges involved in deploying secure AI systems.

---

## Contributors

- Amit Guha | guhaa@oregonstate.edu  
- Jackson Miller | milljac8@oregonstate.edu  
- Jared Yin | yinja@oregonstate.edu  
- Justin Lee | leejusti@oregonstate.edu  
- Ohm Thakor | thakoro@oregonstate.edu 

---

## License
[MIT](https://choosealicense.com/licenses/mit/)
