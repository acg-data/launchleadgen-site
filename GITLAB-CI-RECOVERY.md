# GitLab CI recovery

The recovered GitHub Actions workflows now have native jobs in `.gitlab/ci/` and shell steps in `.gitlab/scripts/`.
Pushes and merge requests run the original checks. In Build â†’ Pipelines â†’ New pipeline, select the `workflow` input to run a particular former manual workflow. Its other inputs appear in the same form.

## Release activation

Publishing and operational write jobs are manual during recovery. This avoids deploying recovered source over newer live releases before provider variables and source drift are reconciled. The job keeps the original branch and input restrictions.
A green build alone does not mean a deployment occurred. Read the publish job result and provider deployment record.

## Variables

Restore the following names under Settings â†’ CI/CD â†’ Variables. Use masked values for secrets and protect write credentials. Secret values could not be exported from the suspended GitHub account.

- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`
