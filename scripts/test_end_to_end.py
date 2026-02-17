"""
End-to-End Test Script for Agentic Talent Matcher.
Simulates the entire workflow:
1. Indexing CVs
2. Running Agent Queries (Generic, Specific, Self-Promotion)
3. Evaluating Responses using LLM-as-a-Judge
4. Generating a Report
"""

import asyncio
import os
import glob

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.vector_store import VectorStoreService
from services.pdf_service import PDFService
from services.agent import run_talent_agent
from services.evaluation import evaluate_agent_response
from config import get_settings


async def main():
    print("🚀 Starting End-to-End Test...\n")
    
    # 1. Initialize Services
    settings = get_settings()
    print(f"🔧 Configuration: LLM={settings.llm_model_name}, EvalLLM={settings.evaluation_llm_model_name or 'Same'}")
    
    vector_store = VectorStoreService()
    pdf_service = PDFService()
    
    # 2. Index Sample CVs
    print("\n📂 Indexing CVs from sample_cvs/...")
    sample_files = glob.glob("sample_cvs/*.pdf")
    if not sample_files:
        print("❌ No PDF files found in sample_cvs/. Run generate_samples.py first.")
        return

    for file_path in sample_files:
        filename = os.path.basename(file_path)
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            chunks = pdf_service.extract_and_chunk(content)
            ids = vector_store.upsert_chunks(chunks, filename)
            print(f"   - Indexed {filename}: {len(ids)} chunks")
        except Exception as e:
            print(f"   ❌ Failed to index {filename}: {e}")

    # 3. Define Test Cases
    test_cases = [
        {
            "name": "Generic Search (Java)",
            "query": "Find a Senior Java Developer and matching jobs for him."
        },
        {
            "name": "Source Specific (Ciklum Python)",
            "query": "Find Ciklum job offers for a Junior Python Developer. Do not check LinkedIn."
        },
        {
            "name": "Self-Promotion (LinkedIn Post)",
            "query": "Write a LinkedIn post about yourself."
        }
    ]

    results = []

    # 4. Run Tests & Evaluations
    print("\n🤖 Running Agent Queries & Evaluations...")
    
    for case in test_cases:
        print(f"\n🔹 Test Case: {case['name']}")
        print(f"   Query: {case['query']}")
        
        # Run Agent
        try:
            response = await run_talent_agent(case['query'])
            print(f"   ✅ Agent Response Received ({len(response)} chars)")
        except Exception as e:
            print(f"   ❌ Agent Failed: {e}")
            response = "Error"

        # Evaluate (Skip eval for pure content generation like LinkedIn post if desired, but let's see)
        eval_result = None
        if response != "Error":
            try:
                # We interpret "context" for evaluation. 
                # For search queries, we want the evaluator to fetch context from Vector DB.
                # For self-promotion, context is irrelevant/empty.
                
                # Context fetching is automatic inside evaluate_agent_response if vector_store_service passed
                eval_result = await evaluate_agent_response(
                    query=case['query'],
                    response=response,
                    context="", # Auto-fetch
                    vector_store_service=vector_store
                )
                print(f"   📊 Evaluation: {eval_result.overall}/5.0")
            except Exception as e:
                print(f"   ❌ Evaluation Failed: {e}")

        results.append({
            "case": case['name'],
            "query": case['query'],
            "response": response,
            "evaluation": eval_result
        })

    # 5. Generate Report
    print("\n📝 Generating Report...")
    generate_report(results)
    print("\n✅ Test Complete.")


def generate_report(results):
    report_lines = ["# Agentic Talent Matcher - Test Report", ""]
    
    # Summary Table
    headers = "Test Case | Overall Score | Relevance | Clarity | Accuracy\n--- | --- | --- | --- | ---"
    report_lines.append(headers)
    
    for r in results:
        eval_res = r.get("evaluation")
        if eval_res:
            row = f"{r['case']} | {eval_res.overall} | {eval_res.relevance.score} | {eval_res.clarity.score} | {eval_res.accuracy.score}"
        else:
            row = f"{r['case']} | N/A | - | - | -"
        report_lines.append(row)
    
    report_lines.append("\n---\n")
    
    # Detailed Results
    for r in results:
        report_lines.append(f"## Test Case: {r['case']}")
        report_lines.append(f"**Query:** {r['query']}\n")
        report_lines.append(f"**Agent Response:**\n\n{r['response']}\n")
        
        eval_res = r.get("evaluation")
        if eval_res:
            report_lines.append("### Evaluation Details")
            report_lines.append(f"- **Relevance ({eval_res.relevance.score}/5)**: {eval_res.relevance.reasoning}")
            report_lines.append(f"- **Clarity ({eval_res.clarity.score}/5)**: {eval_res.clarity.reasoning}")
            report_lines.append(f"- **Accuracy ({eval_res.accuracy.score}/5)**: {eval_res.accuracy.reasoning}")
        
        report_lines.append("\n---\n")
        
    with open("test_report.md", "w") as f:
        f.write("\n".join(report_lines))
    
    print("📄 Report saved to test_report.md")


if __name__ == "__main__":
    asyncio.run(main())
