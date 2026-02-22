# Foundational System Appreciation (Beginner + Support + AI Context)

## 1) What this product is (kid-friendly)
Think of NewsNexus like a **smart newspaper helper**:
- It looks at many news websites.
- It picks important stories.
- It writes a short, simple summary.
- It keeps the original links so people can read the full article.

So instead of reading 100 long pages, you can quickly see what matters first.

## 2) Core building blocks
- **News Agent**: collects raw stories from RSS feeds.
- **AI Service**: summarizes text, tags category, and checks sentiment.
- **Review Agent**: reviews article quality and marks approval status.
- **Content Agent**: enhances articles and recommendations.
- **Orchestrator**: conductor that tells each agent when to run.
- **Database layer**: stores users, articles, reviews, and agent status.

## 3) What was fixed in this update and why it matters
1. **Database session bug fixed**
   - Before: `get_db_connection()` returned a closed DB session.
   - After: it returns a live session; caller closes it.
   - Impact: agents can now actually read/write data.

2. **Local-first database default**
   - Before: default required Postgres (`localhost/newsdb`) even for local testing.
   - After: default uses local SQLite (`newsnexus.db`) when `DATABASE_URL` is missing.
   - Impact: new developers can run core flow immediately.

3. **AI offline fallback mode**
   - Before: missing `OPENAI_API_KEY` crashed service initialization.
   - After: service runs in fallback mode with basic local summary/sentiment/category logic.
   - Impact: core agent is testable in non-production environments.

4. **Orchestrator test cycle support**
   - Added one-cycle execution method for health checks and automation.
   - Impact: SRE and QA can validate orchestration without long-running loops.

5. **Core runner added**
   - Added `agents/core_agent.py` for one-command execution (`python -m agents.core_agent`).
   - Impact: simple smoke test path for beginners and on-call engineers.

6. **Syntax errors fixed**
   - `components/news_card.py`: malformed f-string and safer URL injection handling.
   - `advertisement.py`: escaped braces in embedded JavaScript snippet.
   - Impact: project compiles and can be validated by tooling.

## 4) How to run the core agent quickly
1. (Optional) set environment variables:
   - `DATABASE_URL` (if you want Postgres)
   - `OPENAI_API_KEY` (for real AI responses)
2. Run:
   - `python -m agents.core_agent`
3. Expected:
   - Database initializes.
   - One orchestration cycle runs.
   - Logs show agent and workflow status.

## 5) Support and maintenance mental model
When something breaks, check in this order:
1. **Environment**: are keys/URLs set?
2. **Database**: can tables initialize/connect?
3. **Data ingestion**: are RSS feeds reachable?
4. **AI mode**: online API mode or offline fallback?
5. **Workflow execution**: does orchestrator run a single cycle?
6. **Persistence**: are new rows created for articles/reviews/agent status?

## 6) AI-agent context notes
- The codebase currently has both root-level and `services/` style modules; prefer `agents/ + services/ + database/` paths for future refactors.
- Avoid heavy work at import time; run side effects in explicit entrypoints.
- Keep runtime deterministic for tests by using one-cycle functions and fallback behavior.

## 7) Suggested next evolution milestones
- Add formal test suite (`pytest`) with mocks for external APIs.
- Close DB sessions consistently using context managers.
- Add retries/timeouts for feed and HTTP extraction.
- Replace placeholder logic in review/content workflows with bounded, observable jobs.
- Add structured logging + health endpoint for production observability.
