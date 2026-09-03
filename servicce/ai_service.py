from groq import AsyncGroq
from config import GROQ_API_KEY
from .analytics_service import get_student_statistics, get_group_statistics, get_weekly_group_report, get_monthly_report, get_students_at_risk

client=AsyncGroq(api_key=GROQ_API_KEY)


async def analyze_student_attendance(student_id):
    statistics=await get_student_statistics(student_id)

    prompt=f"""
    Analyz
    e this student's attendance statistics.

    Statistics:
    {statistics}

    Give a short and clear analysis.

    Mention:
    - attendance performance
    - lateness
    - absences
    - early leaving
    - time in class
    - one or two recommendations

    Do not invent any information that is not in the statistics.
    """

    response=await client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role":"system",
                "content":"You are an attendance analysis assistant."
            },
            {
                "role":"user",
                "content":prompt
            }
        ],
        temperature=0.7,
        max_completion_tokens=800,
        reasoning_effort="low",
        include_reasoning=False
    )

    return response.choices[0].message.content.strip()


async def analyze_group_attendance(group_id):
    statistics=await get_group_statistics(group_id)

    prompt=f"""
    Analyze this group's attendance statistics.

    Statistics:
    {statistics}

    Give a short group attendance analysis.

    Mention:
    - overall attendance
    - present students
    - late students
    - absent students
    - students who leave early
    - recommendations for improving attendance

    Do not invent any information that is not in the statistics.
    """

    response=await client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role":"system",
                "content":"You are an attendance analysis assistant."
            },
            {
                "role":"user",
                "content":prompt
            }
        ],
        temperature=0.7,
        max_completion_tokens=800,
        reasoning_effort="low",
        include_reasoning=False
    )

    return response.choices[0].message.content.strip()


async def generate_weekly_recommendation(group_id):
    report=await get_weekly_group_report(group_id)

    prompt=f"""
    Create recommendations based on this group's weekly attendance report.

    Weekly report:
    {report}

    Give practical recommendations for the teacher.

    Focus on:
    - frequent absences
    - lateness
    - attendance improvement
    - possible actions for the next week

    Do not invent attendance data.
    """

    response=await client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role":"system",
                "content":"You are an attendance recommendation assistant."
            },
            {
                "role":"user",
                "content":prompt
            }
        ],
        temperature=0.7,
        max_completion_tokens=800,
        reasoning_effort="low",
        include_reasoning=False
    )

    return response.choices[0].message.content.strip()


async def generate_monthly_summary():
    report=await get_monthly_report()

    prompt=f"""
    Create a monthly attendance summary from this report.

    Monthly report:
    {report}

    Summarize:
    - attendance situation
    - absences
    - lateness
    - early leaving
    - general trends
    - recommendations

    Do not invent any information that is not present in the report.
    """

    response=await client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role":"system",
                "content":"You are an attendance reporting assistant."
            },
            {
                "role":"user",
                "content":prompt
            }
        ],
        temperature=0.7,
        max_completion_tokens=800,
        reasoning_effort="low",
        include_reasoning=False
    )

    return response.choices[0].message.content.strip()


async def analyze_attendance_risk():
    students=await get_students_at_risk()

    prompt=f"""
    Analyze the attendance risk list.

    Students at risk:
    {students}

    Explain:
    - how serious the attendance risk is
    - what teachers or admins should do
    - how to help students improve attendance

    Only use the information provided.
    Do not invent attendance statistics.
    """

    response=await client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role":"system",
                "content":"You are an attendance risk analysis assistant."
            },
            {
                "role":"user",
                "content":prompt
            }
        ],
        temperature=0.7,
        max_completion_tokens=800,
        reasoning_effort="low",
        include_reasoning=False
    )

    return response.choices[0].message.content.strip()