# DrivePilot Simulator Documentation Repository

**ALWAYS follow these instructions first and only search for additional context if the information provided here is incomplete or found to be in error.**

This is a minimal documentation-only repository for the Drive Pilot automotive project. It contains project meeting transcripts and documentation related to autonomous driving features including driver monitoring, adaptive speed limiting, OTA updates, obstacle detection, and regulatory compliance.

## Repository Structure

**VALIDATED REPOSITORY CONTENTS:**
```
drivepilot-simulator/
├── .gitignore          # Python-focused gitignore with general exclusions
├── .github/
│   └── copilot-instructions.md  # This file
└── content/
    └── transcript.md   # OEMagic Teams call transcript for Drive Pilot project
```

## Working Effectively

### Prerequisites
- **NO BUILD SYSTEM**: This repository contains no source code, build scripts, or dependencies
- **NO INSTALLATION REQUIRED**: No SDKs, compilers, or runtime environments needed
- **TEXT EDITING ONLY**: Standard text editor or IDE sufficient for working with markdown files

### Key Project Information
Based on `content/transcript.md`, this repository documents a Drive Pilot autonomous vehicle project with these key requirements:
- **DP-601**: Real-Time Driver Monitoring (camera-based gaze tracking)
- **DP-602**: Adaptive Speed Limiting (maps, weather, traffic integration)  
- **DP-603**: OTA Update Support (secure updates with rollback)
- **DP-604**: Enhanced Obstacle Detection (sensor fusion)
- **DP-605**: Regulatory Mode Switching (geofencing compliance)

### Common Operations

#### View Repository Contents
```bash
# List all files (VALIDATED - works immediately)
ls -la

# View transcript content (VALIDATED - works immediately)  
cat content/transcript.md
```

#### Edit Documentation
```bash
# Edit transcript file (VALIDATED - no build required)
# Use any text editor like nano, vim, or IDE
nano content/transcript.md
```

#### Git Operations
```bash
# Check repository status (VALIDATED - works immediately)
git status

# View commit history (VALIDATED - works immediately)
git log --oneline

# View branches (VALIDATED - works immediately) 
git branch -a
```

## Validation

### NO BUILD OR TEST COMMANDS
- **There are no build commands** - repository contains only documentation
- **There are no test suites** - no automated testing infrastructure
- **There are no linting tools** - standard markdown formatting sufficient
- **There are no dependencies to install** - pure documentation repository

### Manual Validation Steps
When making changes to documentation:
1. **READ TRANSCRIPT**: Always review `content/transcript.md` to understand project context
2. **MARKDOWN VALIDATION**: Ensure markdown syntax is correct by previewing files
3. **CONTENT CONSISTENCY**: Verify any new content aligns with existing Drive Pilot project information
4. **GIT STATUS**: Always run `git status` to see what files have been modified

### Expected Timings
- **Repository clone**: < 5 seconds (minimal content)
- **File viewing/editing**: Instant (no compilation required)
- **Git operations**: < 2 seconds (small repository size)

## Project Context

### Drive Pilot Features (from transcript.md)
The repository documents an automotive autonomous driving system with these components:
- **Driver Monitoring**: Camera-based gaze tracking with 5-second alert threshold
- **Speed Control**: Dynamic speed limiting based on environmental conditions
- **Update System**: Secure OTA updates with rollback capability  
- **Obstacle Detection**: Multi-sensor fusion (IR, radar, ultrasonic)
- **Regulatory Compliance**: GPS-based geofencing for regional requirements

### Team Roles (from transcript.md)
- **Sherry**: Project Manager
- **Fu**: Requirements Engineer  
- **Tanvi**: Software Engineer
- **Dennis**: Test Engineer
- **Pavan**: Homologation Engineer

## Important Notes

### What This Repository IS:
- Documentation and meeting transcripts for Drive Pilot project
- Reference material for automotive autonomous driving requirements
- Project planning and technical discussion records

### What This Repository IS NOT:
- **NOT a source code repository** - contains no implementation
- **NOT a build environment** - no compilation or build processes
- **NOT a test suite** - no automated testing infrastructure  
- **NOT a deployment system** - no runtime or execution environment

### Working with Changes
- Changes are limited to documentation updates
- No code compilation, testing, or deployment required
- Focus on maintaining accurate project documentation
- Ensure consistency with automotive industry standards referenced in transcripts

## Quick Reference Commands

```bash
# Essential commands that work immediately:
pwd                     # Current directory
ls -la                  # List all files  
cat content/transcript.md  # View main content
git status              # Check repository state
git log --oneline       # View commit history
```

**Remember**: This is a documentation-only repository. Do not expect or attempt to find source code, build scripts, test suites, or runtime environments.