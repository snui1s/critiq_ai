import easyocr

# gpu=False ถ้าเครื่องไม่มีการ์ดจอแยก แต่ถ้ามีใส่ True จะซิ่งมาก
reader = easyocr.Reader(['th', 'en'], gpu=False) 

# paragraph=True จะช่วยให้มันพยายามรวมบรรทัดที่อยู่ใกล้กัน ไม่ให้ข้อความกระจายเกินไป
result = reader.readtext('Screenshot 2023-05-13 214129.png', detail=0, paragraph=True)

full_prose = "\n".join(result)
print(full_prose)