# Submission Checklist & Video Guide

## Pre-Submission Checklist

### Code Quality ✓
- [x] All scripts are executable and well-documented
- [x] Code follows Python best practices
- [x] Error handling is robust
- [x] No hardcoded credentials

### Functionality ✓
- [x] Pipeline A (Demo → v1) works end-to-end
- [x] Pipeline B (Onboarding → v2) works end-to-end
- [x] Batch processing works for multiple files
- [x] Version comparison utility works
- [x] Output validation works
- [x] Changelog generation works

### Data Quality ✓
- [x] Extraction avoids hallucination
- [x] Missing data is flagged in questions_or_unknowns
- [x] Prompts follow conversation hygiene rules
- [x] Transfer and fallback protocols are clear
- [x] Business and after-hours flows are distinct

### Documentation ✓
- [x] README.md is comprehensive
- [x] SETUP_GUIDE.md has step-by-step instructions
- [x] All scripts have --help documentation
- [x] Schema examples are provided
- [x] N8N setup is documented

### Zero-Cost Constraint ✓
- [x] Uses only Anthropic free tier
- [x] No paid services or subscriptions
- [x] All tools are open-source or free
- [x] Reproducible by reviewers

## Submission Package

Your repository should include:

```
clara-automation-pipeline/
├── README.md                          # Main documentation
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment template
├── .gitignore                         # Git ignore rules
│
├── docs/
│   ├── SETUP_GUIDE.md                 # Step-by-step setup
│   └── SUBMISSION_GUIDE.md            # This file
│
├── scripts/
│   ├── extraction_engine.py           # Core extraction logic
│   ├── prompt_generator.py            # Agent prompt generation
│   ├── pipeline_a_demo.py             # Demo call pipeline
│   ├── pipeline_b_onboarding.py       # Onboarding pipeline
│   ├── batch_process.py               # Batch processing
│   ├── compare_versions.py            # Version comparison
│   └── validate_outputs.py            # Output validation
│
├── workflows/
│   └── N8N_SETUP.md                   # n8n documentation
│
├── sample_data/
│   ├── demo_call_1_acme.txt           # Sample demo call
│   └── onboarding_call_1_acme.txt     # Sample onboarding
│
└── outputs/
    └── accounts/
        └── ACC001_acme_fire_protection/
            ├── v1/
            │   ├── account_memo.json
            │   ├── agent_spec.json
            │   └── extraction_log.json
            ├── v2/
            │   ├── account_memo.json
            │   ├── agent_spec.json
            │   └── extraction_log.json
            └── changelog.json
```

## Video Demonstration Guide (3-5 minutes)

### Video Structure

**Introduction (30 seconds)**
- Your name
- Assignment overview
- What you built

**Demo Part 1: Pipeline A (60 seconds)**
- Show terminal command running
- Show v1 outputs being generated
- Highlight account_memo.json structure
- Point out questions_or_unknowns

**Demo Part 2: Pipeline B (60 seconds)**
- Show onboarding processing
- Show v2 outputs
- Show changelog.json
- Highlight what changed

**Demo Part 3: Comparison (45 seconds)**
- Run compare_versions.py
- Show side-by-side diff
- Highlight resolved unknowns

**Demo Part 4: Batch Processing (45 seconds)**
- Show batch processing multiple files
- Show summary report
- Show all generated accounts

**Wrap-up (30 seconds)**
- Mention zero-cost approach
- Highlight key features
- Thank reviewers

### Recording Tips

1. **Clean Terminal**:
   ```bash
   clear
   # Set nice prompt
   export PS1="\[\e[1;32m\]\w\[\e[0m\] $ "
   ```

2. **Zoom In**: Make terminal text readable (18pt+ font)

3. **Pre-run**: Test commands before recording

4. **Script**: Have a script of what to say

5. **Pace**: Speak clearly, not too fast

6. **Screen Share**: Use Loom or similar tool

### Example Script

```
"Hi, I'm [Your Name]. For the Clara Answers intern assignment, 
I built a zero-cost automation pipeline that converts demo and 
onboarding calls into production-ready Retell AI agents.

Let me show you how it works.

First, I'll process a demo call for Acme Fire Protection. I'm 
running pipeline_a_demo.py with the transcript as input...

[Run command]

As you can see, it generated a v1 account memo with all the 
structured data extracted from the demo call. Notice the 
questions_or_unknowns field - these are gaps that need to be 
filled during onboarding.

Now let's process the onboarding call for the same company...

[Run pipeline B]

The system merged the new information with v1 and generated v2. 
Here's the changelog showing exactly what changed. Business 
hours went from vague to precise, emergency contacts were added, 
and integration constraints were clarified.

Let me show you the comparison tool...

[Run compare]

You can see v1 versus v2 side by side. The agent is now 
production-ready with no unknowns remaining.

Finally, here's batch processing for multiple companies at once...

[Run batch]

It processed 5 demo calls and 5 onboarding calls in sequence, 
generating all outputs automatically.

Everything runs on free-tier APIs - zero cost. The code is 
well-documented, modular, and ready for production scaling.

Thanks for reviewing my submission!"
```

