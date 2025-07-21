from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_resume_and_job(resume, job_desc):
    prompt = f"""
You are an expert AI career advisor.

Analyze this resume and job description:

Resume:
{resume}

Job Description:
{job_desc}

Return:
1. A detailed comparison of matching and missing skills.
2. Suggestions for improvement.
3. An estimated **percentage match** (as a number only from 0 to 100) based on skills and qualifications.
Format your response like:

**Matching Skills:**
...

**Gaps or Missing Qualifications:**
...

**Suggestions for Improvement:**
...

**Match Percentage:** 85
"""

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content
