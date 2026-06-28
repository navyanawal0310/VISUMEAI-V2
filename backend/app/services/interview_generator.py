from __future__ import annotations

import hashlib
import logging
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ..models.schemas import JobDescription, ResumeAnalysisResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Output schema
# ---------------------------------------------------------------------------

@dataclass
class InterviewQuestion:
    id: str                 # e.g. "q1"
    type: str               # "technical" | "behavioral" | "gap"
    difficulty: str         # "easy" | "medium" | "hard"
    skill: str              # canonical skill name or topic area
    question: str           # the full question text

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "type":       self.type,
            "difficulty": self.difficulty,
            "skill":      self.skill,
            "question":   self.question,
        }


# ---------------------------------------------------------------------------
# Question bank
# Each entry: (skill_canonical, type, easy, medium, hard)
# ---------------------------------------------------------------------------
# fmt: off
_TECHNICAL_BANK: List[Tuple[str, str, str, str]] = [
    # (skill, easy_q, medium_q, hard_q)
    (
        "python",
        "What is the difference between a list and a tuple in Python?",
        "Explain Python's GIL and how it impacts multi-threaded programs.",
        "Design a memory-efficient pipeline in Python for processing 10 GB of CSV data without loading it all into RAM.",
    ),
    (
        "python",
        "What are Python decorators and can you give a simple example?",
        "How does Python's garbage collector work, and what are reference cycles?",
        "Compare asyncio, threading, and multiprocessing in Python — when would you choose each for a CPU-bound vs I/O-bound task?",
    ),
    (
        "java",
        "What is the difference between an abstract class and an interface in Java?",
        "Explain how Java's garbage collector works and the difference between Young and Old generations.",
        "Design a thread-safe singleton in Java without using the `synchronized` keyword on the entire method.",
    ),
    (
        "javascript",
        "What is the difference between `==` and `===` in JavaScript?",
        "Explain the JavaScript event loop and how the call stack, task queue, and microtask queue interact.",
        "How would you implement a custom Promise from scratch in JavaScript?",
    ),
    (
        "typescript",
        "What is the difference between `interface` and `type` in TypeScript?",
        "Explain TypeScript's structural typing system and how it differs from nominal typing.",
        "How would you design a type-safe event emitter in TypeScript using generics and mapped types?",
    ),
    (
        "react",
        "What is the difference between props and state in React?",
        "Explain the React reconciliation algorithm and when you would use `React.memo` or `useMemo`.",
        "How would you architect a large React application to avoid prop drilling without a global state library?",
    ),
    (
        "react",
        "What are React hooks and why were they introduced?",
        "Explain the rules of hooks and what happens if you call a hook conditionally.",
        "Design a custom hook that debounces an API call and handles race conditions when the user types rapidly.",
    ),
    (
        "node.js",
        "What is the event-driven architecture of Node.js and what makes it non-blocking?",
        "How does Node.js handle file I/O differently from a traditional multi-threaded server?",
        "Design a rate-limiter middleware for an Express API that works across multiple Node.js instances.",
    ),
    (
        "django",
        "What is Django's ORM and how does it differ from writing raw SQL?",
        "Explain Django's middleware pipeline and give an example of where you would use custom middleware.",
        "How would you scale a Django application to handle 10,000 concurrent users — what bottlenecks would you address first?",
    ),
    (
        "flask",
        "What is the application context in Flask and how does it differ from the request context?",
        "How do you handle authentication and session management in a Flask REST API?",
        "Design a blueprint-based Flask application that supports multi-tenancy with per-tenant database isolation.",
    ),
    (
        "fastapi",
        "What makes FastAPI faster than Flask for async operations?",
        "Explain how FastAPI's dependency injection system works and give a use case for nested dependencies.",
        "How would you implement background task processing, rate limiting, and API versioning together in FastAPI?",
    ),
    (
        "sql",
        "What is the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN?",
        "Explain database indexing — how does a B-tree index work and what are its trade-offs?",
        "You have a slow query on a 50-million-row table. Walk me through your full optimization process.",
    ),
    (
        "sql",
        "What is the difference between WHERE and HAVING clauses?",
        "Explain ACID properties and how they are implemented in a relational database.",
        "Design a schema for a social network with millions of users that supports efficient follower/following lookups and feed generation.",
    ),
    (
        "postgresql",
        "How does PostgreSQL differ from MySQL in terms of features?",
        "Explain PostgreSQL's MVCC (Multi-Version Concurrency Control) and how it prevents dirty reads.",
        "How would you design a partitioned table in PostgreSQL for time-series data and ensure partition pruning works efficiently?",
    ),
    (
        "mongodb",
        "What is the difference between embedding and referencing documents in MongoDB?",
        "Explain MongoDB's aggregation pipeline and how it differs from SQL GROUP BY.",
        "Design a MongoDB schema for an e-commerce platform with millions of products and user-specific pricing — justify your indexing strategy.",
    ),
    (
        "aws",
        "What is the difference between EC2, ECS, and Lambda in AWS?",
        "Explain how S3 event notifications can trigger serverless workflows and what their limitations are.",
        "Design a fault-tolerant, auto-scaling microservices architecture on AWS with a budget constraint of under $500/month.",
    ),
    (
        "docker",
        "What is the difference between a Docker image and a Docker container?",
        "Explain Docker's layer caching mechanism and how you would write a Dockerfile to optimize build times.",
        "How would you implement a zero-downtime deployment strategy using Docker and a reverse proxy like Nginx?",
    ),
    (
        "kubernetes",
        "What is the difference between a Kubernetes Pod, Deployment, and Service?",
        "Explain how Kubernetes handles rolling updates and how you would configure readiness and liveness probes.",
        "Design a Kubernetes setup for a stateful application (e.g., a database cluster) with persistent storage, auto-scaling, and self-healing.",
    ),
    (
        "machine learning",
        "What is the difference between supervised and unsupervised learning?",
        "Explain the bias-variance trade-off and how you would diagnose overfitting in a model.",
        "Design an end-to-end ML pipeline for a real-time recommendation system that handles concept drift and retrains automatically.",
    ),
    (
        "machine learning",
        "What is cross-validation and why is it important?",
        "Explain how gradient boosting works and compare XGBoost to a random forest.",
        "You have a severely imbalanced dataset (1:99 ratio). Walk me through your complete strategy — from data handling to metric selection to deployment.",
    ),
    (
        "deep learning",
        "What is backpropagation and how does it compute gradients?",
        "Explain vanishing gradients — why they occur in deep networks and how techniques like batch normalization and residual connections address them.",
        "Design a distributed training setup for a 7-billion-parameter model across 64 GPUs — what parallelism strategies would you use?",
    ),
    (
        "nlp",
        "What is tokenization and why does it matter in NLP?",
        "Explain the transformer architecture — specifically how self-attention works and why positional encoding is needed.",
        "You need to fine-tune a large language model for a domain-specific task with only 500 labelled examples. What approach would you take and why?",
    ),
    (
        "git",
        "What is the difference between `git merge` and `git rebase`?",
        "Explain how `git cherry-pick` works and describe a scenario where you would use it over a merge.",
        "Your team's main branch has diverged significantly from a long-running feature branch. Walk me through your strategy to integrate it cleanly.",
    ),
    (
        "docker",
        "What is a multi-stage Docker build and when would you use one?",
        "How do Docker volumes differ from bind mounts, and which would you choose for a production database?",
        "Describe how you would harden a Docker container for a production security audit.",
    ),
    (
        "ci/cd",
        "What is the difference between continuous integration and continuous delivery?",
        "How would you design a CI/CD pipeline that runs tests in parallel and fails fast?",
        "Design a GitOps-based deployment pipeline that supports canary releases, automatic rollback on error rate spikes, and audit trails.",
    ),
    (
        "microservices",
        "What is the main advantage of microservices over a monolithic architecture?",
        "Explain the saga pattern and how it handles distributed transactions across microservices.",
        "Your microservices architecture is experiencing cascading failures. Walk me through how you would implement circuit breakers, bulkheads, and observability to prevent this.",
    ),
    (
        "rest api",
        "What are the main principles of REST and what makes an API RESTful?",
        "Explain idempotency in REST APIs — which HTTP methods are idempotent and why does it matter?",
        "Design a versioned, rate-limited REST API for a multi-tenant SaaS product — document your decisions on authentication, pagination, and error handling.",
    ),
    (
        "redis",
        "What is Redis and what are its primary use cases?",
        "Explain Redis eviction policies — when would you use LRU vs LFU vs noeviction?",
        "Design a distributed lock mechanism using Redis that is safe under network partitions (Redlock algorithm).",
    ),
    (
        "agile",
        "What is the difference between a sprint and a release in Scrum?",
        "How do you handle scope creep mid-sprint and what Scrum ceremonies help prevent it?",
        "Your team consistently fails to finish sprint commitments. How would you use velocity data, retrospectives, and capacity planning to fix this?",
    ),
    (
        "devops",
        "What is the difference between DevOps and traditional IT operations?",
        "Explain infrastructure as code — what problem does Terraform solve that shell scripts don't?",
        "Design a full observability stack (metrics, logs, traces) for a distributed system running 50 microservices.",
    ),
    (
        "tensorflow",
        "What is the difference between eager execution and graph execution in TensorFlow?",
        "Explain how TensorFlow's `tf.data` pipeline optimises data loading during training.",
        "How would you export a TensorFlow model for low-latency inference on edge devices with limited memory?",
    ),
    (
        "pytorch",
        "What is the difference between `torch.Tensor` and `torch.nn.Parameter`?",
        "Explain how PyTorch's autograd engine builds and traverses the computational graph.",
        "Design a custom training loop in PyTorch with mixed-precision training, gradient accumulation, and checkpoint resumption.",
    ),
    (
        "data science",
        "What is the difference between correlation and causation?",
        "Explain how you would handle missing data — when would you impute vs drop?",
        "You are asked to build a churn prediction model for a subscription business. Walk me through your full approach from EDA to production deployment.",
    ),
    (
        "linux",
        "What is the difference between a process and a thread in Linux?",
        "Explain how the Linux kernel handles memory mapping and what the OOM killer does.",
        "A Linux server is unresponsive. Walk me through your full diagnostic process using only command-line tools.",
    ),
    (
        "graphql",
        "What is the difference between a REST API and a GraphQL API?",
        "Explain the N+1 query problem in GraphQL and how DataLoader solves it.",
        "Design a federated GraphQL schema for a platform with 10 independent microservices, including authorization at the field level.",
    ),
    (
        "elasticsearch",
        "What is an inverted index and how does Elasticsearch use it?",
        "Explain the difference between a query context and a filter context in Elasticsearch.",
        "Your Elasticsearch cluster is experiencing high JVM heap pressure. Walk me through your tuning process.",
    ),
    (
        "spark",
        "What is the difference between a transformation and an action in Apache Spark?",
        "Explain how Spark handles data shuffling and why it is a performance bottleneck.",
        "Design a Spark streaming pipeline that ingests from Kafka, deduplicates events within a 5-minute window, and writes to Delta Lake.",
    ),
    (
        "angular",
        "What is the difference between one-way and two-way data binding in Angular?",
        "Explain Angular's change detection strategy and when you would use `OnPush`.",
        "Design a large Angular application with lazy-loaded modules, a shared state service, and role-based route guards.",
    ),
    (
        "vue",
        "What is the difference between computed properties and watchers in Vue?",
        "Explain Vue's reactivity system and how it tracks dependencies.",
        "Design a performant Vue 3 application using Composition API and Pinia for a dashboard that polls live data every 10 seconds.",
    ),
    (
        "spring",
        "What is dependency injection and how does Spring implement it?",
        "Explain Spring Boot's auto-configuration mechanism and how you would override a default bean.",
        "Design a Spring microservice with circuit breakers (Resilience4j), distributed tracing (Zipkin), and an async messaging layer (Kafka).",
    ),
    (
        "go",
        "What is a goroutine and how does it differ from an OS thread?",
        "Explain Go's `select` statement and how it avoids goroutine leaks.",
        "Design a high-throughput HTTP server in Go that handles 100,000 concurrent connections with backpressure and graceful shutdown.",
    ),
]

