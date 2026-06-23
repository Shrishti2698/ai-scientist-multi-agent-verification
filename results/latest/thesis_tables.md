# Thesis Result Tables

## Overall Comparison

| System | Accuracy | Avg Confidence | Avg Evidence | Contradiction Recall |
|---|---:|---:|---:|---:|
| single_agent | 0.583 | 0.604 | 0.0 | 0.0 |
| rag | 0.667 | 0.531 | 0.0 | 0.0 |
| multi_agent_no_critic_loop | 0.833 | 0.577 | 1.0 | 0.5 |
| multi_agent | 0.917 | 0.609 | 1.083 | 0.75 |

## Category Accuracy

| System | critic | extraction | generalization | multi_agent | retrieval | verification |
|---|---:|---:|---:|---:|---:|---:|
| single_agent | 0.5 | 1.0 | 0.5 | 1.0 | 0.333 | 0.5 |
| rag | 0.5 | 1.0 | 1.0 | 1.0 | 0.333 | 0.5 |
| multi_agent_no_critic_loop | 0.5 | 1.0 | 1.0 | 1.0 | 0.667 | 1.0 |
| multi_agent | 1.0 | 1.0 | 1.0 | 1.0 | 0.667 | 1.0 |
