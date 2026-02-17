import fitz
import os

SAMPLE_DIR = "sample_cvs"

CV_PROFILES = [
    {
        "filename": "john_doe_senior_java.pdf",
        "content": """
John Doe
Senior Java Backend Developer
Location: New York, USA
Email: john.doe@example.com

Summary:
Experienced Backend Developer with 8 years of experience building scalable microservices using Java and Spring Boot. Skilled in cloud architecture (AWS), database optimization (PostgreSQL, MongoDB), and CI/CD pipelines.

Skills:
- Languages: Java 17+, Kotlin, SQL
- Frameworks: Spring Boot, Spring Cloud, Hibernate
- Tools: Docker, Kubernetes, Jenkins, Git
- Cloud: AWS (EC2, S3, RDS, Lambda)
- Databases: PostgreSQL, MongoDB, Redis

Experience:
Senior Software Engineer | TechSolutions Inc. (2020 - Present)
- Led the migration of a monolithic application to a microservices architecture, improving scalability by 40%.
- Designed and implemented RESTful APIs for high-volume transactions.
- Mentored junior developers and conducted code reviews.

Software Engineer | FinTech Corp. (2016 - 2020)
- Developed secure payment processing modules using Spring Security.
- Optimized database queries, reducing API latency by 30%.
- Integrated third-party APIs for financial data aggregation.

Education:
B.S. in Computer Science | University of Technology (2016)
"""
    },
    {
        "filename": "jane_smith_junior_python.pdf",
        "content": """
Jane Smith
Junior Python Developer
Location: London, UK
Email: jane.smith@example.com

Summary:
Passionate Junior Python Developer with a strong foundation in web development using Django and Flask. Eager to learn and contribute to innovative projects. Familiar with data analysis libraries like Pandas and NumPy.

Skills:
- Languages: Python, JavaScript, HTML/CSS
- Frameworks: Django, Flask, FastAPI
- Databases: SQLite, MySQL
- Tools: Git, VS Code, Postman
- Other: Agile/Scrum, Unit Testing

Experience:
Junior Python Developer | StartUp Hub (2023 - Present)
- Developed and maintained backend services for a content management system using Django.
- Collaborated with frontend developers to integrate APIs.
- Wrote unit tests using PyTest to ensure code quality.

Intern | CodeCamp (Summer 2022)
- Built a web scraper to collect real estate data using BeautifulSoup.
- Assists in debugging and fixing minor software defects.

Education:
B.S. in Software Engineering | City University (2023)
"""
    },
    {
        "filename": "michael_brown_fullstack_js.pdf",
        "content": """
Michael Brown
Full Stack Developer (MERN Stack)
Location: San Francisco, USA
Email: michael.brown@example.com

Summary:
Full Stack Developer with 5 years of experience in building modern web applications. Proficient in the MERN stack (MongoDB, Express, React, Node.js). Strong understanding of UI/UX principles and responsive design.

Skills:
- Frontend: React.js, Redux, Tailwind CSS, TypeScript
- Backend: Node.js, Express.js, GraphQL
- Databases: MongoDB, Firebase
- DevOps: AWS, Netlify, Vercel

Experience:
Full Stack Developer | Creative Agency (2019 - Present)
- Delivered over 20 web applications for clients across various industries.
- Implemented real-time features using Socket.io for a chat application.
- Optimized frontend performance, achieving Lighthouse scores of 90+.

Frontend Developer | E-commerce Solutions (2017 - 2019)
- Built interactive user interfaces for an online marketplace using React.
- Integrated payment gateways (Stripe, PayPal).
- Collaborated with designers to ensure pixel-perfect implementation.

Education:
B.A. in Computer Information Systems | State University (2017)
"""
    },
    {
        "filename": "sarah_connor_devops.pdf",
        "content": """
Sarah Connor
DevOps Engineer
Location: Berlin, Germany
Email: sarah.connor@example.com

Summary:
Detail-oriented DevOps Engineer specializing in automation, infrastructure as code, and cloud reliability. Expert in Kubernetes orchestration and CI/CD pipeline optimization. Committed to ensuring 99.99% uptime.

Skills:
- Cloud: Azure, AWS, Google Cloud Platform
- Containerization: Docker, Kubernetes (AKS, EKS)
- IaC: Terraform, Ansible, CloudFormation
- CI/CD: Jenkins, GitLab CI, GitHub Actions
- Monitoring: Prometheus, Grafana, ELK Stack

Experience:
DevOps Engineer | CloudNative Systems (2021 - Present)
- Automating infrastructure provisioning using Terraform across multi-cloud environments.
- Managing Kubernetes clusters for microservices deployment.
- Reduced deployment time by 60% through optimized CI/CD pipelines.

System Administrator | IT Services Ltd. (2018 - 2021)
- Managed Linux servers and network security policies.
- Implemented automated backup solutions.
- Monitored system health and resolved critical incidents.

Education:
M.S. in Network Engineering | Technical University (2018)
"""
    },
    {
        "filename": "david_lee_tech_lead.pdf",
        "content": """
David Lee
Technical Lead / Software Architect
Location: Toronto, Canada
Email: david.lee@example.com

Summary:
Visionary Technical Lead with over 12 years of experience in software architecture and team leadership. Proven track record of delivering enterprise-grade solutions. Expert in distributed systems, cloud-native design, and technical strategy.

Skills:
- Architecture: Microservices, Event-Driven Architecture, Domain-Driven Design
- Languages: Go, Java, Python, C#
- Cloud: AWS Certified Solutions Architect, Azure
- Leadership: Team Mentorship, Agile Coaching, Technical hiring
- Databases: Cassandra, DynamoDB, PostgreSQL

Experience:
Technical Lead | Enterprise Solutions (2018 - Present)
- Leading a team of 10+ engineers in developing a high-scale logistics platform.
- Defining technical roadmap and architecture standards.
- Successfully migrated legacy systems to a cloud-native serverless architecture.

Senior Software Engineer | Global Tech (2014 - 2018)
- Designed core backend services processing millions of requests daily.
- Evaluated and introduced new technologies to improve developer productivity.
- Conducted technical interviews and onboarding for new hires.

Education:
M.S. in Computer Science | University of Toronto (2012)
"""
    }
]

def create_pdf(filename, content):
    doc = fitz.open()
    page = doc.new_page()
    
    # Insert text with basic formatting
    text_rect = fitz.Rect(50, 50, 550, 800)
    
    # We use a simple text insertion. For more complex layouts we'd want reportlab,
    # but fitz is great for simple text dumps which is perfect for parsing testing.
    page.insert_textbox(
        text_rect, 
        content, 
        fontsize=11, 
        fontname="helv", 
        align=0  # Left align
    )
    
    filepath = os.path.join(SAMPLE_DIR, filename)
    doc.save(filepath)
    print(f"Generated: {filepath}")

def main():
    if not os.path.exists(SAMPLE_DIR):
        os.makedirs(SAMPLE_DIR)
        
    for profile in CV_PROFILES:
        create_pdf(profile["filename"], profile["content"])

if __name__ == "__main__":
    main()