# Behavioral questions indexed by experience tier
_BEHAVIORAL_BANK: Dict[str, List[Tuple[str, str]]] = {
    "junior": [
        # (skill_context, question)
        ("teamwork",       "Tell me about a time you had to ask for help on a technical task. How did you approach it and what did you learn?"),
        ("problem-solving","Describe a bug you spent a long time debugging. What was your process and what did you find?"),
        ("learning",       "How do you stay up to date with new technologies? Give a recent example of something you taught yourself."),
        ("collaboration",  "Describe a time you worked on a group project. What was your contribution and how did you handle disagreements?"),
        ("initiative",     "Tell me about a time you took ownership of a task that was outside your responsibilities."),
        ("feedback",       "Describe a time you received critical feedback on your code or work. How did you respond?"),
        ("deadline",       "Tell me about a time you had to complete a task under a tight deadline. How did you prioritise?"),
    ],
    "mid": [
        ("leadership",     "Tell me about a time you informally led a technical decision. How did you gain buy-in from teammates?"),
        ("conflict",       "Describe a technical disagreement you had with a colleague. How did you resolve it?"),
        ("delivery",       "Tell me about a project where requirements changed significantly mid-way. How did you adapt?"),
        ("impact",         "Describe the most impactful technical improvement you have made to a system. How did you measure the impact?"),
        ("mentoring",      "Have you mentored a junior developer? What approach did you take and what challenges did you face?"),
        ("failure",        "Tell me about a significant technical failure or outage you were involved in. What was your role and what did you learn?"),
        ("trade-offs",     "Describe a time you had to choose between technical correctness and shipping speed. How did you decide?"),
    ],
    "senior": [
        ("strategy",       "Tell me about a time you influenced the technical direction of a team or product. How did you build consensus?"),
        ("architecture",   "Describe a complex system you designed from scratch. What trade-offs did you make and what would you do differently now?"),
        ("scale",          "Tell me about a time you scaled a system to handle 10x its original load. What broke and how did you fix it?"),
        ("cross-team",     "Describe a time you led a technically complex initiative that involved multiple teams. How did you manage dependencies?"),
        ("people",         "How have you handled a situation where a team member was consistently underperforming? What steps did you take?"),
        ("risk",           "Tell me about a high-risk technical decision you made. How did you assess the risk and what was the outcome?"),
        ("hiring",         "What qualities do you look for when hiring engineers? How do you evaluate them in an interview?"),
    ],
}

