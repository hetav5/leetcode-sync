# 🤖 Fully Automated Setup Guide — GitHub Actions

> **Goal:** Your LeetCode submissions auto-sync to Notion **every single day**, with zero effort from you.
> **Cost:** ₹0. Completely free, forever.
> **Time to set up:** 15-20 minutes (one-time)

---

## 💰 Free Tier Math (so you know it's truly free)

GitHub Actions gives you for private repos:
- **2,000 free minutes per month**

Our script runs once a day, takes ~30 seconds = ~15 minutes per month.
**You're using less than 1% of the free tier.** Both you AND your friend can each have your own repo and never pay a rupee.

If you ever want to make the repo public, it's **literally unlimited minutes**.

---

## 📋 What You'll End Up With

```
Daily at 7:30 PM IST:
  └─ GitHub triggers the workflow
     └─ Workflow runs the Python script
        └─ Script fetches your LeetCode submissions
           └─ Pushes new ones to Notion
              └─ You wake up to an updated Notion ✨
```

You literally do nothing. The grind shows up in Notion on its own.

---

## 🛠️ Step-by-Step Setup

### Part 1: Prepare Your Files (5 minutes)

You need 2 files:
1. `leetcode_to_notion.py` — the script (provided)
2. `.github/workflows/sync.yml` — the GitHub Actions workflow (provided)

Plus a `requirements.txt` for dependencies. Let me list them:

**requirements.txt:**
```
requests
python-dotenv
```

---

### Part 2: Get Your Credentials (5 minutes)

You need **5 secrets**. Have a notepad ready.

