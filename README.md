🤖 Autonomous Code Writer & Debug Agent

An AI-powered autonomous software engineering agent that transforms natural-language requirements into working, tested, debugged, and reviewed code.

Built using LangGraph, LangChain, Gemini, Groq, and FastAPI, this project demonstrates how LLMs can be orchestrated into a multi-step autonomous development workflow.

🔄 Workflow

Requirement → Planning → Code Generation → Test Generation → Execution → Testing → Debugging → Code Review → Final Report

✨ Key Features
🧠 AI Task Planner — breaks complex requirements into actionable steps
💻 AI Code Generator — generates implementation based on the plan
🧪 Test Generator — automatically creates unit tests and edge cases
⚙️ Code Executor — runs the generated implementation and tests
🔍 Test Analyzer — evaluates execution results
🐛 AI Debugger — analyzes failures and automatically retries
🔄 Self-correcting workflow using LangGraph conditional routing
👨‍💻 AI Code Reviewer — evaluates correctness, quality, and coverage
📊 Final Engineering Report — summarizes the complete development process
📡 Real-time streaming — displays agent progress node-by-node
🌐 Full-stack architecture with separate frontend and backend
🏗️ Architecture
User Task
   ↓
Planner
   ↓
Coder
   ↓
Test Generator
   ↓
Executor
   ↓
Tester
   ↓
 ┌───────────────┐
 │               │
PASS           FAILURE
 │               │
 ↓               ↓
Reviewer      Debugger
 │               │
 ↓               └──→ Coder
Final Report
🛠️ Tech Stack

AI: LangGraph LangChain Gemini Groq
Backend: Python FastAPI Pydantic
Frontend: React Next.js
Deployment: Render Vercel

🎯 Project Highlights

This project focuses on Agentic AI and AI Engineering, demonstrating:

Stateful LLM workflows
Agent orchestration
Conditional routing
Automated software testing
AI-assisted debugging
LLM-based code review
Error handling and retry mechanisms
Streaming AI responses
Production-style API integration
Cloud deployment


🚀 Future Improvements
Secure code-execution sandbox
Docker-based isolation
GitHub integration
Automatic pull requests
Multi-language code generation
Advanced LLM evaluation
LangSmith observability
Multi-file project generation

Built to explore how AI can move from simply generating code to actually participating in the software development lifecycle.
