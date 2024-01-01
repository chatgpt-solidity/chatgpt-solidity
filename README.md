

# The code and results for ISSTA 2024 Artifact Evaluation

Paper: AuditGPT: Auditing Smart Contracts with ChatGPT

This document is to help users reproduce the results we reported in our submission. It contains the following descriptions:

- [The code and results for ISSTA 2024 Artifact Evaluation](#the-code-and-results-for-issta-2024-artifact-evaluation)
  - [(Section 1) Figure 1: ERC20 Smart contract that has high severity violation found on large dataset](#section-1-figure-1-erc20-smart-contract-that-has-high-severity-violation-found-on-large-dataset)
  - [(Section 3.2) Table 1: ERC rules’ content and security impacts](#section-32-table-1-erc-rules-content-and-security-impacts)
  - [(Section 3.3) Table 2: Linguistic patterns](#section-33-table-2-linguistic-patterns)
  - [(Section 5.1) Table 3: Evaluation results on the large dataset](#section-51-table-3-evaluation-results-on-the-large-dataset)
  - [(Section 5.1) Figure 2: ERC1155 Smart contract that has high severity violation found on large dataset](#section-51-figure-2-erc1155-smart-contract-that-has-high-severity-violation-found-on-large-dataset)
  - [(Section 5.2) Table 4: Evaluation results on the ground-true dataset](#section-52-table-4-evaluation-results-on-the-ground-true-dataset)
  - [(Section 5.3) Figure 3: Evaluation results on the ground-truth dataset with each design point deactivated](#section-53-figure-3-evaluation-results-on-the-ground-truth-dataset-with-each-design-point-deactivated)
  - [Environment Setup](#environment-setup)
  - [AuditGPT Usage](#auditgpt-usage)

AuditGPT: Using LLM to validate whether a smart contract follows the standard, source code is in `python`. Below is the explanation for its children file/folders:

- `main.py`: CLI entrypoint
- `auditor`: All python code for the auditor
  - `commands/gen.py`: Command 'gen', generating LLM prompts for a smart contract
  - `commands/run.py`: Command 'run', feeding the generated LLM prompts to LLM and collecting the results
  - `llm`: Code related to LLM executing
  - `prompt`: Code related to generate prompts for a smart contract
- `rules`: Manually fixed ERC rules after LLM extraction
- `flows`: Prompt templates

`auditor` is an easy-to-use executable entrypoint for `python/main.py`

All the smart contract source code used in evaluation is in `dataset`:
- `dataset/audited`: ground true dataset
- `dataset/etherscan100`: Part of large dataset, 100 ERC20 smart contracts from etherscan
- `dataset/polyscan50-721`: Part of large dataset, 50 ERC721 smart contracts from polyscan
- `dataset/polyscan50-1155`: Part of large dataset, 50 ERC1155 smart contracts from polyscan

ERC rule extraction results (Section 4.2) are in `evaluation/rule-extraction`.


## (Section 1) Figure 1: ERC20 Smart contract that has high severity violation found on large dataset

Original source code: `dataset/etherscan100/ArnoldSailormoonegger-0x294d7be2.sol`

## (Section 3.2) Table 1: ERC rules’ content and security impacts
Google Sheet: [Table 1](https://docs.google.com/spreadsheets/d/1bVAQkwNiRcLtXXVbB7VWZkL-uwrVC4Y3UHorP_pKRCQ/edit#gid=0)

## (Section 3.3) Table 2: Linguistic patterns
Google Sheet: [Table 2](https://docs.google.com/spreadsheets/d/1bVAQkwNiRcLtXXVbB7VWZkL-uwrVC4Y3UHorP_pKRCQ/edit#gid=626278090)

## (Section 5.1) Table 3: Evaluation results on the large dataset

./evaluation/large:   Folder contains the large dataset results

Below is the explanation for its children folders:

Note: \<name\> is the solidity file name in the `dataset`.

- `etherscan100/<name>/llm`: Results for 100 ERC20 smart contracts from etherscan
- `polyscan50-721/<name>/llm`: Results for 50 ERC721 smart contracts from polyscan
- `polyscan50-1155/<name>/llm`: Results for 50 ERC1155 smart contracts from polyscan

## (Section 5.1) Figure 2: ERC1155 Smart contract that has high severity violation found on large dataset

Original source code: `dataset/polyscan50-1155/MyERC1155Token-0x6482e7f6.sol`

## (Section 5.2) Table 4: Evaluation results on the ground-true dataset

The results are in `./evaluation/necessity/all`


## (Section 5.3) Figure 3: Evaluation results on the ground-truth dataset with each design point deactivated

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