

# The code and results for ISSTA 2024 Artifact Evaluation

Paper: AuditGPT: Auditing Smart Contracts with ChatGPT

This document is to help users reproduce the results we reported in our submission. It contains the following descriptions:

- [The code and results for ISSTA 2024 Artifact Evaluation](#the-code-and-results-for-issta-2024-artifact-evaluation)
  - [Figure 1 (Section 1): ERC20 Smart contract that has high severity violation found on large dataset](#figure-1-section-1-erc20-smart-contract-that-has-high-severity-violation-found-on-large-dataset)
  - [Table 1 (Section 3.2): ERC rules’ content and security impacts](#table-1-section-32-erc-rules-content-and-security-impacts)
  - [Table 2 (Section 3.3): Linguistic patterns](#table-2-section-33-linguistic-patterns)
  - [Table 3 (Section 5.1): Evaluation results on the large dataset](#table-3-section-51-evaluation-results-on-the-large-dataset)
  - [Figure 2 (Section 5.1): ERC1155 Smart contract that has high severity violation found on large dataset](#figure-2-section-51-erc1155-smart-contract-that-has-high-severity-violation-found-on-large-dataset)
  - [Table 4 (Section 5.2): Evaluation results on the ground-true dataset](#table-4-section-52-evaluation-results-on-the-ground-true-dataset)
  - [Figure 3 (Section 5.3): Evaluation results on the ground-truth dataset with each design point deactivated](#figure-3-section-53-evaluation-results-on-the-ground-truth-dataset-with-each-design-point-deactivated)
  - [Environment Setup](#environment-setup)
  - [AuditGPT Usage](#auditgpt-usage)

AuditGPT: Using LLM to validate whether a smart contract follows the standard, source code is in `python`. Below is the explanation for its children file/folders:

- `main.py`: CLI entrypoint
- `auditor`: All python code for the auditor
  - `commands/gen.py`: Command 'gen', generating LLM prompts for a smart contract
  - `commands/run.py`: Command 'run', feeding the generated LLM prompts to LLM and collecting the results
  - `llm`: Code related to LLM executing
  - `prompt`: Code related to generate prompts for a smart contract
- `rules`: Formatted ERC rules
- `flows`: Prompt templates

`auditor` is an easy-to-use executable entrypoint for `python/main.py`

All the smart contract source code used in evaluation is in `dataset`:
- `dataset/audited`: ground true dataset
- `dataset/etherscan100`: Part of large dataset, 100 ERC20 smart contracts from etherscan
- `dataset/polyscan50-721`: Part of large dataset, 50 ERC721 smart contracts from polyscan
- `dataset/polyscan50-1155`: Part of large dataset, 50 ERC1155 smart contracts from polyscan

## Figure 1 (Section 1): ERC20 Smart contract that has high severity violation found on large dataset

Original source code: `dataset/etherscan100/ArnoldSailormoonegger-0x294d7be2.sol`

## Table 1 (Section 3.2): ERC rules’ content and security impacts
Google Sheet: [Table 1](https://docs.google.com/spreadsheets/d/1bVAQkwNiRcLtXXVbB7VWZkL-uwrVC4Y3UHorP_pKRCQ/edit#gid=0)

## Table 2 (Section 3.3): Linguistic patterns
Google Sheet: [Table 2](https://docs.google.com/spreadsheets/d/1bVAQkwNiRcLtXXVbB7VWZkL-uwrVC4Y3UHorP_pKRCQ/edit#gid=626278090)

## Table 3 (Section 5.1): Evaluation results on the large dataset

./evaluation/large:   Folder contains the large dataset results

Below is the explanation for its children folders:

Note: \<name\> is the solidity file name in the `dataset`.

- `etherscan100/<name>/llm`: Results for 100 ERC20 smart contracts from etherscan
- `polyscan50-721/<name>/llm`: Results for 50 ERC721 smart contracts from polyscan
- `polyscan50-1155/<name>/llm`: Results for 50 ERC1155 smart contracts from polyscan

## Figure 2 (Section 5.1): ERC1155 Smart contract that has high severity violation found on large dataset

Original source code: `dataset/polyscan50-1155/MyERC1155Token-0x6482e7f6.sol`

## Table 4 (Section 5.2): Evaluation results on the ground-true dataset

The results are in `./evaluation/necessity/all`





## Figure 3 (Section 5.3): Evaluation results on the ground-truth dataset with each design point deactivated

`./evaluation/necessity`:   Folder contains the ground-truth dataset results

Below is the explanation for its children file/folders:

Note: \<name\> is the solidity file name in the `dataset`. 

- `all/<name>/llm`: Results from all design points activated
- `fullcode/<name>/llm`: Results from deactivating design point "Code Slicing"
- `fullerc/<name>/llm`: Results from deactivating design point "ERC Rule Extraction"
- `nocm/<name>/llm`: Results from deactivating design point "Breaking Down Compound Rules"
- `noos/<name>/llm`: Results from deactivating design point "One Shot"
- `universal/<name>/llm`: Results from deactivating design point "Prompt Specialization" 
- `graph.ipynb`: Python script to generate the bar graph

## Environment Setup
```bash
# Create Python virtual environment
$ python3 -m venv .venv

# Activate the virtual environment in the terminal
$ source .venv/bin/activate

# Install the dependencies
$ pip install -r requirements.txt
```

## AuditGPT Usage

```bash
# Generate the LLM prompts for a smart contract
$ ./auditor gen <output> --file <path to solidity file>
# Example: ./auditor gen output --file dataset/etherscan100/ArnoldSailormoonegger-0x294d7be2.sol

# Audit this smart contract
$ ./auditor run output/ArnoldSailormoonegger-0x294d7be2 --set
```