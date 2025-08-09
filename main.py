import os
import sys
from google import genai
from fpdf import FPDF
from google.genai import types
import json
import re
def write_content(pdf, content, level=0):
    if isinstance(content, dict):
        for key, value in content.items():
            pdf.set_font("Times", size=12 + max(0, 2 - level), style='B')
            pdf.cell(0, 10, txt=("  " * level) + key, ln=True)
            write_content(pdf, value, level + 1)
    else:
        pdf.set_font("Times", size=12)
        pdf.multi_cell(0, 10, txt=str(content))
        pdf.ln(2)

client = genai.Client(api_key="YOUR_API_KEY")
print("Welcome to Topic Content Generator!")
topic= input("Enter a topic to generate content for: ")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Give 5 sub-topics of {topic}. Only subtopics seperated by commas, nothing else.", # The content to generate
)
subtopics = response.text.split(',')
subtopics.insert(0, "Introduction to " + topic)
# print(response.text)
print("The subtopics are:")
for i in range(len(subtopics)):
    print(f"{i+1}. {subtopics[i].strip()}")

nums = input("Enter the subtopic numbers separated by commas to generate content for:")

valid_subtopics = []
for num in nums.split(','):
    if num.strip().isdigit() and 1 <= int(num.strip()) <= len(subtopics):
        valid_subtopics.append(subtopics[int(num.strip()) - 1].strip())
    else:
        print(f"Invalid subtopic number: {num.strip()}. It will be skipped.")
print("Do you want to add some more subtopics? (yes=1/no=0)")
print("Note: Only first 5 subtopics will be considered for content generation.")
add_more = input().strip()
if add_more == '1':
    while True:
        new_subtopic = input("Enter a new subtopic (or 'done' to finish): ")
        if new_subtopic.strip().lower() == 'done':
            break
        valid_subtopics.append(new_subtopic.strip())
print("Generating content for the selected subtopics...")
valid_subtopics = valid_subtopics[:5]
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Generate content for the following subtopics that come under the Topic: {topic}: {', '.join(valid_subtopics)} In json format with keys as subtopic names and values as the content. Provide explanation for each subtopic in less than 50 words. Return only valid JSON. Do not wrap in backticks, code fences, or extra text.",
    config={
        # "max_output_tokens": 1000,  # Adjust the maximum output tokens as needed
    }
)
print("Generated content:")
json_content = response.text
print(json_content)
# cleaned = re.sub(r"^```(?:json)?\n|\n```$", "", json_content.strip())
data = json.loads(json_content)

# Save the generated content to a pdf
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Times", size=12)
pdf.cell(200, 10, txt=f"Topic: {topic}", ln=True, align='C')
pdf.ln(10)  # Add a line break
for subtopic, content in data.items():
    pdf.set_font("Times", size=14, style='B')
    pdf.cell(0, 10, txt=subtopic, ln=True)
    write_content(pdf, content)


pdf_file_name = f"{topic.replace(' ', '_')}_content.pdf"
pdf.output(pdf_file_name)
print(f"Content saved to {pdf_file_name}")
print("Thank you for using Topic Content Generator!")
