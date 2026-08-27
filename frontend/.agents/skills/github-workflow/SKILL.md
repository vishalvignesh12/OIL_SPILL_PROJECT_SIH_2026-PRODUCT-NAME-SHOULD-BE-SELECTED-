---
name: github-workflow
description: Safely work on a shared GitHub repository while protecting other developers' changes and keeping frontend work isolated.
---

# GitHub Team Workflow Skill

This is a shared repository.

The developer may be working on a personal feature branch.

## Before modifying files

Inspect:

- current branch
- git status
- existing changes

Never assume the working tree is clean.

## Protect other developers

Do NOT:

- delete unrelated files
- overwrite another developer's work
- reset the repository
- discard uncommitted changes
- rewrite history
- force push

Never run:

git reset --hard

git clean -fd

git push --force

unless explicitly instructed by the developer.

## Scope

The developer is primarily responsible for frontend work.

Prefer modifying:

- frontend files
- React source
- frontend configuration
- frontend documentation

Do not modify backend/database code unless explicitly requested or required and approved.

## Before committing

Check:

git status

Review changed files.

Only commit files related to the current task.

## Commit

Use clear commit messages.

Example:

feat: build oil spill dashboard

fix: handle vessel API error

feat: add AIS map visualization

## Push

Never force push.

Push only the current feature branch.

## Collaboration

Do not merge branches automatically.

Do not modify main/master automatically.

Do not create pull requests unless explicitly requested.