# Gap questions: why the skill matters in context and what the candidate would do
_GAP_BANK: Dict[str, Tuple[str, str, str]] = {
    # skill → (easy_q, medium_q, hard_q)
    "machine learning": (
        "This role requires machine learning knowledge. Can you describe any exposure you've had to ML concepts, even outside a professional context?",
        "Machine learning is central to this role but appears to be a gap in your background. How would you ramp up, and what resources would you use?",
        "The JD requires hands-on ML experience you currently lack. Describe how you would approach a project that required training and deploying a classification model for the first time.",
    ),
    "docker": (
        "Docker is listed as a requirement. Have you worked with containers in any capacity? What is your understanding of containerisation?",
        "You haven't listed Docker in your experience. How would you containerise an existing Python web application, and what challenges do you anticipate?",
        "Docker is a core tool in this role. Walk me through how you would migrate a legacy monolithic application to a containerised microservices architecture with zero downtime.",
    ),
    "kubernetes": (
        "Kubernetes appears in the job requirements but not your resume. What do you know about container orchestration?",
        "You lack Kubernetes experience. Given a Dockerfile, how would you write the Kubernetes manifests to deploy it with 3 replicas and a load balancer?",
        "Kubernetes is heavily used here and is a gap in your profile. Design a Kubernetes-based deployment strategy for a stateful service — walk us through the key Kubernetes resources you'd use.",
    ),
    "aws": (
        "This role uses AWS. What cloud platforms have you worked with and how transferable do you think those skills are?",
        "AWS experience is required but missing from your background. How would you host a Python REST API on AWS with auto-scaling and a managed database?",
        "AWS is core to this role. Design a serverless data pipeline on AWS that ingests from S3, transforms with Lambda, and stores in RDS — how would you handle failures and retries?",
    ),
    "react": (
        "React is a requirement here. Have you worked with any frontend frameworks? What similarities or differences do you see?",
        "You haven't listed React. Given a REST API, how would you build a React component that fetches data, handles loading and error states, and updates on user interaction?",
        "React is central to this role and isn't in your resume. Design a performant React dashboard that displays real-time data from a WebSocket — address re-rendering, state management, and accessibility.",
    ),
    "typescript": (
        "TypeScript is used in this team. Have you used statically-typed languages before? How comfortable are you learning TypeScript?",
        "TypeScript is listed as required but missing from your profile. How would you migrate a JavaScript file to TypeScript without breaking existing functionality?",
        "The codebase is fully in TypeScript. Design the type system for a plugin architecture where third-party developers can extend the platform — use generics, discriminated unions, and utility types.",
    ),
    "sql": (
        "This role requires SQL. Have you worked with relational databases in any way?",
        "SQL is a gap in your background. Write a query to find the top 5 customers by revenue in the last 30 days from a sales table with columns: customer_id, amount, created_at.",
        "Advanced SQL is needed here. Design the schema and write the queries for a leaderboard system that shows weekly and all-time rankings, handles ties, and updates in near-real-time.",
    ),
    "agile": (
        "The team follows Agile/Scrum. Have you worked in any structured delivery process before?",
        "You don't have Agile experience listed. How would you manage your own tasks in a two-week sprint, and how would you communicate blockers?",
        "This role involves leading Agile ceremonies. How would you run a sprint retrospective for a team that has missed three consecutive sprint goals?",
    ),
    "tensorflow": (
        "TensorFlow is used in this role. Have you worked with any deep learning framework?",
        "TensorFlow is a gap. How would you load a pre-trained image classification model in TensorFlow and use it to classify new images?",
        "TensorFlow is central here. Design a custom training loop in TensorFlow 2 that supports mixed-precision, gradient clipping, and learning rate warm-up.",
    ),
    "pytorch": (
        "PyTorch is used here. What is your familiarity with deep learning frameworks?",
        "PyTorch appears to be a gap. How would you define a simple feedforward network in PyTorch and train it on a custom dataset?",
        "The team uses PyTorch for research. Implement a custom loss function and a training loop with gradient accumulation for a scenario where batch size is limited by GPU memory.",
    ),
    "nlp": (
        "This role involves NLP. Can you describe any text processing work you've done?",
        "NLP is required but not in your background. How would you build a simple text classifier using pre-trained embeddings?",
        "NLP is core to this role. Design a production NLP pipeline that ingests raw documents, extracts named entities, performs sentiment analysis, and serves results via a REST API with sub-100ms latency.",
    ),
    "devops": (
        "This role has a DevOps component. What experience do you have with deployment or infrastructure?",
        "DevOps is a gap in your profile. How would you set up a basic CI/CD pipeline for a Python web application?",
        "The role requires owning the DevOps culture. Design an end-to-end platform — from local development to production — that includes observability, automated testing gates, and one-click rollback.",
    ),
    "graphql": (
        "GraphQL is used in this role. Have you worked with alternative API paradigms to REST?",
        "GraphQL is a gap. How would you convert a simple REST endpoint into a GraphQL query with arguments and a typed schema?",
        "GraphQL is the API layer here. Design a schema federation strategy for 8 independent services and explain how you would handle authentication, authorisation at the resolver level, and error handling.",
    ),
    "microservices": (
        "This role uses microservices architecture. Have you worked on distributed systems?",
        "Microservices is a gap. How would you split a monolithic e-commerce application into services — where would you draw the boundaries?",
        "Microservices experience is required. Design the inter-service communication strategy for a checkout flow that involves inventory, payment, notification, and order services — handle partial failures.",
    ),
    "ci/cd": (
        "CI/CD is listed as a requirement. Have you automated any part of a software delivery process?",
        "You don't have CI/CD experience. Describe how you would set up a GitHub Actions workflow to run tests, build a Docker image, and push it to a registry on every merge to main.",
        "CI/CD ownership is part of this role. Design a pipeline that supports trunk-based development, feature flags, automated security scanning, and progressive delivery to production.",
    ),
}

