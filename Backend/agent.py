import os
import re
import json
import time
import base64
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

load_dotenv()

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

with open("profile.json") as f:
    PROFILE = json.load(f)

llm = ChatGroq(model="openai/gpt-oss-20b", api_key=GROQ_API_KEY)


def sanitize_latex(text: str) -> str:
    if not text:
        return ""
    return (text
        .replace("\u2013", "--")
        .replace("\u2014", "--")
        .replace("\xe2\x80\x93", "--")
        .replace("\xe2\x80\x94", "--")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", "``")
        .replace("\u201d", "''")
        .replace("\u2011", "-")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("$", "\\$")
        .replace("#", "\\#")
    )


def fetch_github_projects() -> list:
    repos_url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=20"
    repos = requests.get(repos_url, headers=HEADERS).json()

    skip_names = {"anaghakalyanaraman", "AASADS", "ASADS", "calculator", "Majorproject"}

    projects = []
    for repo in repos:
        if repo.get("fork"):
            continue
        if repo["name"] in skip_names:
            continue

        name = repo["name"]
        desc = repo.get("description")

        if not desc:
            readme_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{name}/readme"
            readme_resp = requests.get(readme_url, headers=HEADERS)
            if readme_resp.status_code == 200:
                readme_data = readme_resp.json()
                readme_text = base64.b64decode(readme_data["content"]).decode("utf-8", errors="ignore")[:500]
                for attempt in range(3):
                    try:
                        summary = llm.invoke([HumanMessage(content=f"Summarize this GitHub repo README in one sentence (max 15 words): {readme_text}")])
                        desc = summary.content.strip()
                        break
                    except Exception:
                        if attempt < 2:
                            time.sleep(5)
                time.sleep(1.5)

        if not desc:
            continue

        langs_resp = requests.get(repo["languages_url"], headers=HEADERS).json()
        languages = list(langs_resp.keys()) if isinstance(langs_resp, dict) else []

        projects.append({
            "name": name,
            "description": desc,
            "languages": languages
        })

    return projects


