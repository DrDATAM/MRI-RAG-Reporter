from pathlib import Path
import json
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


def load_case_summary(case_summary_path):
    """
    Load the structured case summary.

    This JSON file was created from the segmentation mask.
    It contains the numeric measurements that the report is allowed to use.
    """

    if not case_summary_path.exists():
        raise FileNotFoundError(
            f"Missing case summary file: {case_summary_path}\n"
            "Run this first:\n"
            "  python scripts/01_create_case_summary.py"
        )

    case_summary_text = case_summary_path.read_text(encoding="utf-8")
    case_summary = json.loads(case_summary_text)

    return case_summary


def load_retrieved_context(retrieved_context_path):
    """
    Load the retrieved knowledge-base context.

    This text file was created by the LangChain retrieval script.
    It contains knowledge-base chunks relevant to this case.
    """

    if not retrieved_context_path.exists():
        raise FileNotFoundError(
            f"Missing retrieved context file: {retrieved_context_path}\n"
            "Run this first:\n"
            "  python scripts/03_langchain_retrieval_demo.py"
        )

    retrieved_context = retrieved_context_path.read_text(encoding="utf-8")

    return retrieved_context


def format_case_summary_for_prompt(case_summary):
    """
    Convert case_summary.json into readable text for the LLM.

    We keep this explicit and simple so it is easy to inspect.
    """

    lines = []

    lines.append(f"Case ID: {case_summary['case_id']}")
    lines.append(f"Dataset: {case_summary['dataset']}")
    lines.append(f"Image shape: {case_summary['image_shape']}")
    lines.append(f"Voxel spacing mm: {case_summary['voxel_spacing_mm']}")
    lines.append(f"Voxel volume mm3: {case_summary['voxel_volume_mm3']}")
    lines.append(f"Unique segmentation labels: {case_summary['unique_labels']}")
    lines.append("")

    lines.append("Label map:")
    for label_value, label_name in case_summary["label_map"].items():
        lines.append(f"- {label_value}: {label_name}")
    lines.append("")

    lines.append("Label statistics:")
    for label_name, statistics in case_summary["label_statistics"].items():
        lines.append(f"- {label_name}")
        lines.append(f"  label value: {statistics['label_value']}")
        lines.append(f"  voxel count: {statistics['voxel_count']}")
        lines.append(f"  volume mm3: {statistics['volume_mm3']}")
        lines.append(f"  volume ml: {statistics['volume_ml']}")
    lines.append("")

    lines.append("Region groups:")
    for group_name, group_statistics in case_summary["region_groups"].items():
        lines.append(f"- {group_name}")
        lines.append(
            f"  included regions: {group_statistics['included_regions']}"
        )
        lines.append(f"  voxel count: {group_statistics['voxel_count']}")
        lines.append(f"  volume mm3: {group_statistics['volume_mm3']}")
        lines.append(f"  volume ml: {group_statistics['volume_ml']}")
    lines.append("")

    lines.append("Important note:")
    lines.append(case_summary["important_note"])

    formatted_case_summary = "\n".join(lines)

    return formatted_case_summary


