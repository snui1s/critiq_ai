import easyocr
import fitz
import os
import csv


def init_csv(csv_path):
    if not os.path.exists(csv_path):
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "resumename", "ocr_result"])
        return 1
    else:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)
            if len(data) <= 1:
                return 1
            return int(data[-1][0]) + 1


def process_all_resumes(resume_dir, csv_path):
    next_id = init_csv(csv_path)

    files = [f for f in os.listdir(resume_dir) if f.endswith(".pdf")]
    if not files:
        print("No PDF files found.")
        return

    print("Initializing EasyOCR...")
    reader = easyocr.Reader(["th", "en"])

    with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for filename in files:
            pdf_path = os.path.join(resume_dir, filename)
            print(f"Processing ID {next_id}: {filename}")

            try:
                doc = fitz.open(pdf_path)
                full_text = ""

                if len(doc) > 0:
                    # Method 1: Try Direct Text Extraction
                    for page in doc:
                        full_text += page.get_text() + "\n"

                    # Method 2: Fallback to OCR if text is too short (likely scanned)
                    if len(full_text.strip()) < 50:
                        print(
                            f"  > Text too short/empty. Falling back to OCR for {filename}..."
                        )
                        full_text = ""  # Reset
                        for page in doc:
                            # Zoom = 2 (2x resolution = 144 dpi) for better OCR
                            mat = fitz.Matrix(2, 2)
                            pix = page.get_pixmap(matrix=mat)
                            temp_img = f"temp_ocr_{next_id}.png"
                            pix.save(temp_img)

                            result = reader.readtext(temp_img, detail=0)
                            full_text += " ".join(result) + "\n"

                            if os.path.exists(temp_img):
                                os.remove(temp_img)

                # Clean up text slightly
                full_text = full_text.strip()

                writer.writerow([next_id, filename, full_text])
                f.flush()
                print(f"Done.")

                next_id += 1
                doc.close()
            except Exception as e:
                print(f"Error processing {filename}: {e}")


if __name__ == "__main__":
    RESUME_DIR = "resumes"
    CSV_DB = "ocr_results.csv"

    if os.path.exists(RESUME_DIR):
        process_all_resumes(RESUME_DIR, CSV_DB)
        print(f"\nOCR completed. Data saved to {CSV_DB}")
    else:
        print(f"Directory '{RESUME_DIR}' not found.")