#### 🍪 LeetCode Cookies (2 values)
1. Log in to [leetcode.com](https://leetcode.com)
2. Press `F12` to open DevTools
3. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
4. Click **Cookies** → `https://leetcode.com` on the left
5. Find and copy these two values:
   - `LEETCODE_SESSION` (long string, ~600+ characters)
   - `csrftoken` (shorter string, ~64 characters)

#### 👤 LeetCode Username
- Your LeetCode username (visible in your profile URL: `leetcode.com/u/YOUR_USERNAME`)

#### 🔑 Notion Integration Token
1. Go to [notion.so/my-integrations](https://notion.so/my-integrations)
2. Click **"+ New integration"**
3. Name it: `LeetCode Sync`
4. Associated workspace: pick yours
5. Click **Submit**
6. Copy the **"Internal Integration Secret"** (starts with `secret_...` or `ntn_...`)

#### 🗂️ Notion Database ID
1. Open your "Problem Tracker" database in Notion (the one Notion AI built)
2. Click **"..."** (top right) → **"Connections"** → search for and add `LeetCode Sync`
3. Click **"Share"** button → also confirm the integration has access
4. Copy the URL of the database. It looks like:
   ```
   https://notion.so/myworkspace/abc123def456...?v=xyz789...
                                  ^^^^^^^^^^^^^^^^
                                  This is the database ID
   ```
   The database ID is the 32-character string before `?v=`

---

### Part 3: Create the GitHub Repo (5 minutes)

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `leetcode-notion-sync`
3. **Set to Private** (important — your secrets are encrypted but private is safer)
4. Check **"Add a README file"**
5. Click **Create repository**

#### Upload the files:
1. Click **"Add file"** → **"Upload files"**
2. Drag in these 3 files:
   - `leetcode_to_notion.py`
   - `requirements.txt` (create this with the 2 lines above)
3. Commit changes
4. Now create the workflow file:
   - Click **"Add file"** → **"Create new file"**
   - Name it: `.github/workflows/sync.yml` (yes, with the slashes — GitHub auto-creates folders)
   - Paste the content of `sync.yml` (provided)
   - Commit

---

### Part 4: Add Secrets to GitHub (5 minutes)

This is where your credentials live, **encrypted**.

1. In your repo, go to **Settings** (top right)
2. In the left sidebar, click **Secrets and variables** → **Actions**
3. Click **"New repository secret"** for each of these:

| Secret Name | Value |
|---|---|
| `LEETCODE_SESSION` | Your session cookie (long string) |
| `LEETCODE_CSRF` | Your csrftoken cookie |
| `LEETCODE_USERNAME` | Your LeetCode username |
| `NOTION_TOKEN` | Your Notion integration token |
| `NOTION_DATABASE_ID` | Your database ID |
| `SOLVED_BY` | `Me` (or `Friend` for your friend's repo) |

Save each one. **GitHub encrypts them** — nobody (not even you) can read them again after saving. They're only used at runtime.

---

### Part 5: Test It! (1 minute)

1. Go to the **Actions** tab in your repo
2. Click **"LeetCode to Notion Sync"** workflow (left sidebar)
3. Click **"Run workflow"** → **"Run workflow"** (green button)
4. Wait ~30 seconds, refresh
5. Click the running/completed workflow to see logs
6. Check your Notion — your submissions should be there!

If you see ✅ green checkmark → you're done. The workflow now runs every day automatically.

If you see ❌ red X → click into it to see the error. 99% of issues are:
- Wrong property names in Notion database (must be EXACT)
- Expired LeetCode cookie (just refresh from browser)
- Integration not shared with the database

---

## 👥 For Your Friend

Your friend does the **same setup in their own GitHub account** with:
- Their own LeetCode cookies
- Same Notion token + database ID (you share these — both write to the same DB)
- `SOLVED_BY` = `Friend`

To share the Notion DB with your friend's integration:
- You don't need a separate Notion integration for them — they use the same one, OR
- You create a second integration and share the DB with both

**Simpler:** Just give your friend the Notion token + DB ID, and they use them. Notion integrations don't have per-user limits.

---

## ⏰ Changing the Schedule

The workflow runs daily at **7:30 PM IST** (14:00 UTC). To change it, edit the cron in `sync.yml`:

```yaml
schedule:
  - cron: '0 14 * * *'   # Format: minute hour day month day-of-week
```

Examples:
- `'0 14 * * *'` → 14:00 UTC = **7:30 PM IST**
- `'30 18 * * *'` → 18:30 UTC = **12:00 AM IST (midnight)**
- `'0 4 * * *'` → 04:00 UTC = **9:30 AM IST**
- `'0 */6 * * *'` → every 6 hours

Use [crontab.guru](https://crontab.guru) to build custom schedules visually.

> ⚠️ **GitHub Actions caveat:** Scheduled workflows on free tier can be delayed by 10-30 minutes during peak hours. Not a problem for once-a-day syncing.

---

## 🚨 Maintenance (Monthly Check-In)

### LeetCode cookies expire every ~30 days
**Symptom:** Workflow starts failing, logs say "Failed to fetch from LeetCode"

**Fix:** Just refresh the cookies in GitHub secrets
1. Re-grab `LEETCODE_SESSION` from browser DevTools
2. Go to repo Settings → Secrets → click `LEETCODE_SESSION` → Update
3. Done

**Tip:** Set a calendar reminder for the 1st of each month to refresh cookies.

---

## 🔒 Security FYI

You might think: *"Wait, my LeetCode session is stored on GitHub??"*

Here's the truth:
- ✅ GitHub Secrets are **encrypted at rest** with industry-standard encryption
- ✅ They're only decrypted **inside the workflow runner** for ~30 seconds
- ✅ Even repo admins **cannot view** secret values after saving
- ✅ The repo is **private** — only you can access it
- ✅ Worst case scenario if leaked: someone can see your LeetCode history. Not catastrophic.

This is the same security model used by professional engineering teams. You're fine.

---

## ✅ Final Checklist

- [ ] Created private GitHub repo `leetcode-notion-sync`
- [ ] Uploaded `leetcode_to_notion.py` and `requirements.txt`
- [ ] Created `.github/workflows/sync.yml`
- [ ] Added all 6 secrets to repo settings
- [ ] Shared Notion database with the integration
- [ ] Ran the workflow manually once → succeeded
- [ ] Saw new submissions appear in Notion 🎉
- [ ] Your friend did the same with their account

---

## 🎁 Bonus: Add a Sync Status Badge to Notion

In your Notion dashboard, add this to show whether your sync is healthy:

1. Get your badge URL:
   ```
   https://github.com/YOUR_USERNAME/leetcode-notion-sync/actions/workflows/sync.yml/badge.svg
   ```
2. In Notion, use `/image` and paste the URL
3. You'll see a 🟢 green badge if sync is healthy, 🔴 red if failing

Glanceable status. Looks pro.

---

## 🆘 Common Errors

| Error | Cause | Fix |
|---|---|---|
| `Failed to fetch from LeetCode` | Expired cookie | Refresh `LEETCODE_SESSION` secret |
| `Notion: object_not_found` | Integration not shared with DB | Share DB with integration in Notion |
| `Notion: validation_error` | Property names don't match | Check DB columns match exactly (case-sensitive) |
| `Missing environment variables` | Forgot to add a secret | Add all 6 secrets in repo settings |
| Workflow doesn't trigger on schedule | First scheduled run can take ~24 hrs | Just wait, or trigger manually first |

---

## 🎉 You Did It

You just set up **professional-grade automation** that most engineers don't have for their side projects. This is exactly the kind of stuff you can talk about in interviews:

> "I built a Python automation that syncs my LeetCode progress to a Notion dashboard via the Notion API and the LeetCode GraphQL API, deployed on GitHub Actions with a daily cron schedule."

That sentence alone is more impressive than a todo app. Mention it. Put the repo on your resume.

Now — go solve some problems. The grind is logging itself from here.
