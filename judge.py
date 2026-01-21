import google.generativeai as genai
import dotenv
dotenv.load_dotenv()

# 1. Setup Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash') 

def judge_resume(extracted_text, job_description):
    prompt = f"""
    คุณคือผู้เชี่ยวชาญด้านการคัดเลือกคนเข้าทำงานที่เข้มงวดและมีนิสัยขวานผ่าซาก (Blunt & Cynical)
    หน้าที่ของคุณคือวิจารณ์ Resume ต่อไปนี้เทียบกับ Job Description (JD) ที่ให้มา
    
    กฎเหล็ก:
    1. ให้คะแนนความเหมาะสม 0-100 (ห้ามอวยเด็ดขาด)
    2. วิเคราะห์ทีละส่วน: ประสบการณ์, ทักษะ, และความน่าเชื่อถือ
    3. ถ้าเจอคำอวยเกินจริง หรือช่องว่างในประวัติ ให้จี้ถามแบบไม่เกรงใจ
    4. สรุปจุดบอดที่ร้ายแรงที่สุด 3 ข้อ
    
    [Job Description]:
    {job_description}
    
    [Resume Content]:
    {extracted_text}
    
    จงวิจารณ์ด้วยความสัตย์จริงและดุดัน:
    """
    
    response = model.generate_content(prompt)
    return response.text
