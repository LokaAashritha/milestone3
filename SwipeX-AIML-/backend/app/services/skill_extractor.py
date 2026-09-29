import re

SKILL_TAXONOMY: dict[str, list[str]] = {
    "Python": [r"\bpython\b", r"\bpython3\b", r"\bpy\b"],
    "FastAPI": [r"\bfastapi\b", r"\bfast-api\b"],
    "Django": [r"\bdjango\b", r"\bdjango rest framework\b", r"\bdrf\b"],
    "Flask": [r"\bflask\b"],
    "Java": [r"\bjava\b(?!\s*script)"],
    "Spring Boot": [r"\bspring boot\b", r"\bspringboot\b", r"\bspring framework\b"],
    "Go": [r"\bgolang\b", r"\bgo\s+language\b", r"\bGo\b"],
    "Rust": [r"\brust\b", r"\brustlang\b"],
    "C++": [r"\bc\+\+\b", r"\bcpp\b"],
    "C#": [r"\bc#\b", r"\bcsharp\b", r"\b\.net\b", r"\bdotnet\b"],
    "Node.js": [r"\bnode\.?js\b", r"\bnodejs\b", r"\bnode\b"],
    "Express": [r"\bexpress\.?js\b", r"\bexpress\b"],
    "Ruby": [r"\bruby\b(?!\s*on\s*rails)", r"\bruby on rails\b", r"\brails\b"],
    "PHP": [r"\bphp\b", r"\blaravel\b", r"\bsymfony\b"],
    "Scala": [r"\bscala\b"],
    "Kotlin": [r"\bkotlin\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b", r"\bes6\b"],
    "TypeScript": [r"\btypescript\b", r"\bts\b"],
    "React": [r"\breact\.?js\b", r"\breact\b(?!\s*native)"],
    "React Native": [r"\breact native\b"],
    "Next.js": [r"\bnext\.?js\b", r"\bnextjs\b"],
    "Vue.js": [r"\bvue\.?js\b", r"\bvue\b", r"\bvuejs\b"],
    "Angular": [r"\bangular\b", r"\bangularjs\b"],
    "HTML5": [r"\bhtml5\b", r"\bhtml\b"],
    "CSS3": [r"\bcss3\b", r"\bcss\b"],
    "Tailwind CSS": [r"\btailwind\s*css\b", r"\btailwind\b"],
    "Bootstrap": [r"\bbootstrap\b"],
    "Redux": [r"\bredux\b", r"\bredux-toolkit\b"],
    "Zustand": [r"\bzustand\b"],
    "Webpack": [r"\bwebpack\b"],
    "Vite": [r"\bvite\b"],
    "PostgreSQL": [r"\bpostgresql\b", r"\bpostgres\b", r"\bpsql\b"],
    "MySQL": [r"\bmysql\b"],
    "MongoDB": [r"\bmongodb\b", r"\bmongo\b"],
    "Redis": [r"\bredis\b"],
    "SQLite": [r"\bsqlite\b", r"\bsqlite3\b"],
    "SQL": [r"\bsql\b"],
    "NoSQL": [r"\bnosql\b"],
    "Elasticsearch": [r"\belasticsearch\b", r"\belastic search\b"],
    "Cassandra": [r"\bcassandra\b"],
    "DynamoDB": [r"\bdynamodb\b"],
    "Snowflake": [r"\bsnowflake\b"],
    "BigQuery": [r"\bbigquery\b"],
    "Docker": [r"\bdocker\b", r"\bcontainerization\b", r"\bcontainers\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "AWS": [r"\baws\b", r"\bamazon web services\b", r"\bec2\b", r"\bs3\b", r"\blambda\b"],
    "Azure": [r"\bazure\b", r"\bmicrosoft azure\b"],
    "GCP": [r"\bgcp\b", r"\bgoogle cloud\b", r"\bgoogle cloud platform\b"],
    "Terraform": [r"\bterraform\b"],
    "CI/CD": [
        r"\bci/cd\b",
        r"\bci-cd\b",
        r"\bcontinuous integration\b",
        r"\bcontinuous deployment\b",
    ],
    "GitHub Actions": [r"\bgithub actions\b"],
    "GitLab CI": [r"\bgitlab ci\b", r"\bgitlab-ci\b"],
    "Jenkins": [r"\bjenkins\b"],
    "Linux": [r"\blinux\b", r"\bubuntu\b", r"\bdebian\b", r"\brhel\b"],
    "Bash": [r"\bbash\b", r"\bshell scripting\b", r"\bsh\b"],
    "Git": [r"\bgit\b", r"\bgithub\b", r"\bgitlab\b"],
    "Prometheus": [r"\bprometheus\b"],
    "Grafana": [r"\bgrafana\b"],
    "REST API": [r"\brest\s*api\b", r"\brestful\b", r"\brest\s*apis\b", r"\brest\b"],
    "GraphQL": [r"\bgraphql\b"],
    "Microservices": [r"\bmicroservices\b", r"\bmicroservice\b"],
    "gRPC": [r"\bgrpc\b"],
    "Kafka": [r"\bapache kafka\b", r"\bkafka\b"],
    "RabbitMQ": [r"\brabbitmq\b"],
    "Celery": [r"\bcelery\b"],
    "SQLAlchemy": [r"\bsqlalchemy\b"],
    "Pydantic": [r"\bpydantic\b"],
    "Prisma": [r"\bprisma\b"],
    "Machine Learning": [r"\bmachine learning\b", r"\bml\b"],
    "Deep Learning": [r"\bdeep learning\b", r"\bdl\b"],
    "NLP": [r"\bnlp\b", r"\bnatural language processing\b"],
    "PyTorch": [r"\bpytorch\b"],
    "TensorFlow": [r"\btensorflow\b", r"\btf\b"],
    "scikit-learn": [r"\bscikit-learn\b", r"\bsklearn\b"],
    "spaCy": [r"\bspacy\b"],
    "pandas": [r"\bpandas\b"],
    "NumPy": [r"\bnumpy\b"],
    "SciPy": [r"\bscipy\b"],
    "Transformers": [r"\btransformers\b", r"\bhuggingface\b", r"\bhugging face\b"],
    "LLM": [r"\bllm\b", r"\bllms\b", r"\blarge language models\b"],
    "Computer Vision": [r"\bcomputer vision\b", r"\bcv\b", r"\bopencv\b"],
    "Data Analysis": [r"\bdata analysis\b", r"\bdata analytics\b"],
    "Tableau": [r"\btableau\b"],
    "PowerBI": [r"\bpowerbi\b", r"\bpower bi\b"],
    "Statistics": [r"\bstatistics\b", r"\bstatistical\b"],
    "MLflow": [r"\bmlflow\b"],
    "Spark": [r"\bapache spark\b", r"\bspark\b", r"\bpyspark\b"],
    "pytest": [r"\bpytest\b"],
    "Jest": [r"\bjest\b"],
    "React Testing Library": [r"\breact testing library\b", r"\brtl\b"],
    "Selenium": [r"\bselenium\b"],
    "Playwright": [r"\bplaywright\b"],
    "Cypress": [r"\bcypress\b"],
    "Postman": [r"\bpostman\b"],
    "API Testing": [r"\bapi testing\b"],
    "Unit Testing": [r"\bunit testing\b", r"\bunit test\b", r"\bunit tests\b"],
    "Jira": [r"\bjira\b"],
    "Agile": [r"\bagile\b", r"\bscrum\b", r"\bkanban\b"],
    "System Design": [r"\bsystem design\b", r"\barchitecture\b"],
    "Code Review": [r"\bcode review\b", r"\bcode reviews\b"],
    "Mentoring": [r"\bmentoring\b", r"\bleadership\b"],
    "Problem Solving": [r"\bproblem solving\b", r"\banalytical thinking\b"],
}


class SkillExtractor:
    def __init__(self, taxonomy: dict[str, list[str]] = SKILL_TAXONOMY):
        self.taxonomy = taxonomy
        self._compiled_patterns: dict[str, list[re.Pattern]] = {}
        for canonical_name, patterns in self.taxonomy.items():
            compiled_list = []
            for pattern in patterns:
                flags = re.IGNORECASE
                compiled_list.append(re.compile(pattern, flags))
            self._compiled_patterns[canonical_name] = compiled_list

        self._nlp = None
        try:
            import spacy
            self._nlp = spacy.load("en_core_web_sm")
        except Exception:
            self._nlp = None

    def extract_skills_spacy_ner(self, text: str) -> set[str]:
        if not self._nlp or not text:
            return set()
        found: set[str] = set()
        try:
            doc = self._nlp(text[:5000])  # limit length for fast performance
            for ent in doc.ents:
                if ent.label_ in ("ORG", "PRODUCT", "LANGUAGE", "NORP"):
                    matched = self.extract_skills(ent.text)
                    if matched:
                        found.update(matched)
        except Exception:
            pass
        return found

    def extract_skills(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        found_skills: set[str] = set()
        cleaned_text = text.replace("/", " / ").replace("-", " - ")

        for canonical_name, regex_list in self._compiled_patterns.items():
            for regex in regex_list:
                if regex.search(text) or regex.search(cleaned_text):
                    found_skills.add(canonical_name)
                    break

        if self._nlp:
            spacy_skills = self.extract_skills_spacy_ner(text)
            found_skills.update(spacy_skills)

        return sorted(found_skills, key=lambda s: s.lower())

    def normalize_skills(self, skills: list[str]) -> list[str]:
        if not skills:
            return []

        normalized: set[str] = set()
        for raw_skill in skills:
            extracted = self.extract_skills(raw_skill)
            if extracted:
                normalized.update(extracted)
            else:
                cleaned = raw_skill.strip()
                if cleaned:
                    normalized.add(cleaned)

        return sorted(normalized, key=lambda s: s.lower())


skill_extractor = SkillExtractor()
