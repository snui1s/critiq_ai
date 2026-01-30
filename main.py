import os
from OCR import process_all_resumes
from judge import main_evaluation_loop


def main():
    RESUME_DIR = "resumes"
    OCR_CSV = "ocr_results.csv"

    print("=== STEP 1: RUNNING OCR PROCESS ===")
    if not os.path.exists(RESUME_DIR):
        print(f"Directory '{RESUME_DIR}' not found. Creating it...")
        os.makedirs(RESUME_DIR)

    files = [f for f in os.listdir(RESUME_DIR) if f.endswith(".pdf")]

    if not files:
        print(f"No PDF files found in '{RESUME_DIR}'.")
        if os.path.exists(OCR_CSV):
            print(f"But found existing '{OCR_CSV}'. Proceeding to evaluation...")
        else:
            print("No resumes to process and no existing results found. Stopping.")
            return
    else:
        process_all_resumes(RESUME_DIR, OCR_CSV)
        print("\nOCR Step Completed.\n")

    print("=== STEP 2: RUNNING AI EVALUATION (JUDGE) ===")
    main_evaluation_loop()
    print("\nAI Evaluation Step Completed.")
    print("You can check the final results in 'judge_results.csv'")


if __name__ == "__main__":
    main()
