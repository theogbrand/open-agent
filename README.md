# Primitives for users to create their own pseudo-deterministic workflows
* Workflow: User can chat with Mia to create a "Skill" (Inspired by [Voyager](https://github.com/MineDojo/Voyager) then save it to be used later)
* Mia should prompt user to test workflow on some mock data to verify workflow is working as planned before trying on real data (Gmail/Gcal)

# Tools
* Structured Outputs, tool calling, information extraction
* ideas in [SWARM](https://github.com/openai/swarm)

* Gmail, Gcal, Slack use cases

Demo
1. Agent fans out for information via Slack/Gmail, summarises it back to user
2. Monitor daily some status from Jira/Notion
3. Schedule a meeting with person X to follow up on some item

Memory
1. when user gives feedback to Mia on Search Queries should contain current company and alma mater, Mia should remember to search this the next time same workflow is fired

Proposed Flow:
1. Query
2. Plan?
3. Main Agent transfers to Gmail/Calendar SubAgent?
4. SubAgent composes CRUD functions it has access to to answer query
5. passes control back to Main Agent to reply

# Usage:
1. install requirements, copied over so might need some manual installations
2. download credentials.json file to run google-auth.py so token.json is returned to access your own GSuite data
3. run main.py 