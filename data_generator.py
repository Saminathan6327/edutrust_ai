import json

academic_regulations = {
    "university_name": "EduTrust Global University",
    "academic_year": "2025-2026",
    "regulations": [
        {
            "category": "Grading System & GPA",
            "title": "Grading Scale and Cumulative GPA Calculation",
            "content": "EduTrust Global University uses a 4.0 grading scale: A+ (4.0, 90-100%), A (3.7, 85-89%), B+ (3.3, 80-84%), B (3.0, 75-79%), C+ (2.3, 70-74%), C (2.0, 65-69%), D (1.0, 50-64%), F (0.0, Below 50%). CGPA is calculated by dividing total quality points earned (Grade Points x Course Credits) by total credit hours attempted. Minimum CGPA required for graduation is 2.0 for Undergraduate and 3.0 for Postgraduate degrees."
        },
        {
            "category": "Attendance Policy",
            "title": "Mandatory Attendance and Condonation Rules",
            "content": "Students must maintain a minimum of 75% attendance in each course to be eligible to sit for final semester examinations. Attendance between 65% and 74% may be condoned on official medical grounds or approved university representation upon submitting documentation to the Academic Dean within 5 days of absence, along with a condonation fee of $50 per course. Attendance below 65% results in automatic debarment ('F-ATT' grade) and the student must repeat the course."
        },
        {
            "category": "Credit Requirements & Course Load",
            "title": "Degree Credit Limits and Overload Policy",
            "content": "Undergraduate degrees require completion of 120 credit hours (72 Core, 30 Major Electives, 18 General Education). Standard full-time credit load per semester is 15-18 credits. Maximum allowed load is 21 credits. Students with CGPA >= 3.5 may apply for a credit overload up to 24 credits upon approval from their Academic Advisor and Dean."
        },
        {
            "category": "Tuition Fees & Payments",
            "title": "Fee Structure, Deadlines, Penalties and Refund Policy",
            "content": "Tuition fees are $4,500 per semester for undergraduate students and $5,500 for postgraduate students. Payment deadline is 10 business days before the semester start. Late payments incur a fee of $50 per week. Failure to pay by Week 3 results in course registration cancellation. Refund schedule: 100% refund prior to Day 1, 80% during Week 1, 50% during Week 2, 0% after Week 2."
        },
        {
            "category": "Exams & Re-evaluation",
            "title": "Supplementary Exams, Re-checking and Grade Improvement",
            "content": "Students who fail a course with a 'D' or 'F' grade may apply for a Supplementary Exam held in July/January. Re-evaluation of answer scripts can be requested within 14 days of result declaration for a fee of $30 per paper (refundable if grade changes by at least one letter). Students may repeat up to 3 courses to improve CGPA; only the higher grade will be factored into final CGPA calculation."
        },
        {
            "category": "Academic Probation & Suspension",
            "title": "Probation Criteria and Dismissal Rules",
            "content": "A student whose CGPA falls below 2.0 at the end of any semester is placed on Academic Probation for the following semester. While on probation, maximum allowed credit load is restricted to 12 credits. If the CGPA remains below 2.0 for two consecutive semesters, the student is subject to Academic Suspension for one academic year or permanent dismissal."
        },
        {
            "category": "Internships & Practical Training",
            "title": "Mandatory Internship Policy for Seniors",
            "content": "All undergraduate students must complete an 8-week industry internship or research training project during the summer after their 3rd year. The internship carries 4 academic credits. Students must submit an internship logbook, company supervisor evaluation, and project report. Minimum passing grade is 'Pass' (C grade equivalent)."
        },
        {
            "category": "Course Add/Drop & Withdrawal",
            "title": "Add/Drop Window and Official Course Withdrawal",
            "content": "Students may Add or Drop courses without academic or financial penalty during the first 2 weeks of the semester via the Student Portal. Official course withdrawal is permitted from Week 3 through Week 8, resulting in a 'W' grade on the transcript (does not impact GPA). Withdrawals after Week 8 result in an automatic 'F' grade unless approved for extraordinary medical reasons."
        }
    ]
}

