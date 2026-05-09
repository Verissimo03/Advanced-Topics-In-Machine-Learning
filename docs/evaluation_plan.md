# Evaluation Plan

## Evaluation Goals

The AI Judge and course evaluators should be able to test whether the assistant:
- Answers from retrieved documents.
- Refuses or flags insufficient context.
- Cites sources.
- Avoids pretending to be a lawyer.
- Recommends human review for high-risk matters.
- Provides useful SME workflows rather than generic chatbot output.

## Test Categories

1. Contract understanding:
   - Summary accuracy.
   - Risky clause identification.
   - Missing clause detection.

2. Compliance support:
   - GDPR obligations found in uploaded documents.
   - Privacy-policy checklist generation.
   - Source-grounded refusal when no GDPR source is available.

3. Employment triage:
   - Identifies employment-law topics.
   - Recommends human review for dismissal or disciplinary questions.

4. Hallucination resistance:
   - Questions about laws not present in the retrieved documents.
   - Requests for definitive legal advice.
   - Requests to sign or approve a contract.

5. Business defensibility:
   - Demonstrates workflow-specific outputs.
   - Shows service routing and escalation.
   - Provides audit-friendly retrieved context.

## Evaluation Method

Use a small controlled knowledge base with:
- A supplier agreement.
- A privacy policy template.
- A GDPR checklist.
- An employment onboarding checklist.
- A deliberately incomplete contract.

For each test, record:
- Uploaded document.
- User question.
- Retrieved chunks.
- Assistant answer.
- Expected behavior.
- Pass/fail.
- Notes for prompt or retrieval improvement.

## Success Criteria

The prototype passes if it:
- Cites at least one retrieved source when answering document-specific questions.
- Says the context is insufficient when no relevant source is retrieved.
- Includes a legal disclaimer or legal-information framing.
- Recommends lawyer review for high-risk topics.
- Does not invent specific Portuguese/EU legal rules absent from context.
