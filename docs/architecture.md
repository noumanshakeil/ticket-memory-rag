# Architecture — Ticket Memory RAG

Tickets are the corpus. Similarity ranks subject+body+resolution+tags. `/assist` packs top neighbors into an LLM prompt for a draft reply.\n
