# Contributing to SBEP Protocol

Thank you for your interest in improving the Source-Bound Execution Protocol (SBEP)!

## How to Contribute

### 1. Documentation Improvements

**Before Making Changes:**
- Read the current documentation thoroughly
- Check existing issues and discussions
- Understand the impact of your proposed changes

**Types of Documentation Contributions:**
- **Core Protocol Updates**: Changes to `SBEP-MANIFEST.md`
- **Template Improvements**: Updates to templates in `SBEP_Core/`
- **Example Projects**: New examples in `examples/`
- **Implementation Guides**: Step-by-step tutorials
- **Policy Clarifications**: Additions to `SBEP_Core/EXCEPTION-POLICIES/`

### 2. Contribution Process

#### Step 1: Document Your Intent
Create an issue describing:
- What problem you're solving
- Proposed solution approach
- Expected impact on existing implementations
- Backward compatibility considerations

#### Step 2: Make Changes
1. **Version Control**: All changes must increment version numbers appropriately
2. **Documentation**: Update `SBEP_Core/SBEP-POLICY-CHANGELOG.md`
3. **Testing**: Verify changes don't break existing implementations
4. **Examples**: Update or create examples if needed

#### Step 3: Review Process
- Self-review against SBEP principles
- Test with actual AI agent implementations
- Verify all documentation links and references
- Check that templates still work

### 3. Types of Changes

#### Core Protocol Changes (SBEP-MANIFEST.md)
**Requires:** Version increment + policy changelog entry

**Process:**
1. Update version number in `SBEP-MANIFEST.md`
2. Add entry to `SBEP_Core/SBEP-POLICY-CHANGELOG.md`
3. Update any affected templates
4. Create migration guide if needed

**Example:**
```markdown
## 2025-10-23
- v2.3 Added new agent initialization requirements
- v2.3 Enhanced terminal execution safety protocols  
- v2.3 Updated project structure standards for microservices
```

#### Template Updates
**Affects:** Files in `SBEP_Core/` with `-TEMPLATE` suffix

**Process:**
1. Update template files
2. Verify template completeness
3. Update `SBEP_Core/README.md` if new templates added
4. Test template with new project setup

#### New Examples
**Location:** `examples/{example-name}/`

**Requirements:**
- Complete, working example
- README.md with setup instructions  
- Demonstrates specific SBEP patterns
- Includes both success and failure scenarios

#### Policy Additions
**Location:** `SBEP_Core/EXCEPTION-POLICIES/`

**Format:** `EP-{CATEGORY}-{NUMBER}.md`
- **EP-DEP-001**: Deployment exception policy
- **EP-SEC-001**: Security exception policy
- **EP-INT-001**: Integration exception policy

### 4. Quality Standards

#### Documentation Quality
- **Clarity**: Non-technical stakeholders can understand intent
- **Completeness**: All necessary information included
- **Accuracy**: Technically correct and tested
- **Consistency**: Follows established patterns and terminology

#### Code Examples
- **Runnable**: All examples must work as written
- **Commented**: Explain why, not just what
- **Error Handling**: Show both success and failure paths
- **Cross-Platform**: Consider Windows/Mac/Linux differences

#### Process Compliance
- **RTFM First**: Document consultation requirements
- **Safety First**: Rollback and recovery procedures
- **Evidence-Based**: Show proof of concept testing

### 5. Review Criteria

Your contribution will be evaluated on:

#### Technical Merit
- [ ] Solves a real problem
- [ ] Maintains backward compatibility (or provides migration)
- [ ] Follows SBEP principles
- [ ] Includes proper error handling

#### Documentation Quality  
- [ ] Clear, concise writing
- [ ] Proper grammar and formatting
- [ ] All links work correctly
- [ ] Examples are complete and tested

#### Implementation Impact
- [ ] Changes benefit multiple use cases
- [ ] Doesn't add unnecessary complexity
- [ ] Maintains SBEP's core philosophy
- [ ] Provides clear value proposition

### 6. Common Contribution Areas

#### High-Priority Needs
- **Windows Terminal Improvements**: Better command execution patterns
- **Integration Templates**: Common API integration patterns
- **Error Recovery Guides**: Handling common failure scenarios
- **Performance Optimization**: Faster document lookup and processing

#### Documentation Gaps
- **Migration Guides**: Moving from other systems to SBEP
- **Troubleshooting**: Common issues and solutions  
- **Best Practices**: Proven patterns from real implementations
- **Tool Integration**: IDE plugins, CI/CD integration

### 7. Style Guide

#### Markdown Formatting
- Use `#` headers, not `===` underlining
- Code blocks must specify language: `bash`, `json`, `yaml`
- Use **bold** for important concepts, `code` for filenames
- Lists use `-` bullets, not `*` or `+`

#### File Naming
- Use kebab-case: `my-new-feature.md`
- Templates end with `-TEMPLATE`: `project-setup-TEMPLATE.md`  
- Policies use format: `EP-CATEGORY-NUMBER.md`
- Examples use descriptive directory names: `wordpress-integration/`

#### Content Structure
```markdown
# Title (H1 - only one per document)

Brief overview paragraph.

## Section (H2)

Content...

### Subsection (H3)

Details...

#### Sub-subsection (H4 - rare, use sparingly)
```

### 8. Testing Your Contributions

Before submitting:

1. **Spell Check**: Use a spell checker
2. **Link Check**: Verify all internal and external links
3. **Example Testing**: Run all code examples
4. **AI Agent Testing**: Have an AI agent follow your instructions
5. **Cross-Platform Check**: Consider different operating systems

### 9. Submission Checklist

- [ ] Issue created describing the change
- [ ] All files follow naming conventions
- [ ] `SBEP_Core/SBEP-POLICY-CHANGELOG.md` updated (if applicable)
- [ ] Version incremented (if applicable)  
- [ ] Examples tested and working
- [ ] Documentation links verified
- [ ] Backward compatibility maintained or migration provided
- [ ] Self-reviewed for clarity and completeness

### 10. Questions and Support

**Before Asking:**
- Search existing documentation
- Check the policy changelog for recent changes
- Review similar examples in the repository

**When Asking:**
- Provide specific examples
- Show what you've already tried
- Explain the business case for your change
- Include error messages or unexpected behavior

---

## Philosophy

SBEP contributions should embody the same principles we expect from AI agents:

- **Read First**: Understand existing solutions before proposing new ones
- **Document Everything**: Changes without documentation are incomplete
- **Safety First**: Consider the impact on existing implementations
- **Evidence-Based**: Prove your changes work in practice

Thank you for helping make SBEP better for everyone!