@tool
def generate_latex_resume(content: str) -> str:
    """
    Generate a LaTeX resume. Input must be a JSON string with keys:
    selected_projects (list), tailored_bullets (dict)
    """
    data = json.loads(content)
    selected_projects = data["selected_projects"]
    tailored_bullets = data["tailored_bullets"]

    profile = PROFILE

    exp_latex = ""
    for exp in profile["experience"]:
        bullets = "\n".join([f"    \\resumeItem{{{sanitize_latex(b)}}}" for b in exp["bullets"]])
        exp_latex += f"""
    \\resumeSubheading
      {{{sanitize_latex(exp['title'])}}}{{{sanitize_latex(exp['date'])}}}
      {{{sanitize_latex(exp['company'])}}}{{}}
    \\resumeItemListStart
{bullets}
    \\resumeItemListEnd"""

    proj_latex = ""
    for proj in selected_projects:
        proj_name = proj["name"]
        bullets = tailored_bullets.get(proj_name, [proj.get("description", "")])
        bullet_items = "\n".join([f"    \\resumeItem{{{sanitize_latex(b)}}}" for b in bullets])
        stack = ", ".join(proj.get("languages", proj.get("tech_stack", [])))
        proj_latex += f"""
    \\resumeProjectHeading
      {{\\textbf{{{sanitize_latex(proj_name)}}} $|$ \\emph{{{sanitize_latex(stack)}}}}}{{}}
    \\resumeItemListStart
{bullet_items}
    \\resumeItemListEnd"""

    skills = profile["skills"]
    edu0 = profile['education'][0]
    edu1 = profile['education'][1]

    latex = f"""\\documentclass[letterpaper,11pt]{{article}}
\\usepackage{{latexsym}}
\\usepackage[empty]{{fullpage}}
\\usepackage{{titlesec}}
\\usepackage{{enumitem}}
\\usepackage[hidelinks]{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage{{tabularx}}
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\addtolength{{\\oddsidemargin}}{{-0.5in}}
\\addtolength{{\\evensidemargin}}{{-0.5in}}
\\addtolength{{\\textwidth}}{{1in}}
\\addtolength{{\\topmargin}}{{-.5in}}
\\addtolength{{\\textheight}}{{1.0in}}
\\newcommand{{\\resumeItem}}[1]{{\\item\\small{{#1}}}}
\\newcommand{{\\resumeSubheading}}[4]{{
  \\item\\begin{{tabular*}}{{0.97\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
    \\textbf{{#1}} & #2 \\\\
    \\textit{{\\small#3}} & \\textit{{\\small #4}} \\\\
  \\end{{tabular*}}}}
\\newcommand{{\\resumeProjectHeading}}[2]{{
  \\item\\begin{{tabular*}}{{0.97\\textwidth}}{{l@{{\\extracolsep{{\\fill}}}}r}}
    \\small#1 & #2 \\\\
  \\end{{tabular*}}}}
\\newcommand{{\\resumeSubHeadingListStart}}{{\\begin{{itemize}}[leftmargin=0.15in, label={{}}]}}
\\newcommand{{\\resumeSubHeadingListEnd}}{{\\end{{itemize}}}}
\\newcommand{{\\resumeItemListStart}}{{\\begin{{itemize}}}}
\\newcommand{{\\resumeItemListEnd}}{{\\end{{itemize}}\\vspace{{-5pt}}}}

\\begin{{document}}

\\begin{{center}}
  \\textbf{{\\Huge {sanitize_latex(profile['name'])}}} \\\\
  \\small {sanitize_latex(profile['phone'])} $|$
  \\href{{mailto:{profile['email']}}}{{{profile['email']}}} $|$
  \\href{{https://{profile['linkedin']}}}{{{profile['linkedin']}}} $|$
  \\href{{https://{profile['github']}}}{{{profile['github']}}}
\\end{{center}}

\\section{{Education}}
\\resumeSubHeadingListStart
  \\resumeSubheading
    {{{sanitize_latex(edu0['degree'])}}}{{{sanitize_latex(edu0['date'])}}}
    {{{sanitize_latex(edu0['school'])}}}{{{sanitize_latex(edu0['gpa'])}}}
  \\resumeSubheading
    {{{sanitize_latex(edu1['degree'])}}}{{{sanitize_latex(edu1['date'])}}}
    {{{sanitize_latex(edu1['school'])}}}{{{sanitize_latex(edu1['gpa'])}}}
\\resumeSubHeadingListEnd

\\section{{Experience}}
\\resumeSubHeadingListStart
{exp_latex}
\\resumeSubHeadingListEnd

\\section{{Projects}}
\\resumeSubHeadingListStart
{proj_latex}
\\resumeSubHeadingListEnd

\\section{{Technical Skills}}
\\begin{{itemize}}[leftmargin=0.15in, label={{}}]
  \\small{{\\item{{
    \\textbf{{Languages}}{{: {', '.join(skills['languages'])}}} \\\\
    \\textbf{{Frameworks}}{{: {', '.join(skills['frameworks'])}}} \\\\
    \\textbf{{Cloud/DevOps}}{{: {', '.join(skills['cloud_devops'])}}} \\\\
    \\textbf{{Databases}}{{: {', '.join(skills['databases'])}}} \\\\
    \\textbf{{AI/ML}}{{: {', '.join(skills['ai_ml'])}}}
  }}}}
\\end{{itemize}}

\\end{{document}}"""

    output_path = "output_resume.tex"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)

    return json.dumps({"status": "success", "latex_file": output_path})


def run_tailor(jd: str) -> dict:
    projects = fetch_github_projects()

    prompt = f"""Given this job description:
{jd}

Here are the candidate's GitHub projects:
{json.dumps(projects, indent=2)}

1. Pick the 3 most relevant projects for this JD
2. Write 2-3 bullet points per project using keywords from the JD
3. IMPORTANT: Do NOT use %, &, $, #, or any special characters. Write "40 percent" instead of "40%".
4. Return ONLY valid JSON, no extra text:
{{
  "selected_projects": [
    {{"name": "...", "description": "...", "languages": [...]}}
  ],
  "tailored_bullets": {{
    "project_name": ["bullet 1", "bullet 2", "bullet 3"]
  }}
}}"""

    for attempt in range(3):
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            break
        except Exception as e:
            if attempt < 2:
                time.sleep(5)
            else:
                return {"latex": "", "agent_response": f"Groq error: {str(e)}"}

    json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
    if not json_match:
        return {"latex": "", "agent_response": "Failed to parse LLM response"}

    data = json.loads(json_match.group())
    generate_latex_resume.invoke(json.dumps(data))

    latex_content = ""
    if os.path.exists("output_resume.tex"):
        with open("output_resume.tex", encoding="utf-8") as f:
            latex_content = f.read()

    return {"latex": latex_content, "agent_response": "Resume generated successfully"}


if __name__ == "__main__":
    projects = fetch_github_projects()
    print(json.dumps(projects, indent=2))