# ANVIL - Feature Documentation

This document provides a breakdown of the key features of the ANVIL application, as demonstrated in the provided interface figures.

## Figure 1: Welcome Screen (Home)
The entry point of the application provides a clean and focused user experience.
* **Mode Selection:** Users are greeted with a clear choice between two primary learning modes:
  * **Assistant:** For querying and discussing study materials.
  * **Quiz Me!:** For testing knowledge through AI-generated questions.

## Figure 2: Quiz Mode (Multiple Choice)
The primary interface for taking generated quizzes.
* **AI-Generated Quiz Interface:** Displays questions derived from the user's study materials, offering multiple-choice options (A, B, C, D) for quick assessment.
* **Progress Tracking:** A visual progress bar and percentage indicator (e.g., "0% done", "Question 1 of 17") help users track their advancement through the current quiz.
* **Quiz History Sidebar:** A left-hand navigation panel that stores and organizes past quizzes (e.g., "OS 101 - SG9 - Security.pdf"). This allows users to easily switch between different topics and study sessions.
* **Import Material Access:** A persistent "Import" button in the sidebar provides quick access to add new documents without leaving the quiz environment.

## Figure 3: Quiz Mode (Open-ended & AI Grading)
An advanced testing feature for deeper learning evaluation.
* **Free-form Answer Text Area:** Supports open-ended questions (e.g., "Describe a program threat in your own words...") where users must articulate their understanding rather than just selecting an option.
* **Real-time AI Grading and Feedback:** The system evaluates the user's written response and provides immediate, targeted feedback. It displays a relevance score (e.g., "Score 0/100") and a brief explanation of what was expected versus what the student provided, helping to identify knowledge gaps.

## Figure 4: Import Materials Modal
The interface for bringing external knowledge into ANVIL.
* **Document Upload & Text Input:** Users can upload standard document formats (PDF/TXT) using the "Browse" button, or directly paste plain text into the provided text area.
* **Automatic Quiz Generation:** The "Import & Generate Quiz" button processes the provided content and automatically synthesizes a set of relevant questions for the user to study.

## Figure 5: Assistant Mode
The interactive chatbot interface for studying.
* **Interactive Chat Interface:** A conversational UI where users can type specific questions about their documents (e.g., "What are device drivers...").
* **Context-Aware Responses:** The AI assistant uses the imported materials as its knowledge base to provide accurate, context-specific answers, acting as a personalized tutor for those specific documents.
