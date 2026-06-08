[![Python](https://shields.io/badge/python-3.10+-informational)](https://docs.python.org/3.10/)

# Copilot Agents

Custom agents for GitHub Copilot in VS Code built on top of default system
prompts. Tested only with DeepSeek API, but should work with any
OpenAI-compatible API.

## Agents

### Explainer

Extended version of **Ask** agent with a tendency to show KaTeX math and Mermaid
diagrams when explaining technical concepts.

| Example prompt | Before | After |
| --- | --- | --- |
| Explain binary search complexity. | Binary search halves the search space each step, so its time complexity is O(log n). For 1 million elements you need about 20 comparisons. | Binary search halves the search space at each step, yielding $O(\log n)$ time. For $n = 10^6$ elements, the worst-case comparisons are $\lceil \log_2 n \rceil = 20$. The recurrence relation $$T(n) = T\!\left(\frac{n}{2}\right) + O(1)$$ solves to $T(n) = O(\log n)$ by the Master Theorem. |
| Describe the lifecycle of a TCP connection. | TCP starts with a three-way handshake: SYN, SYN-ACK, ACK. Then data transfers. Finally it closes with a four-way handshake: FIN, ACK, FIN, ACK. | TCP connections follow a well-defined state machine: ![Example](https://github.com/hanggrian/copilot-agents/raw/assets/example.svg) |

## Usage

Create a new custom agent with `Chat: Configure Custom Agent...` command and
select one of the provided templates.
