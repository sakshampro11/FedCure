# Deploy FedCure: Render + Vercel

## Before you start

1. Push this revision to a private GitHub or GitLab repository. Never commit patient CSVs, API keys, .env files, or database URLs.
2. Choose your Vercel project name. Its initial URL normally looks like https://YOUR-PROJECT.vercel.app.
3. This guide deploys a single Render API instance. Do not scale the API horizontally without adding distributed coordination for aggregation.

## 1. Create the Vercel project

Create a Vercel project from this repository:

- Set **Root Directory** to frontend.
- Keep the detected **Next.js** framework settings.
- Add this Production environment variable. It is safe to expose because it is an API URL, not a secret.

    NEXT_PUBLIC_API_URL=https://placeholder.invalid

Deploy once. Copy the resulting Vercel URL; it is required by the API's CORS configuration. The site will not work yet because the API URL is deliberately a placeholder.

## 2. Create the Render Blueprint

In Render, choose **New +** → **Blueprint**, select the same repository, and use the root-level render.yaml.

The Blueprint creates:

- fedcure-api, a Docker web service in Singapore.
- fedcure-db, a private Render Postgres database.
- A generated JWT_SECRET; do not replace it with a weaker value.
- A required REGISTRATION_TOKEN. Enter a new, unique random value of at least 32 characters when Render prompts for it.

Render prompts for ALLOWED_ORIGINS. Enter the exact Vercel URL from step 1, without a trailing slash:

    https://YOUR-PROJECT.vercel.app

If you later add a custom Vercel domain, use a comma-separated value:

    https://YOUR-PROJECT.vercel.app,https://app.example.com

Approve the selected paid Render plans only after reviewing their pricing. PyTorch workloads and persistent Postgres state are not suitable for a sleeping/free API service.

Wait for Render to report a successful deploy, then open:

    https://YOUR-RENDER-API.onrender.com/api/health

It must return a JSON response with status set to healthy.

## 3. Point Vercel at Render

In Vercel → Project → Settings → Environment Variables, replace the placeholder with:

    NEXT_PUBLIC_API_URL=https://YOUR-RENDER-API.onrender.com

Redeploy the Vercel project. NEXT_PUBLIC variables are embedded during the frontend build, so changing the value requires a new deployment.

## 4. Smoke test

1. Open the Vercel site and register one test hospital using the REGISTRATION_TOKEN from step 2 as the network enrollment code.
2. Copy the API key shown on the confirmation screen. It is displayed only once.
3. Log in with that key.
4. Open the dashboard. It should load an empty training history instead of showing an API or CORS error.
5. In Render logs, verify that the API started without configuration errors.

## Run federated training

The global model starts as version v0 with random weights. Predictions become meaningful only after at least one completed aggregation round.

REQUIRED_HOSPITALS is 4 by default. Use the network enrollment code to register four distinct hospitals and retain each hospital's API key separately. The API key is the hospital client identity; the client does not need a separate numeric identifier.

Each hospital runs the client beside its own private CSV. The file must have these columns:

    age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,target

On a trusted machine with Docker and a reviewed checkout of this repository:

    docker build -t fedcure-client:latest ./client

    docker run --rm `
      -e SERVER_URL="https://YOUR-RENDER-API.onrender.com" `
      -e API_KEY="fc_THE_HOSPITALS_PRIVATE_KEY" `
      -e NUM_ROUNDS=1 `
      -e EPOCHS_PER_ROUND=3 `
      -v "${PWD}/data/hospital_1.csv:/data/hospital.csv" `
      fedcure-client:latest

Run the command once for each of the four hospital keys and datasets. When the fourth unique update arrives, the API creates model v1 and the dashboard records round 1. Repeat with NUM_ROUNDS=1 for deliberate, observable rounds.

Do not place API keys in Vercel, Render, browser code, screenshots, or shared chat messages. Store them in a hospital-controlled secret manager.

## Operations checklist

- Keep Render and Vercel accounts protected with MFA.
- Restrict repository access because the client source and deployment topology are sensitive.
- Monitor Render deploy and application logs.
- Back up Render Postgres before schema changes.
- Rotate a hospital API key by creating a replacement hospital credential before deactivating the old record. A dedicated key-rotation endpoint is not yet implemented.
- Treat the model and training data as sensitive. Differential-privacy noise in this demo does not by itself establish regulatory compliance.