def create_fixed_rag_prompt(case_summary_text, retrieved_context):
    """
    Create the exact prompt that will be sent to the LLM.

    This is called 'fixed RAG' because:
    - the retrieval step is already done
    - the case summary is already created
    - the prompt structure is fixed
    - the LLM only writes the final report
    """

    prompt = f"""
You are an educational medical imaging AI assistant.

Your task is to write a technical, educational report for a real segmented brain MRI case.

You must use only the information provided in:

1. CASE SUMMARY
2. RETRIEVED KNOWLEDGE CONTEXT

Do not invent clinical findings.
Do not give a diagnosis.
Do not give treatment advice.
Do not give prognosis or survival prediction.
Do not write as if this is a clinical radiology report.
Do not claim that the segmentation is clinically verified.
Do not use numeric values unless they are present in the CASE SUMMARY.

Write for a machine learning / medical imaging audience.

The report should include these sections:

# Segmented Brain Tumor MRI RAG Report

## 1. Case overview
Summarize the case identifier, dataset source, available segmentation labels, and the purpose of the report.

## 2. Available MRI sequences
Explain the MRI sequences used in this project:
T1, T1-Gd or contrast-enhanced T1, T2, and FLAIR.
Keep this explanation educational and concise.

## 3. Segmentation-derived measurements
Report the tumor-region volumes from the CASE SUMMARY.
Include:
- necrotic tumor core
- peritumoral edema
- enhancing tumor
- whole tumor
- tumor core

Use a simple Markdown table.

## 4. Meaning of the tumor regions
Explain what each segmentation label represents, using the retrieved context.
Make clear that these are segmentation-derived regions.

## 5. What the measurements can and cannot tell us
Explain that voxel counts and volumes are descriptive measurements derived from the segmentation mask.
Mention that the project does not train a segmentation model and does not validate clinical correctness.

## 6. Safety and limitations
State clearly that this is an educational RAG demonstration, not a diagnostic system.

## 7. Grounding statement
Briefly state that numeric values come from case_summary.json and explanatory context comes from the retrieved knowledge base.

CASE SUMMARY
================================================================================
{case_summary_text}

RETRIEVED KNOWLEDGE CONTEXT
================================================================================
{retrieved_context}
"""

    return prompt.strip()


def create_llm_from_env():
    """
    Create the LLM object using values from .env.

    Required:
    - OPENAI_API_KEY

    Optional:
    - OPENAI_MODEL
    - OPENAI_BASE_URL

    OPENAI_BASE_URL is useful when using an OpenAI-compatible institutional endpoint.
    """

    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")

    if openai_api_key is None:
        raise RuntimeError(
            "OPENAI_API_KEY was not found.\n"
            "Please check that your .env file exists and contains:\n"
            "OPENAI_API_KEY=your_key_here"
        )

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    base_url = os.getenv("OPENAI_BASE_URL")

    print("=" * 80)
    print("LLM configuration")
    print("=" * 80)
    print(f"Model name: {model_name}")

    if base_url is None:
        print("Base URL: default OpenAI endpoint")
        llm = ChatOpenAI(
            model=model_name,
            temperature=0,
        )
    else:
        print(f"Base URL: {base_url}")
        llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            base_url=base_url,
        )

    print("=" * 80)
    print()

    return llm


def save_text(output_path, text):
    """Save text to a file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def main():
    project_root = Path(__file__).resolve().parents[1]

    case_id = "case_001"

    case_summary_path = (
        project_root
        / "data"
        / "processed"
        / f"{case_id}_summary.json"
    )

    retrieved_context_path = (
        project_root
        / "outputs"
        / f"{case_id}_retrieved_context.txt"
    )

    prompt_output_path = (
        project_root
        / "outputs"
        / f"{case_id}_llm_prompt.txt"
    )

    report_output_path = (
        project_root
        / "outputs"
        / f"{case_id}_fixed_rag_report.md"
    )

    case_summary = load_case_summary(case_summary_path)

    retrieved_context = load_retrieved_context(retrieved_context_path)

    case_summary_text = format_case_summary_for_prompt(case_summary)

    prompt = create_fixed_rag_prompt(
        case_summary_text=case_summary_text,
        retrieved_context=retrieved_context,
    )

    save_text(
        output_path=prompt_output_path,
        text=prompt,
    )

    print("=" * 80)
    print("PROMPT SENT TO THE LLM")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    print(f"Saved prompt to: {prompt_output_path}")
    print("=" * 80)
    print()

    llm = create_llm_from_env()

    print("=" * 80)
    print("Calling LLM")
    print("=" * 80)

    response = llm.invoke(prompt)

    report_text = response.content

    save_text(
        output_path=report_output_path,
        text=report_text,
    )

    print("LLM report created.")
    print(f"Saved report to: {report_output_path}")
    print("=" * 80)
    print()

    print("=" * 80)
    print("REPORT PREVIEW")
    print("=" * 80)
    print(report_text[:2000])
    print("=" * 80)


if __name__ == "__main__":
    main()