## Common Issues to Avoid

### In Video

❌ Don't show your API key
❌ Don't have messy terminal with errors
❌ Don't go over 5 minutes
❌ Don't skip showing actual outputs
❌ Don't forget to show changelog

### In Code

❌ Don't commit .env with real keys
❌ Don't have broken imports
❌ Don't have hardcoded paths
❌ Don't skip error handling
❌ Don't ignore the zero-cost constraint

## Final Checks Before Submission

### 1. Clean Repository

```bash
# Remove any test artifacts
rm -rf outputs/test_*
rm -rf __pycache__

# Ensure .env is in .gitignore
git status  # Should not show .env
```

### 2. Test Fresh Install

```bash
# In a new directory
git clone <your-repo>
cd clara-automation-pipeline
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add API key to .env
python scripts/pipeline_a_demo.py --input sample_data/demo_call_1_acme.txt --account-id ACC001
```

### 3. Validate All Outputs

```bash
python scripts/validate_outputs.py
```

Should show all green checkmarks.

### 4. Check Documentation

- [ ] README has clear setup instructions
- [ ] Sample commands work as written
- [ ] Links are not broken
- [ ] Examples match actual output format

### 5. Record Video

- [ ] Audio is clear
- [ ] Screen is readable
- [ ] Demo flows smoothly
- [ ] Under 5 minutes
- [ ] Uploaded to Loom or YouTube

## Submission

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Complete Clara Answers automation pipeline"
   git push
   ```

2. **Make Repository Accessible**
   - Public repo, OR
   - Private repo with access granted to reviewers

3. **Submit**
   - GitHub repository URL
   - Loom video URL
   - Brief cover note (optional)

## Cover Note Template

```
Subject: Clara Answers Intern Assignment - [Your Name]

Hi Clara Team,

I'm excited to submit my automation pipeline assignment!

Repository: [GitHub URL]
Demo Video: [Loom URL]

Key Features:
- Zero-cost implementation using Claude API free tier
- End-to-end pipelines for demo and onboarding calls
- Robust version control with detailed changelogs
- Batch processing for 10+ calls
- Comprehensive validation and error handling

The system successfully processes the 5 demo + 5 onboarding 
dataset with no errors. All outputs follow the required schema 
and prompt hygiene rules.

Tech Stack:
- Python 3.9+
- Anthropic Claude API (free tier)
- Local JSON storage
- Git for version control

Looking forward to discussing the implementation!

Best regards,
[Your Name]
```

## Evaluation Criteria Alignment

Make sure your submission addresses:

### A) Automation and Reliability (35 points)
- ✓ Runs end-to-end on all 10 files
- ✓ Batch processing with error handling
- ✓ Clear logs and failure handling
- ✓ Idempotent operations

### B) Data Quality and Prompt Quality (30 points)
- ✓ No hallucination - flags unknowns explicitly
- ✓ Prompts follow conversation hygiene
- ✓ Transfer and fallback logic is solid
- ✓ Correct extraction without inventing facts

### C) Engineering Quality (20 points)
- ✓ Clean, modular architecture
- ✓ Proper versioning and diff tracking
- ✓ Good logs and debuggability
- ✓ Reusable code patterns

### D) Documentation and Reproducibility (15 points)
- ✓ Comprehensive README
- ✓ Step-by-step setup guide
- ✓ We can run it from your instructions
- ✓ Clear outputs and file structure

### Bonus Points
- ✓ Diff viewer (compare_versions.py)
- ✓ Batch processing with metrics
- ✓ Validation script
- ✓ Sample data included

## Good Luck!

You've built a solid automation pipeline. Make sure your video 
demonstrates it clearly, and your documentation helps reviewers 
reproduce your results.

Questions? Review the main README.md and SETUP_GUIDE.md.

---

**Remember**: This assignment tests systems thinking, not just 
coding. Show that you understand the business problem, handle 
uncertainty well, and built something production-ready.
