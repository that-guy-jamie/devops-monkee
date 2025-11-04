# Success Tool Capture Process (SBEP Validated)

## The Distinction

**SBEP's Role:** Define and validate the **process** of capturing success tools
**Tool Ownership:** Tools stay private/proprietary (GitLab, internal repos)
**Metadata Ownership:** All metadata stays private - nothing exposed publicly

## Why Keep Everything Private?

Exposing tool metadata publicly would reveal:
- Your competitive advantages
- Problems you're solving internally
- Your internal workflow patterns
- Technology stack hints
- Strategic direction

**Solution:** SBEP validates process compliance in your private repo. Nothing goes public.

## The Process (SBEP Validated - Private Only)

### 1. Success Identification
When a project succeeds, follow SBEP-mandated process:

**SBEP Validates (in private repo):**
- Success criteria are documented
- Tools/processes that enabled success are identified
- Documentation of "why this tool mattered" exists

**Everything stays private** - no public exposure

### 2. Tool Extraction
Extract successful tools following SBEP standards:

**SBEP Validates (in private repo):**
- Tool has clear purpose statement (private)
- Tool has usage documentation (private)
- Tool has integration points documented (private)
- Tool follows SBEP naming/structure conventions

**Tool Location:** Private repo only, organized by project type

### 3. Tool Registration (Private Only)
Register tool in private SBEP index for internal tracking:

**SBEP Validates (Process Only):**
- Process for registering tools exists
- Tool structure follows SBEP conventions
- Documentation standards are met
- **NO tool names, purposes, or metadata exposed publicly**

**Tool Location:** Private repo only, tracked in private SBEP index

### 4. Tool Reuse
When starting new project, reference successful tools:

**SBEP Validates (in private repo):**
- Tool references exist in project mandate (private)
- Tool integration points are documented (private)
- Tool versions are tracked (private)

**Tool Location:** Private repo tools referenced from new project

## Example: Successful Project Tool Capture

### Process (SBEP Validated - Private Repo Only)
1. **Identify Success:** Project completed with 95% SBEP compliance (private)
2. **Document Tools:** Custom validation tool, data protection scanner, system health monitor (private)
3. **Extract Tools:** Package tools following SBEP structure (private)
4. **Register:** Add to private `sds/SBEP-INDEX.yaml` in internal repo (private)
5. **Validate:** SBEP checks process was followed correctly (private validation)

### Tools (Private/Proprietary)
- `tools/custom-validator.ts` - Internal private repo
- `tools/data-protection-scanner.ts` - Internal private repo  
- `tools/system-monitor.ts` - Internal private repo

### SBEP Validation (Process Only)
```bash
# SBEP checks process was followed (in private repo)
devops-monkee success:validate ./example-project

# Validates (all private):
# - Process documentation exists ✓
# - Tool structure follows conventions ✓
# - Documentation standards met ✓
# - NO tool names/metadata exposed publicly ✓
```

**Tool registry stays completely private** - only in internal repo.

## SBEP Commands (Private Repo Only)

### Validate Success Capture Process

```bash
# Validate that success tools were captured following SBEP process
# Runs in your private GitLab repo - nothing goes public
devops-monkee success:validate ./project-path

# Checks (all private):
# - Success criteria documented?
# - Tools identified and documented?
# - Tools registered in private SBEP index?
# - Tool structure follows SBEP standards?
# - Process compliance met?
```

### Audit Success Tools (Private)

```bash
# Audit all success tools in private repo
# Results stay private - never exposed publicly
devops-monkee success:audit

# Reports (private only):
# - Which tools exist (internal)
# - Which tools are referenced by active projects (internal)
# - Which tools haven't been reused (internal)
# - Process compliance status (internal)
```

## Process Compliance Checklist

SBEP validates these elements exist (in private repo):

- [ ] Success criteria documented
- [ ] Tools that enabled success identified
- [ ] Each tool has purpose statement (private)
- [ ] Each tool has usage documentation (private)
- [ ] Tools registered in private SBEP index
- [ ] Tool structure follows SBEP conventions
- [ ] Tool metadata includes source project and success metrics (private)
- [ ] Tool versioning tracked (private)
- [ ] Integration points documented (private)

**Everything above stays in private GitLab repo. Nothing exposed publicly.**

## Repository Structure

### Public (GitHub: devops-monkee)
- SBEP protocol definition
- Process validation framework
- Process standards (how to capture tools)
- **NO tool metadata**
- **NO tool registry**
- **NO competitive intelligence**

### Private (GitLab: sbep-protocol)
- Extracted success tools (code)
- Project-specific implementations
- Proprietary tool registry (metadata)
- Private SBEP index with success tools section
- All competitive intelligence stays private
- All tool names and purposes stay private

## Benefits

1. **Process Standardization** - SBEP ensures consistent tool capture (validated privately)
2. **Tool Privacy** - Tools and metadata completely private
3. **Competitive Protection** - No exposure of capabilities or advantages
4. **Validation** - SBEP validates process compliance (in private repo)
5. **Reusability** - Tools available for future projects (privately)
6. **Quality** - Process ensures tools are well-documented (private docs)

## Implementation

SBEP validates **process compliance only** (in private repo):
- Process was followed (checklist completion)
- Documentation structure follows standards
- Tool organization meets conventions
- **No tool names or purposes exposed**
- **No metadata shared publicly**
- **No competitive intelligence leaked**

Tools, metadata, and registry remain completely private. SBEP only ensures the **process** for capturing success tools is followed correctly. The actual tools, their purposes, and what problems they solve stay in your private GitLab repo.

**Public SBEP framework** → Defines process standards
**Private execution** → Your tools, your metadata, your competitive advantages stay private