course_catalog = {
    "courses": [
        {
            "code": "CS101",
            "title": "Introduction to Computer Science & Python",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall & Spring",
            "prerequisites": "None",
            "instructor": "Dr. Aris Thorne",
            "syllabus": "Fundamental concepts of programming, algorithms, data structures, variables, loops, functions, object-oriented design, and problem solving in Python."
        },
        {
            "code": "CS201",
            "title": "Data Structures & Algorithms",
            "credits": 4,
            "department": "Computer Science",
            "semester": "Fall & Spring",
            "prerequisites": "CS101",
            "instructor": "Prof. Elena Rostova",
            "syllabus": "Arrays, linked lists, stacks, queues, trees, graphs, hashing, sorting algorithms, dynamic programming, and asymptotic complexity analysis (Big-O)."
        },
        {
            "code": "CS302",
            "title": "Database Management Systems",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall",
            "prerequisites": "CS201",
            "instructor": "Dr. Marcus Vance",
            "syllabus": "Relational database design, ER diagrams, SQL querying, normalization (1NF to BCNF), indexing, transaction processing, and introduction to NoSQL databases."
        },
        {
            "code": "DS202",
            "title": "Foundations of Data Science & Machine Learning",
            "credits": 4,
            "department": "Data Science",
            "semester": "Spring",
            "prerequisites": "CS101, MATH101",
            "instructor": "Dr. Maya Lin",
            "syllabus": "Exploratory data analysis, Pandas, NumPy, scikit-learn, regression models, classification, clustering, evaluation metrics, and ethical AI overview."
        },
        {
            "code": "MATH101",
            "title": "Calculus & Linear Algebra for Engineers",
            "credits": 4,
            "department": "Mathematics",
            "semester": "Fall & Spring",
            "prerequisites": "High School Mathematics",
            "instructor": "Prof. Alan Vance",
            "syllabus": "Limits, derivatives, integration, matrices, vector spaces, eigenvalues, eigenvectors, and application of linear algebra to data science."
        },
        {
            "code": "BUS210",
            "title": "Principles of Financial Management",
            "credits": 3,
            "department": "Business Administration",
            "semester": "Fall",
            "prerequisites": "None",
            "instructor": "Dr. Sarah Jenkins",
            "syllabus": "Time value of money, risk and return, financial statement analysis, capital budgeting, corporate finance, and valuation techniques."
        },
        {
            "code": "AI401",
            "title": "Artificial Intelligence & Conversational Agents",
            "credits": 4,
            "department": "Computer Science",
            "semester": "Spring",
            "prerequisites": "CS201, DS202",
            "instructor": "Dr. Sophia Patel",
            "syllabus": "Natural language processing, transformer architectures, LLMs, RAG systems, prompt engineering, agentic workflows, and ethical AI guardrails."
        }
    ]
}

faqs = """
Q: What are the library opening hours?
A: The EduTrust Central Library is open Monday through Friday from 8:00 AM to 10:00 PM, and Saturday-Sunday from 10:00 AM to 6:00 PM. During final exam weeks, the library operates 24/7.

Q: How do I apply for a Merit Scholarship?
A: Merit Scholarships cover up to 50% of semester tuition for students maintaining a CGPA of 3.8 or higher. Applications open every semester on the Student Portal. Deadline for Fall is October 15, and for Spring is March 15. Submit transcript and recommendation letter.

Q: What hostel accommodation options are available on campus?
A: EduTrust offers single, double, and triple-sharing hostel rooms. Single rooms cost $1,200/semester, double $900/semester, and triple $700/semester including Wi-Fi and laundry. Meal plans are mandatory for hostel residents ($800/semester).

Q: How does campus placement assistance work?
A: The Career Development Cell (CDC) conducts placement drives starting in the 7th semester. Over 150 top tech and business firms visit annually. Students must register with CDC, attend resume building workshops, and maintain zero active backlogs.

Q: How can I connect to the campus Wi-Fi network?
A: Select the 'EduTrust-Campus-WiFi' network. Login using your Student ID (e.g., STU2025001) and your University Portal password. For support, visit the IT Helpdesk in Hall B, Room 104.

Q: Where is the University Health Center located?
A: The Health Center is located next to Hostel Block 3. It provides free primary medical care, first aid, and mental health counseling. Operating hours are 24/7 with a resident doctor on call. Phone: +1-800-EDUTRUST-HEALTH.
"""

with open('/working_dir/c_608c0f17e2e78757/edutrust_ai/data/academic_regulations.json', 'w') as f:
    json.dump(academic_regulations, f, indent=2)

with open('/working_dir/c_608c0f17e2e78757/edutrust_ai/data/course_catalog.json', 'w') as f:
    json.dump(course_catalog, f, indent=2)

with open('/working_dir/c_608c0f17e2e78757/edutrust_ai/data/student_faqs.txt', 'w') as f:
    f.write(faqs)

print("Datasets successfully written!")