# Fallback gap question when the skill has no entry in _GAP_BANK
_GAP_FALLBACK = {
    "easy":   "The JD lists {skill} as a requirement that doesn't appear in your resume. What is your current knowledge level and how would you approach learning it?",
    "medium": "{skill} is a gap between your profile and the role requirements. Describe a plan to get up to speed within 30 days, and what you would deliver first.",
    "hard":   "{skill} is a critical requirement you currently lack. Design a concrete 90-day learning plan — including projects you would build — to demonstrate competency to the hiring team.",
}

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_DIFFICULTY_LEVELS = ("easy", "medium", "hard")
_EXPERIENCE_TIERS  = {
    "junior": (0, 2),    # 0–2 years
    "mid":    (2, 5),    # 2–5 years
    "senior": (5, 999),  # 5+ years
}
_TARGET_COUNTS = {
    "technical":  2,
    "behavioral": 1,
    "gap":        2,
}


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class InterviewGenerator:
    """
    Generates 5 personalised interview questions with no external calls.

    Question composition:
        2 × technical  — drawn from the candidate's matched skills
        1 × behavioral — tier-matched to the candidate's years of experience
        2 × gap        — one per top missing skill

    When matched skills < 2 or missing skills < 2, the generator fills the
    remaining slots with additional technical or behavioral questions so the
    total always equals 5.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_questions(
        self,
        resume_analysis: Optional[ResumeAnalysisResult],
        job_description: JobDescription,
        difficulty: str = "medium",
    ) -> List[InterviewQuestion]:
        """
        Parameters
        ----------
        resume_analysis : ResumeAnalysisResult | None
            Parsed resume data. If None, falls back to JD-only signals.
        job_description : JobDescription
            The target role with required/preferred skills.
        difficulty : str
            One of "easy", "medium", "hard".  Defaults to "medium".

        Returns
        -------
        List[InterviewQuestion]
            Always exactly 5 questions with unique ids q1–q5.
        """
        difficulty = self._normalise_difficulty(difficulty)
        logger.info(
            "Generating interview questions | difficulty=%s | role=%s",
            difficulty,
            job_description.title,
        )

        # ── Gather signals ─────────────────────────────────────────────
        matched_skills  = self._get_matched_skills(resume_analysis, job_description)
        missing_skills  = self._get_missing_skills(resume_analysis, job_description)
        experience_tier = self._get_experience_tier(resume_analysis)
        seed            = self._determinism_seed(resume_analysis, job_description)
        rng             = random.Random(seed)

        # ── Build question slots ───────────────────────────────────────
        questions: List[InterviewQuestion] = []

        # Slot 1 & 2 — Technical
        tech_qs = self._pick_technical(matched_skills, difficulty, rng, n=_TARGET_COUNTS["technical"])
        questions.extend(tech_qs)

        # Slot 3 — Behavioral
        beh_qs = self._pick_behavioral(experience_tier, difficulty, matched_skills, rng, n=_TARGET_COUNTS["behavioral"])
        questions.extend(beh_qs)

        # Slot 4 & 5 — Gap
        gap_qs = self._pick_gap(missing_skills, difficulty, rng, n=_TARGET_COUNTS["gap"])
        questions.extend(gap_qs)

        # ── Fill to exactly 5 ──────────────────────────────────────────
        questions = self._pad_to_five(questions, matched_skills, missing_skills, experience_tier, difficulty, rng)

        # Deduplicate (by question text, keep first occurrence)
        seen: set = set()
        unique: List[InterviewQuestion] = []
        for q in questions:
            key = q.question.strip().lower()
            if key not in seen:
                seen.add(key)
                unique.append(q)

        result = unique[:5]

        # Assign sequential ids
        for i, q in enumerate(result, 1):
            q.id = f"q{i}"

        logger.info(
            "Generated %d questions: %s",
            len(result),
            [q.type for q in result],
        )
        return result

    # ------------------------------------------------------------------
    # Signal extraction
    # ------------------------------------------------------------------

    def _get_matched_skills(
        self,
        resume: Optional[ResumeAnalysisResult],
        jd: JobDescription,
    ) -> List[str]:
        """Skills present in both the resume and the JD requirements."""
        if not resume:
            return []
        candidate = set(s.lower() for s in (resume.skills or []) + (resume.tools or []))
        required  = set(s.lower() for s in (jd.required_skills or []))
        preferred = set(s.lower() for s in (jd.preferred_skills or []))
        matched   = candidate & (required | preferred)
        # Preserve JD ordering so questions feel role-specific
        ordered   = [s for s in (jd.required_skills or []) if s.lower() in matched]
        extra     = [s for s in matched if s not in ordered]
        return ordered + extra

    def _get_missing_skills(
        self,
        resume: Optional[ResumeAnalysisResult],
        jd: JobDescription,
    ) -> List[str]:
        """Required skills absent from the resume."""
        if not resume:
            return list(jd.required_skills or [])
        candidate = set(s.lower() for s in (resume.skills or []) + (resume.tools or []))
        return [s for s in (jd.required_skills or []) if s.lower() not in candidate]

    def _get_experience_tier(self, resume: Optional[ResumeAnalysisResult]) -> str:
        years = (resume.experience_years or 0) if resume else 0
        for tier, (lo, hi) in _EXPERIENCE_TIERS.items():
            if lo <= years < hi:
                return tier
        return "mid"

    # ------------------------------------------------------------------
    # Pickers
    # ------------------------------------------------------------------

    def _pick_technical(
        self,
        matched_skills: List[str],
        difficulty: str,
        rng: random.Random,
        n: int,
    ) -> List[InterviewQuestion]:
        """Pick `n` technical questions from the candidate's matched skills."""
        idx = _DIFFICULTY_LEVELS.index(difficulty)
        pool: List[Tuple[str, str]] = []  # (skill, question_text)

        for skill in matched_skills:
            skill_l = skill.lower()
            entries = [e for e in _TECHNICAL_BANK if e[0] == skill_l]
            for entry in entries:
                # entry: (skill, easy, medium, hard)
                pool.append((skill_l, entry[idx + 1]))

        if not pool:
            # Fallback: any question at the right difficulty
            pool = [(e[0], e[idx + 1]) for e in _TECHNICAL_BANK]

        rng.shuffle(pool)
        seen_skills: set = set()
        picked = []
        for skill_l, q_text in pool:
            if skill_l not in seen_skills:
                seen_skills.add(skill_l)
                picked.append(
                    InterviewQuestion(
                        id="",
                        type="technical",
                        difficulty=difficulty,
                        skill=skill_l,
                        question=q_text,
                    )
                )
            if len(picked) == n:
                break

        return picked

    def _pick_behavioral(
        self,
        tier: str,
        difficulty: str,
        matched_skills: List[str],
        rng: random.Random,
        n: int,
    ) -> List[InterviewQuestion]:
        """Pick `n` behavioral questions suited to the candidate's experience tier."""
        pool = _BEHAVIORAL_BANK.get(tier, _BEHAVIORAL_BANK["mid"])
        candidates = list(pool)  # [(skill_context, question)]
        rng.shuffle(candidates)

        # Prefer questions whose skill_context overlaps with candidate skills
        skill_set = set(s.lower() for s in matched_skills)
        prioritised = sorted(
            candidates,
            key=lambda t: t[0].lower() in skill_set,
            reverse=True,
        )

        return [
            InterviewQuestion(
                id="",
                type="behavioral",
                difficulty=difficulty,
                skill=ctx,
                question=q_text,
            )
            for ctx, q_text in prioritised[:n]
        ]

    def _pick_gap(
        self,
        missing_skills: List[str],
        difficulty: str,
        rng: random.Random,
        n: int,
    ) -> List[InterviewQuestion]:
        """Pick `n` gap questions targeting the most impactful missing skills."""
        if not missing_skills:
            return []

        # Prioritise skills with a dedicated entry in _GAP_BANK
        has_entry  = [s for s in missing_skills if s.lower() in _GAP_BANK]
        no_entry   = [s for s in missing_skills if s.lower() not in _GAP_BANK]
        ordered    = has_entry[:n] + no_entry[: max(0, n - len(has_entry))]
        selected   = ordered[:n]

        idx = _DIFFICULTY_LEVELS.index(difficulty)
        questions  = []
        for skill in selected:
            skill_l = skill.lower()
            if skill_l in _GAP_BANK:
                q_text = _GAP_BANK[skill_l][idx]
            else:
                template = _GAP_FALLBACK[difficulty]
                q_text   = template.format(skill=skill)
            questions.append(
                InterviewQuestion(
                    id="",
                    type="gap",
                    difficulty=difficulty,
                    skill=skill_l,
                    question=q_text,
                )
            )

        return questions

    # ------------------------------------------------------------------
    # Padding
    # ------------------------------------------------------------------

    def _pad_to_five(
        self,
        questions: List[InterviewQuestion],
        matched_skills: List[str],
        missing_skills: List[str],
        tier: str,
        difficulty: str,
        rng: random.Random,
    ) -> List[InterviewQuestion]:
        """Fill any remaining slots to reach exactly 5 questions."""
        existing_texts = {q.question.strip().lower() for q in questions}
        result = list(questions)

        while len(result) < 5:
            needed = 5 - len(result)
            # Alternate: extra technical → extra behavioral → extra gap
            if len([q for q in result if q.type == "technical"]) < 4:
                extras = self._pick_technical(matched_skills, difficulty, rng, n=needed + 2)
            elif len([q for q in result if q.type == "gap"]) < 3 and missing_skills:
                extras = self._pick_gap(missing_skills, difficulty, rng, n=needed + 2)
            else:
                extras = self._pick_behavioral(tier, difficulty, matched_skills, rng, n=needed + 2)

            for q in extras:
                if q.question.strip().lower() not in existing_texts:
                    existing_texts.add(q.question.strip().lower())
                    result.append(q)
                    if len(result) == 5:
                        break

            # Safety: if we exhausted all sources, break to avoid infinite loop
            if not extras:
                break

        return result[:5]

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise_difficulty(difficulty: str) -> str:
        d = difficulty.strip().lower()
        return d if d in _DIFFICULTY_LEVELS else "medium"

    @staticmethod
    def _determinism_seed(
        resume: Optional[ResumeAnalysisResult],
        jd: JobDescription,
    ) -> int:
        """
        Produce a stable integer seed so the same resume+JD combination
        always yields the same questions.  Avoids randomness surprises
        between page reloads without requiring stored state.
        """
        parts = [jd.title, jd.description or ""]
        if resume:
            parts.append(resume.resume_id)
            parts.extend(sorted(resume.skills or []))
        raw = "|".join(parts).encode("utf-8")
        return int(hashlib.md5(raw).hexdigest(), 16) % (2**31)